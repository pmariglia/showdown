import constants
from collections import defaultdict
from copy import copy

from config import logger

import data
from data import all_move_json
from data import pokedex
from data.helpers import get_standard_battle_sets
from data.helpers import get_mega_pkmn_name

from showdown.engine.objects import State
from showdown.engine.objects import Side
from showdown.engine.objects import Pokemon as TransposePokemon

from showdown.helpers import get_pokemon_info_from_condition
from showdown.helpers import normalize_name
from showdown.helpers import calculate_stats
from data.helpers import get_all_possible_moves_for_random_battle
from data.helpers import get_most_likely_item_for_random_battle_pokemon
from data.helpers import get_most_likely_ability_for_random_battle
from data.helpers import get_all_possible_moves_for_standard_battle
from data.helpers import get_most_likely_item_for_standard_battle_pokemon
from data.helpers import get_most_likely_ability_for_standard_battle
from data.helpers import get_most_likely_spread_for_standard_battle


class Battle:

    def __init__(self, battle_tag):
        self.battle_tag = battle_tag
        self.user = Battler()
        self.opponent = Battler()
        self.weather = None
        self.field = None
        self.trick_room = False

        self.started = False
        self.rqid = None

        self.force_switch = False
        self.wait = False

        self.battle_type = None

        self.time_remaining = 240

    def initialize_team_preview(self, user_json, opponent_pokemon, battle_mode):
        self.user.from_json(user_json, first_turn=True)
        self.user.reserve.insert(0, self.user.active)
        self.user.active = None

        for pkmn_string in opponent_pokemon:
            pokemon = Pokemon.from_switch_string(pkmn_string)
            self.opponent.reserve.append(pokemon)

        smogon_usage_data = get_standard_battle_sets(battle_mode)
        data.standard_battle_sets = smogon_usage_data

        self.started = True
        self.rqid = user_json[constants.RQID]

    def start_random_battle(self, user_json, opponent_switch_string):
        self.user.from_json(user_json, first_turn=True)

        pkmn_information = opponent_switch_string.split('|')[3]
        pkmn = Pokemon.from_switch_string(pkmn_information)
        self.opponent.active = pkmn

        self.started = True
        self.rqid = user_json[constants.RQID]

    def prepare_random_battle(self):
        if not self.opponent.mega_revealed():
            check_in_sets = self.battle_type == constants.STANDARD_BATTLE
            self.opponent.active.try_convert_to_mega(check_in_sets=check_in_sets)

        self.opponent.active.guess_random_battle_attributes()
        for pkmn in filter(lambda x: x.is_alive(), self.opponent.reserve):
            pkmn.guess_random_battle_attributes()

    def prepare_standard_battle(self):
        if not self.opponent.mega_revealed():
            check_in_sets = self.battle_type == constants.STANDARD_BATTLE
            self.opponent.active.try_convert_to_mega(check_in_sets=check_in_sets)

        self.opponent.active.guess_standard_battle_attributes()
        for pkmn in filter(lambda x: x.is_alive(), self.opponent.reserve):
            pkmn.guess_standard_battle_attributes()

    def to_object(self):
        user_active = TransposePokemon.from_state_pokemon_dict(self.user.active.to_dict())
        user_reserve = dict()
        for mon in self.user.reserve:
            user_reserve[mon.name] = TransposePokemon.from_state_pokemon_dict(mon.to_dict())

        opponent_active = TransposePokemon.from_state_pokemon_dict(self.opponent.active.to_dict())
        opponent_reserve = dict()
        for mon in self.opponent.reserve:
            opponent_reserve[mon.name] = TransposePokemon.from_state_pokemon_dict(mon.to_dict())

        user = Side(user_active, user_reserve, copy(self.user.side_conditions), self.user.trapped)
        opponent = Side(opponent_active, opponent_reserve, copy(self.opponent.side_conditions), self.opponent.trapped)

        state = State(user, opponent, self.weather, self.field, self.trick_room, self.force_switch, self.wait)
        return state


