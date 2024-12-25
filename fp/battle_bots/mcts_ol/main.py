import logging
from multiprocessing import Queue, Process
import multiprocessing
from queue import Empty
import time
import random
import threading
from fp.battle import Battle
from config import FoulPlayConfig
from contextlib import contextmanager
from .team_sampler import sample_opponent_teams
from pokey_engine import State
from ..helpers import prepare_battle
from ..poke_engine_helpers import battle_to_pokeystate
import signal
logger = logging.getLogger(__name__)

def logger_thread(queue):
    """Thread to receive log records from worker processes"""
    while True:
        try:
            record = queue.get()
            if record is None:  # Sentinel value to stop the thread
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)
        except Empty:
            continue
        except Exception as e:
            print(f"Error in logger thread: {e}")

def process_mcts(state_data, log_queue, result_queue):
    """Worker process function to run MCTS"""
    try:
        # Set up logging to queue for this process
        queue_handler = logging.handlers.QueueHandler(log_queue)
        logger = logging.getLogger(__name__)
        logger.handlers = []
        logger.addHandler(queue_handler)
        logger.setLevel(logging.INFO)
        
        serialized_state, likelihood, search_time = state_data
        
        # Recreate pokey_state from serialized data
        pokey_state = State()
        pokey_state.deserialize(serialized_state)
        
        logger.info("Searching for a move using MCTS...")
        policy, num_iterations = pokey_state.perform_mcts_search_st(search_time)
        
        logger.info(f"Iterations: {num_iterations}")
        logger.info(f"Policy: {policy}")
        
        # Send results back through the result queue
        result = {x[0]: x[1] * likelihood for x in policy}
        result_queue.put(result)
        
    except (KeyboardInterrupt, SystemExit):
        logger.info("MCTS process interrupted")
        raise
    except Exception as e:
        logger.error(f"Error in MCTS process: {e}")
        raise
    
@contextmanager
def process_cleanup_handler(processes, log_queue, logging_thread):
    """Context manager to ensure processes are cleaned up"""
    try:
        yield
    finally:
        # Terminate all processes
        for p in processes:
            if p.is_alive():
                p.terminate()
                p.join(timeout=1)
                if p.is_alive():
                    p.kill()

        # Clear the result queue
        while not log_queue.empty():
            try:
                log_queue.get_nowait()
            except Empty:
                break

        # Stop logging thread
        log_queue.put(None)
        if logging_thread and logging_thread.is_alive():
            logging_thread.join(timeout=1)

class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)
        self.num_team_map = {6: 2, 5: 4, 4: 8, 3: 16, 2: 16, 1:16, 0:16}
        try:
            multiprocessing.set_start_method('spawn', force=True)
        except RuntimeError:
            # If it's already been set, that's fine
            pass
    def find_best_move(self):
        if self.team_preview:
            self.user.active = self.user.reserve.pop(0)
            self.opponent.active = self.opponent.reserve.pop(0)

        try:
            known_counter = sum(1 for p in [self.opponent.active] + self.opponent.reserve if p)
            num_teams = self.num_team_map[known_counter]
            
            # Get multiple complete opponent teams
            sampled_battles = sample_opponent_teams(self, num_teams=num_teams)
            
            # Prepare battles and convert to pokey states
            prepared_states = []
            for battle, likelihood in sampled_battles:
                copied_battle = prepare_battle(battle, lambda x: None)
                pokey_state = battle_to_pokeystate(copied_battle)
                serialized_state = pokey_state.serialize()
                logger.info("Prepared team state: {}".format(serialized_state))
                prepared_states.append((serialized_state, likelihood))

            search_time_per_battle = round(FoulPlayConfig.search_time_ms / max(num_teams / 5.3, 1))
            state_data = [(state, likelihood, search_time_per_battle) 
                         for state, likelihood in prepared_states]
            
            start = time.time()
            log_queue = Queue()
            result_queue = Queue()
            logging_thread = threading.Thread(target=logger_thread, args=(log_queue,))
            logging_thread.daemon = True  # Make thread daemon so it dies with the main process
            logging_thread.start()

            processes = []
            results = []

            with process_cleanup_handler(processes, log_queue, logging_thread):
                # Start processes
                for battle_data in state_data:
                    p = Process(target=process_mcts, args=(battle_data, log_queue, result_queue))
                    p.daemon = True  # Make process daemon so it dies with the parent
                    processes.append(p)
                    p.start()

                # Wait for results with timeout
                timeout = FoulPlayConfig.search_time_ms / 1000 + 5  # Add 5 second buffer
                deadline = time.time() + timeout

                for p in processes:
                    remaining = max(0, deadline - time.time())
                    p.join(timeout=remaining)
                    if p.is_alive():
                        logger.warning(f"Process {p.pid} timed out")
                        continue

                    try:
                        result = result_queue.get_nowait()
                        results.append(result)
                    except Empty:
                        logger.error(f"Process {p.pid} finished but produced no result")

            if not results:
                logger.error("No results were produced by any process")
                # Return a fallback move if available
                return self._get_fallback_move()

            # Aggregate results
            move_names = results[0].keys()
            final_policy = []
            for move in move_names:
                final_policy.append(sum(policy[move] for policy in results))
            
            choices = sorted(list(zip(move_names, final_policy)), 
                           reverse=True, key=lambda x: x[1])
            
            logger.info(f"Final Policy: {choices}")
            best_choice = choices[0][0]
            
            logger.info(f"Final choice: {best_choice}")
            logger.info(f"Elapsed time: {time.time() - start}")

        except Exception as e:
            logger.error(f"Error in find_best_move: {e}")
            return self._get_fallback_move()
        finally:
            if self.team_preview:
                self.user.reserve.insert(0, self.user.active)
                self.user.active = None
                self.opponent.reserve.insert(0, self.opponent.active)
                self.opponent.active = None

        return best_choice

    def _get_fallback_move(self):
        """Return a fallback move in case of errors"""
        if self.team_preview:
            return "1"  # Default team preview choice
        
        # Get first available move
        if self.user.active and self.user.active.moves:
            return self.user.active.moves[0].name
        return None

# Add signal handlers at module level
def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}. Cleaning up...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)