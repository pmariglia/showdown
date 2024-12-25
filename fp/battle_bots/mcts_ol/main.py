import logging
from multiprocessing import Queue, Process
from queue import Empty
import time
import random
import threading
from fp.battle import Battle
from config import FoulPlayConfig
from .team_sampler import sample_opponent_teams
from pokey_engine import State
from ..helpers import prepare_battle
from ..poke_engine_helpers import battle_to_pokeystate

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
    # Set up logging to queue for this process
    queue_handler = logging.handlers.QueueHandler(log_queue)
    logger = logging.getLogger(__name__)
    logger.handlers = []
    logger.addHandler(queue_handler)
    logger.setLevel(logging.INFO)
    
    serialized_state, likelihood, search_time = state_data
    try:
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
        
    except Exception as e:
        logger.error(f"Error in MCTS process: {e}")
        raise

class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)
        self.num_team_map = {6: 2, 5: 4, 4: 8, 3: 16, 2: 16, 1:16, 0:16}

    def find_best_move(self):
        if self.team_preview:
            self.user.active = self.user.reserve.pop(0)
            self.opponent.active = self.opponent.reserve.pop(0)
        known_counter = 0
        if self.opponent.active:
            known_counter += 1
        for p in self.opponent.reserve:
            if p:
                known_counter += 1
        num_teams = self.num_team_map[known_counter]
        # Get multiple complete opponent teams
        sampled_battles = sample_opponent_teams(self, num_teams=num_teams)
        
        # Prepare battles and convert to pokey states
        prepared_states = []
        for battle, likelihood in sampled_battles:
            # Copy battle and lock moves without predicting sets
            copied_battle = prepare_battle(battle, lambda x: None)
            
            # Convert to pokey state and serialize
            pokey_state = battle_to_pokeystate(copied_battle)
            serialized_state = pokey_state.serialize()
            logger.info("Prepared team state: {}".format(serialized_state))
            
            prepared_states.append((serialized_state, likelihood))

        # Prepare data for parallel processing
        search_time_per_battle = round(FoulPlayConfig.search_time_ms / max(num_teams / 5.3, 1))
        state_data = [(state, likelihood, search_time_per_battle) 
                     for state, likelihood in prepared_states]
        start = time.time()
        # Set up logging queue and thread
        log_queue = Queue()
        result_queue = Queue()
        logging_thread = threading.Thread(target=logger_thread, args=(log_queue,))
        logging_thread.start()

        # Run MCTS processes
        processes = []
        for battle_data in state_data:
            p = Process(target=process_mcts, args=(battle_data, log_queue, result_queue))
            processes.append(p)
            p.start()

        # Wait for all processes to complete and collect results
        results = []
        for p in processes:
            p.join()
            try:
                result = result_queue.get_nowait()
                results.append(result)
            except Empty:
                logger.error(f"Process {p.pid} finished but produced no result")

        # Signal logging thread to finish
        log_queue.put(None)
        logging_thread.join()
        
        
        if not results:
            logger.error("No results were produced by any process")
            return None

        # Aggregate choices from all parallel MCTS runs
        move_names = results[0].keys()
        final_policy = []
        for move in move_names:
            final_policy.append(sum(policy[move] for policy in results))
        
        choices = sorted(list(zip(move_names, final_policy)), reverse=True, key= lambda x: x[1])
        
        logger.info(f"Final Policy: {choices}")
        best_choice = choices[0][0]
        # if self.turn >= 10:
        #     best_choice = choices[0][0]
        # else:
        #     best_choice = list(move_names)[random.choices(
        #         range(len(final_policy)), 
        #         weights=final_policy, 
        #         k=1
        #     )[0]]
        
        logger.info(f"Final choice: {best_choice}")
        logger.info(f"Elapsed time: {time.time() - start}")

        if self.team_preview:
            self.user.reserve.insert(0, self.user.active)
            self.user.active = None
            self.opponent.reserve.insert(0, self.opponent.active)
            self.opponent.active = None

        return best_choice