class Battler:

    def __init__(self):
        self.active = None
        self.reserve = []
        self.side_conditions = defaultdict(lambda: 0)

        self.name = None
        self.trapped = False

        self.account_name = None

    def mega_revealed(self):
        return self.active.is_mega or any(p.is_mega for p in self.reserve)

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
            for stat, number in pkmn_dict[constants.STATS].items():
                pkmn.stats[constants.STAT_ABBREVIATION_LOOKUPS[stat]] = number

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


class Pokemon:

    def __init__(self, name: str, level: int):
        self.name = normalize_name(name)
        self.base_name = self.name
        self.level = level

        try:
            self.base_stats = pokedex[self.name][constants.BASESTATS]
        except KeyError:
            logger.info("Could not pokedex entry for {}".format(self.name))
            self.name = [k for k in pokedex if self.name.startswith(k)][0]
            logger.info("Using {} instead".format(self.name))
            self.base_stats = pokedex[self.name][constants.BASESTATS]

        self.stats = calculate_stats(self.base_stats, self.level)

        self.max_hp = self.stats.pop(constants.HITPOINTS)
        self.hp = self.max_hp
        if self.name == 'shedinja':
            self.max_hp = 1
            self.hp = 1

        self.ability = None
        self.types = pokedex[self.name][constants.TYPES]
        self.item = constants.UNKNOWN_ITEM

        self.fainted = False
        self.moves = []
        self.status = None
        self.volatile_statuses = []
        self.boosts = defaultdict(lambda: 0)
        self.can_mega_evo = False
        self.can_ultra_burst = True

        self.is_mega = False

    def forme_change(self, new_pkmn_name):
        hp_percent = float(self.hp) / self.max_hp
        moves = self.moves
        boosts = self.boosts
        status = self.status

        self.__init__(new_pkmn_name, self.level)
        self.hp = round(hp_percent * self.max_hp)
        self.moves = moves
        self.boosts = boosts
        self.status = status

    def try_convert_to_mega(self, check_in_sets=False):
        if self.item != constants.UNKNOWN_ITEM:
            return
        mega_pkmn_name = get_mega_pkmn_name(self.name)
        in_sets_data = mega_pkmn_name in data.standard_battle_sets

        if (mega_pkmn_name and check_in_sets and in_sets_data) or (mega_pkmn_name and not check_in_sets):
            logger.debug("Guessing mega-evolution: {}".format(mega_pkmn_name))
            self.forme_change(mega_pkmn_name)

    def is_alive(self):
        return self.hp > 0

    @classmethod
    def from_switch_string(cls, switch_string):
        details = switch_string.split(',')
        name = details[0]
        try:
            level = int(details[1].replace('L', '').strip())
        except (IndexError, ValueError):
            level = 100
        return Pokemon(name, level)

    def set_spread(self, nature, evs):
        evs = [int(e) for e in evs.split(',')]
        hp_percent = self.hp / self.max_hp
        self.stats = calculate_stats(self.base_stats, self.level, evs=evs, nature=nature)
        self.max_hp = self.stats.pop(constants.HITPOINTS)
        self.hp = self.max_hp * hp_percent

    def add_move(self, move_name: str):
        try:
            new_move = Move(move_name)
            self.moves.append(new_move)
            return new_move
        except KeyError:
            logger.warning("{} is not a known move".format(move_name))
            return None

    def get_move(self, move_name: str):
        for m in self.moves:
            if m.name == normalize_name(move_name):
                return m
        return None

    def update_moves_for_random_battles(self):
        if len(self.moves) == 4:
            logger.debug("{} revealed 4 moves: {}".format(self.name, self.moves))
            return
        additional_moves = get_all_possible_moves_for_random_battle(self.name, [m.name for m in self.moves])
        logger.debug("Guessing additional moves for {}: {}".format(self.name, additional_moves))
        for m in additional_moves:
            self.moves.append(Move(m))

    def update_ability_for_random_battles(self):
        if self.ability is not None:
            logger.debug("{} has revealed it's ability as {}, not guessing".format(self.name, self.ability))
            return
        ability = get_most_likely_ability_for_random_battle(self.name)
        logger.debug("Guessing ability={} for {}".format(ability, self.name))
        self.ability = ability

    def update_item_for_random_battles(self):
        if self.item != constants.UNKNOWN_ITEM:
            logger.debug("{} has revealed it's item as {}, not guessing".format(self.name, self.item))
            return
        item = get_most_likely_item_for_random_battle_pokemon(self.name)
        logger.debug("Guessing item={} for {}".format(item, self.name))
        self.item = item

    def update_moves_for_standard_battles(self):
        if len(self.moves) == 4:
            logger.debug("{} revealed 4 moves: {}".format(self.name, self.moves))
            return
        additional_moves = get_all_possible_moves_for_standard_battle(self.name, [m.name for m in self.moves])
        logger.debug("Guessing additional moves for {}: {}".format(self.name, additional_moves))
        for m in additional_moves:
            self.moves.append(Move(m))

    def update_ability_for_standard_battles(self):
        if self.ability is not None:
            logger.debug("{} has revealed it's ability as {}, not guessing".format(self.name, self.ability))
            return
        ability = get_most_likely_ability_for_standard_battle(self.name)
        logger.debug("Guessing ability={} for {}".format(ability, self.name))
        self.ability = ability

    def update_item_for_standard_battles(self):
        if self.item != constants.UNKNOWN_ITEM:
            logger.debug("{} has revealed it's item as {}, not guessing".format(self.name, self.item))
            return
        item = get_most_likely_item_for_standard_battle_pokemon(self.name)
        logger.debug("Guessing item={} for {}".format(item, self.name))
        self.item = item

    def update_spread_for_standard_battles(self):
        nature, evs = get_most_likely_spread_for_standard_battle(self.name)
        logger.debug("Spread assumption for {}: {}, {}".format(self.name, nature, evs))
        self.set_spread(nature, evs)

    def guess_random_battle_attributes(self):
        self.update_ability_for_random_battles()
        self.update_item_for_random_battles()
        self.update_moves_for_random_battles()

    def guess_standard_battle_attributes(self):
        self.update_ability_for_standard_battles()
        self.update_item_for_standard_battles()
        self.update_moves_for_standard_battles()
        self.update_spread_for_standard_battles()

    def to_dict(self):
        return {
            constants.FAINTED: self.fainted,
            constants.ID: self.name,
            constants.LEVEL: self.level,
            constants.HITPOINTS: self.hp,
            constants.MAXHP: self.max_hp,
            constants.ABILITY: self.ability,
            constants.ITEM: self.item,
            constants.BASESTATS: self.base_stats,
            constants.STATS: self.stats,
            constants.BOOSTS: self.boosts,
            constants.STATUS: self.status,
            constants.VOLATILE_STATUS: set(self.volatile_statuses),
            constants.MOVES: [m.to_dict() for m in self.moves],
            constants.TYPES: self.types,
            constants.CAN_MEGA_EVO: self.can_mega_evo
        }

    @classmethod
    def get_dummy(cls):
        p = Pokemon('pikachu', 100)
        p.hp = 0
        p.name = ''
        p.ability = None
        p.fainted = True
        return p

    def __eq__(self, other):
        return self.name == other.name and self.level == other.level

    def __repr__(self):
        return "{}, level {}".format(self.name, self.level)


class Move:
    def __init__(self, name):
        name = normalize_name(name)
        move_json = all_move_json[name]
        self.name = name
        self.max_pp = int(move_json.get(constants.PP) * 1.6)

        self.disabled = False
        self.can_z = False
        self.current_pp = self.max_pp

    def to_dict(self):
        return {
            "id": self.name,
            "disabled": self.disabled,
            "current_pp": self.current_pp
        }

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return "{}".format(self.name)
