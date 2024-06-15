import constants
import random
from showdown.battle import Battle

from ..helpers import format_decision


class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)

    def find_best_move(self):
        state = self.create_state()
        my_options = self.get_all_options()[0]

        moves = []
        switches = []

        print(my_options)
        for option in my_options:
            if option.startswith(constants.SWITCH_STRING + " "):
                switches.append(option)
            else:
                moves.append(option)

        if self.force_switch or not moves:
            return format_decision(self, switches[0])

        return format_decision(self, moves[random.randint(0, len(moves) - 1)])

