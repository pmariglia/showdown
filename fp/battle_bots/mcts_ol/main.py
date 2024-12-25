import logging
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from queue import Empty
import time
from fp.battle import Battle
from config import FoulPlayConfig
from .team_sampler import sample_opponent_teams
from pokey_engine import State
from ..helpers import prepare_battle
from ..poke_engine_helpers import battle_to_pokeystate
logger = logging.getLogger(__name__)

def process_mcts_simplified(state_data):
    """Simplified worker function"""
    serialized_state, likelihood, search_time = state_data
    try:
        # Recreate pokey_state from serialized data
        pokey_state = State()
        pokey_state.deserialize(serialized_state)
        
        policy, num_iterations = pokey_state.perform_mcts_search_st(search_time)
        logger.info(f"Iterations: {num_iterations}")
        logger.info(f"Policy: {policy}")
        
        return {x[0]: x[1] * likelihood for x in policy}
        
    except Exception as e:
        logger.error(f"Error in MCTS process: {e}")
        return {}
    
class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)
        self.num_team_map = {6: 2, 5: 4, 4: 8, 3: 16, 2: 16, 1:16, 0:16}

    def find_best_move(self):
        if self.team_preview:
            self.user.active = self.user.reserve.pop(0)
            self.opponent.active = self.opponent.reserve.pop(0)

        try:
            # Prepare data as before
            known_counter = sum(1 for p in [self.opponent.active] + self.opponent.reserve if p)
            num_teams = self.num_team_map[known_counter]
            
            sampled_battles = sample_opponent_teams(self, num_teams=num_teams)
            prepared_states = []
            for battle, likelihood in sampled_battles:
                copied_battle = prepare_battle(battle, lambda x: None)
                pokey_state = battle_to_pokeystate(copied_battle)
                serialized_state = pokey_state.serialize()
                prepared_states.append((serialized_state, likelihood))

            search_time_per_battle = round(FoulPlayConfig.search_time_ms / max(num_teams / 5.3, 1))
            state_data = [(state, likelihood, search_time_per_battle) 
                         for state, likelihood in prepared_states]
            
            start = time.time()
            results = []
            
            # Use ProcessPoolExecutor to manage processes
            with ProcessPoolExecutor(max_workers=len(state_data)) as executor:
                future_to_data = {
                    executor.submit(process_mcts_simplified, data): data 
                    for data in state_data
                }
                
                timeout = search_time_per_battle/1000 + 5  # Convert to seconds and add buffer
                completed_futures = []
                
                # Collect results as they complete
                for future in future_to_data:
                    try:
                        result = future.result(timeout=timeout)
                        if result:  # Only add non-empty results
                            results.append(result)
                    except TimeoutError:
                        logger.warning("MCTS process timed out")
                    except Exception as e:
                        logger.error(f"MCTS process failed: {e}")

            if not results:
                logger.error("No valid results produced")
                return self._get_fallback_move()

            # Process results as before
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

            return best_choice

        except Exception as e:
            logger.error(f"Error in find_best_move: {e}")
            return self._get_fallback_move()

        finally:
            if self.team_preview:
                self.user.reserve.insert(0, self.user.active)
                self.user.active = None
                self.opponent.reserve.insert(0, self.opponent.active)
                self.opponent.active = None

    def _get_fallback_move(self):
        if self.team_preview:
            return "1"
        if self.user.active and hasattr(self.user.active, 'moves') and self.user.active.moves:
            return self.user.active.moves[0].name
        return None