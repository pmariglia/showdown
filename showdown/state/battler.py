from copy import copy
from collections import defaultdict
import constants
from showdown.helpers import get_pokemon_info_from_condition
from showdown.state.pokemon import Pokemon


class Battler:

    def __init__(self):
        self.active = None
        self.reserve = []
        self.side_conditions = defaultdict(lambda: 0)

        self.name = None
        self.trapped = False

        self.account_name = None

    def from_json(self, user_json, first_turn=False):
        if first_turn:
            existing_conditions = (None, None, None)
        else:
            existing_conditions = (self.active.name, self.active.boosts, self.active.volatile_statuses)

        try:
            trapped = user_json[constants.ACTIVE][0].get(constants.TRAPPED, False)
            maybe_trapped = user_json[constants.ACTIVE][0].get(constants.MAYBE_TRAPPED, False)
            self.trapped = trapped or maybe_trapped
        except KeyError:
            self.trapped = False

        try:
            can_mega_evo = user_json[constants.ACTIVE][0][constants.CAN_MEGA_EVO]
        except KeyError:
            can_mega_evo = False

        try:
            can_ultra_burst = user_json[constants.ACTIVE][0][constants.CAN_ULTRA_BURST]
        except KeyError:
            can_ultra_burst = False

        try:
            can_z_move = []
            for m in user_json[constants.ACTIVE][0][constants.CAN_Z_MOVE]:
                if m is not None:
                    can_z_move.append(True)
                else:
                    can_z_move.append(False)
        except KeyError:
            can_z_move = [False, False, False, False]

        self.name = user_json[constants.SIDE][constants.ID]
        self.reserve.clear()
        for index, pkmn_dict in enumerate(user_json[constants.SIDE][constants.POKEMON]):

            pkmn = Pokemon.from_switch_string(pkmn_dict[constants.DETAILS])
            pkmn.ability = pkmn_dict[constants.REQUEST_DICT_ABILITY]
            pkmn.index = index + 1
            pkmn.hp, pkmn.max_hp, pkmn.status = get_pokemon_info_from_condition(pkmn_dict[constants.CONDITION])
            pkmn.item = pkmn_dict[constants.ITEM] if pkmn_dict[constants.ITEM] else None

            if pkmn_dict[constants.ACTIVE]:
                self.active = pkmn
                if existing_conditions[0] == pkmn.name:
                    pkmn.boosts = existing_conditions[1]
                    pkmn.volatile_statuses = existing_conditions[2]
            else:
                self.reserve.append(pkmn)

            for move_name in pkmn_dict[constants.MOVES]:
                if move_name.startswith(constants.HIDDEN_POWER):
                    pkmn.add_move('{}{}'.format(
                        move_name,
                        constants.HIDDEN_POWER_RESERVE_MOVE_BASE_DAMAGE_STRING
                        )
                    )
                else:
                    pkmn.add_move(move_name)

        # if there is no active pokemon, we do not want to look through it's moves
        if constants.ACTIVE not in user_json:
            return

        self.active.can_mega_evo = can_mega_evo
        self.active.can_ultra_burst = can_ultra_burst

        # clear the active moves so they can be reset by the options available
        self.active.moves.clear()

        # update the active pokemon's moves to show disabled status/pp remaining
        # this assumes that there is only one active pokemon (single-battle)
        for index, move in enumerate(user_json[constants.ACTIVE][0][constants.MOVES]):
            if move[constants.ID] == constants.HIDDEN_POWER:
                self.active.add_move('{}{}{}'.format(
                        constants.HIDDEN_POWER,
                        move['move'].split()[constants.HIDDEN_POWER_TYPE_STRING_INDEX].lower(),
                        constants.HIDDEN_POWER_ACTIVE_MOVE_BASE_DAMAGE_STRING
                    )
                )
            else:
                self.active.add_move(move[constants.ID])
            self.active.moves[-1].disabled = move.get(constants.DISABLED, False)
            self.active.moves[-1].current_pp = move.get(constants.PP, 1)
            if can_z_move[index]:
                self.active.moves[index].can_z = True

    def to_dict(self):
        return {
            constants.TRAPPED: self.trapped,
            constants.ACTIVE: self.active.to_dict(),
            constants.RESERVE: [p.to_dict() for p in self.reserve],
            constants.SIDE_CONDITIONS: copy(self.side_conditions)
        }
