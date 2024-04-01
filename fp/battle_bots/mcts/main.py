import logging

import constants
from fp.battle import Battle
from config import FoulPlayConfig

from ..helpers import (
    fill_in_standardbattle_unknowns,
    fill_in_randombattle_unknowns,
    prepare_battle,
    fill_in_battle_factory_unknowns,
)
from ..poke_engine_helpers import (
    get_payoff_matrix_from_mcts,
    battle_to_poke_engine_state,
)

logger = logging.getLogger(__name__)


class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)

    def find_best_move(self):
        if self.team_preview:
            self.user.active = self.user.reserve.pop(0)
            self.opponent.active = self.opponent.reserve.pop(0)

        if self.battle_type == constants.RANDOM_BATTLE:
            fn = fill_in_randombattle_unknowns
        elif self.battle_type == constants.BATTLE_FACTORY:
            fn = fill_in_battle_factory_unknowns
        else:
            fn = fill_in_standardbattle_unknowns

        battle = prepare_battle(self, fn)

        logger.info("Searching for a move using MCTS...")
        choice, win_percentage, num_iterations = get_payoff_matrix_from_mcts(
            battle_to_poke_engine_state(battle), FoulPlayConfig.search_time_ms
        )
        logger.info("Choice: {}, {}".format(choice, win_percentage))
        logger.info("Iterations: {}".format(num_iterations))

        if self.team_preview:
            self.user.reserve.insert(0, self.user.active)
            self.user.active = None
            self.opponent.reserve.insert(0, self.opponent.active)
            self.opponent.active = None

        return choice
