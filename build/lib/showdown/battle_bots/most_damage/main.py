import constants
from data import all_move_json
from showdown.battle import Battle
from showdown.engine.damage_calculator import calculate_damage
from showdown.engine.find_state_instructions import update_attacking_move
from ..helpers import format_decision


class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)

    def find_best_move(self):
        state = self.create_state()
        my_options = self.get_all_options()[0]

        moves = []
        switches = []
        for option in my_options:
            if option.startswith(constants.SWITCH_STRING + " "):
                switches.append(option)
            else:
                moves.append(option)

        if self.force_switch or not moves:
            return format_decision(self, switches[0])

        most_damage = -1
        choice = None
        for move in moves:
            damage_amounts = calculate_damage(state, constants.USER, move, constants.DO_NOTHING_MOVE)

            damage = damage_amounts[0] if damage_amounts else 0

            if damage > most_damage:
                choice = move
                most_damage = damage

        return format_decision(self, choice)
