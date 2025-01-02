import logging
from concurrent.futures import ProcessPoolExecutor

from poke_engine import MctsResult

from fp.battle import Battle
from config import FoulPlayConfig

from .team_sampler import (
    prepare_random_battles,
    fill_in_opponent_unrevealed_pkmn,
)

from poke_engine import (
    State as PokeEngineState,
    monte_carlo_tree_search,
)

from ..poke_engine_helpers import battle_to_poke_engine_state

logger = logging.getLogger(__name__)

# number of revealed pokemon -> number of teams to sample
NUM_TEAM_MAP = {6: 2, 5: 4, 4: 8, 3: 16, 2: 16, 1: 16}


def select_move_from_mcts_results(mcts_results: list[(MctsResult, float, int)]) -> str:
    final_policy = {}
    for mcts_result, sample_chance, index in mcts_results:
        this_policy = max(mcts_result.side_one, key=lambda x: x.visits)
        logger.info(
            "Policy {}: {} visited {}% avg_score={} sample_chance_multiplier={}".format(
                index,
                this_policy.move_choice,
                round(100 * this_policy.visits / mcts_result.total_visits, 2),
                this_policy.total_score / this_policy.visits,
                round(sample_chance, 3),
            )
        )
        for s1_option in mcts_result.side_one:
            final_policy[s1_option.move_choice] = final_policy.get(
                s1_option.move_choice, 0
            ) + (sample_chance * (s1_option.visits / mcts_result.total_visits))

    final_policy = sorted(final_policy.items(), key=lambda x: x[1], reverse=True)
    logger.info("Final policy: {}".format(final_policy))
    return final_policy[0][0]


def get_result_from_mcts(
    poke_engine_state: PokeEngineState, search_time_ms: int, index: int
) -> MctsResult:
    state_string = poke_engine_state.to_string()
    logger.debug("Calling with {} state: {}".format(index, state_string))

    res = monte_carlo_tree_search(poke_engine_state, search_time_ms)
    logger.info("Iterations {}: {}".format(index, res.total_visits))
    return res


class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)

    def find_best_move(self):
        if self.team_preview:
            self.user.active = self.user.reserve.pop(0)
            self.opponent.active = self.opponent.reserve.pop(0)

        revealed_pkmn = len(self.opponent.reserve)
        if self.opponent.active is not None:
            revealed_pkmn += 1

        num_battles = max(NUM_TEAM_MAP[revealed_pkmn], FoulPlayConfig.parallelism)
        battles = prepare_random_battles(self, num_battles)
        for b, _ in battles:
            fill_in_opponent_unrevealed_pkmn(b)

        logger.info("Searching for a move using MCTS...")
        search_time_per_battle = FoulPlayConfig.search_time_ms // (
            max(num_battles // FoulPlayConfig.parallelism, 1)
        )
        with ProcessPoolExecutor(max_workers=FoulPlayConfig.parallelism) as executor:
            futures = []
            for index, (b, chance) in enumerate(battles):
                fut = executor.submit(
                    get_result_from_mcts,
                    battle_to_poke_engine_state(b),
                    search_time_per_battle,
                    index,
                )
                futures.append((fut, chance, index))

        mcts_results = [
            (fut.result(), chance, index) for (fut, chance, index) in futures
        ]
        choice = select_move_from_mcts_results(mcts_results)
        logger.info("Choice: {}".format(choice))

        if self.team_preview:
            self.user.reserve.insert(0, self.user.active)
            self.user.active = None
            self.opponent.reserve.insert(0, self.opponent.active)
            self.opponent.active = None

        return choice
