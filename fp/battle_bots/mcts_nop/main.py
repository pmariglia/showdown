
from concurrent.futures import ProcessPoolExecutor
import logging, os, time
from fp.battle import Battle
from config import FoulPlayConfig
from .team_sampler import sample_opponent_teams
from ..helpers import prepare_battle
from ..poke_engine_helpers import (
    get_mcts_policy,
    battle_to_poke_engine_state,
)
from poke_engine import (
    state_from_string
)
from poke_engine import (
    state_from_string
)
from ..poke_engine_helpers import (
    get_mcts_policy,
    battle_to_poke_engine_state,
)

# Basic logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_mcts_task(state_data):
    """Worker function for MCTS processing"""
    serialized_state, likelihood, search_time = state_data
    
    try:
        poke_state = state_from_string(serialized_state)
        policy, num_iterations = get_mcts_policy(poke_state, search_time)
        return {x[0]: x[1] * likelihood for x in policy}
    except Exception as e:
        logger.error(f"Error in MCTS process: {e}")
        raise

class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)
        self.num_team_map = {6: 2, 5: 4, 4: 8, 3: 16, 2: 16, 1:16, 0:16}
        
    def find_best_move(self):
        logger.info("Starting find_best_move.")
        if self.team_preview:
            self.user.active = self.user.reserve.pop(0)
            self.opponent.active = self.opponent.reserve.pop(0)

        try:
            known_counter = sum(1 for p in [self.opponent.active] + self.opponent.reserve if p)
            num_teams = self.num_team_map[known_counter]
            
            if os.environ.get('CPUS_PER_BOT'):
                cpus = float(os.environ.get('CPUS_PER_BOT'))
                num_teams = min(num_teams, max(2, int(cpus * 2)))
                logger.info(f"Limiting to {num_teams} teams based on {cpus} CPUs")
            else:
                cpus = 4

            sampled_battles = sample_opponent_teams(self, num_teams=num_teams)

            # Prepare states
            prepared_states = []
            for battle, likelihood in sampled_battles:
                copied_battle = prepare_battle(battle, lambda x: None)
                poke_engine_state = battle_to_poke_engine_state(copied_battle)
                serialized_state = poke_engine_state.to_string()
                prepared_states.append((serialized_state, likelihood))

            search_time_per_battle = round(FoulPlayConfig.search_time_ms / max(num_teams / cpus, 1))
            state_data = [(state, likelihood, search_time_per_battle)
                         for state, likelihood in prepared_states]

            start = time.time()
            results = []
            
            # Use ProcessPoolExecutor instead of manual process management
            with ProcessPoolExecutor(max_workers=cpus) as executor:
                future_to_state = {executor.submit(process_mcts_task, data): data 
                                 for data in state_data}
                
                # Wait for all futures to complete with timeout
                timeout = FoulPlayConfig.search_time_ms / 1000 + 5
                remaining_time = timeout
                
                for future in future_to_state:
                    try:
                        result = future.result(timeout=remaining_time)
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Task failed: {e}")
                    
                    remaining_time = timeout - (time.time() - start)
                    if remaining_time <= 0:
                        break

            if not results:
                logger.error("No results were produced")
                return self._get_fallback_move()

            # Aggregate results
            move_names = results[0].keys()
            final_policy = []
            for move in move_names:
                final_policy.append(sum(policy.get(move, 0) for policy in results))

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

        if self.user.active and self.user.active.moves:
            return self.user.active.moves[0].name
        return None