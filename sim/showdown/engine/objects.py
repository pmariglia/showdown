from collections import defaultdict
from copy import copy

import sim.constants as constants
from sim.data import all_move_json
from sim.helpers import calculate_stats
from sim import pokedex



boost_multiplier_lookup = {
    -6: 2/8,
    -5: 2/7,
    -4: 2/6,
    -3: 2/5,
    -2: 2/4,
    -1: 2/3,
    0: 2/2,
    1: 3/2,
    2: 4/2,
    3: 5/2,
    4: 6/2,
    5: 7/2,
    6: 8/2
}


class State:
    __slots__ = ('user', 'opponent', 'weather', 'field', 'trick_room')

    def __init__(self, user, opponent, weather=None, field=None, trick_room=False):
        self.user = user
        self.opponent = opponent
        self.weather = weather
        self.field = field
        self.trick_room = trick_room

    def get_self_options(self, force_switch):
        forced_move = self.user.active.forced_move()
        if forced_move:
            return [forced_move]

        if force_switch:
            possible_moves = []
        else:
            possible_moves = [m[constants.ID] for m in self.user.active.moves if not m[constants.DISABLED]]

        if self.user.trapped(self.opponent.active):
            possible_switches = []
        else:
            possible_switches = self.user.get_switches()

        return possible_moves + possible_switches

    def get_opponent_options(self):
        forced_move = self.opponent.active.forced_move()
        if forced_move:
            return [forced_move]

        if self.opponent.active.hp <= 0:
            possible_moves = []
        else:
            possible_moves = [m[constants.ID] for m in self.opponent.active.moves if not m[constants.DISABLED]]

        if self.opponent.trapped(self.user.active):
            possible_switches = []
        else:
            possible_switches = self.opponent.get_switches()

        return possible_moves + possible_switches

    def get_all_options(self):
        force_switch = self.user.active.hp <= 0
        wait = self.opponent.active.hp <= 0

        # double faint or team preview
        if force_switch and wait:
            user_options = self.get_self_options(force_switch) or [constants.DO_NOTHING_MOVE]
            opponent_options = self.get_opponent_options() or [constants.DO_NOTHING_MOVE]
            return user_options, opponent_options

        if force_switch:
            opponent_options = [constants.DO_NOTHING_MOVE]
        else:
            opponent_options = self.get_opponent_options()

        if wait:
            user_options = [constants.DO_NOTHING_MOVE]
        else:
            user_options = self.get_self_options(force_switch)

        if not user_options:
            user_options = [constants.DO_NOTHING_MOVE]

        if not opponent_options:
            opponent_options = [constants.DO_NOTHING_MOVE]

        return user_options, opponent_options

    def battle_is_finished(self):
        # Returns:
        #    1 if the bot (self) has won
        #   -1 if the opponent has won
        #    False if the battle is not over

        if self.user.active.hp <= 0 and not any(pkmn.hp for pkmn in self.user.reserve.values()):
            return -1
        elif self.opponent.active.hp <= 0 and not any(pkmn.hp for pkmn in self.opponent.reserve.values()) and len(self.opponent.reserve) == 5:
            return 1

        return False

    @classmethod
    def from_dict(cls, state_dict):
        return State(
            Side.from_dict(state_dict[constants.USER]),
            Side.from_dict(state_dict[constants.OPPONENT]),
            state_dict[constants.WEATHER],
            state_dict[constants.FIELD],
            state_dict[constants.TRICK_ROOM]
        )

    def __repr__(self):
        return str(
            {
                constants.USER: self.user,
                constants.OPPONENT: self.opponent,
                constants.WEATHER: self.weather,
                constants.FIELD: self.field,
                constants.TRICK_ROOM: self.trick_room
            }
        )

    def __dict__(self):
        return {
                constants.USER: self.user,
                constants.OPPONENT: self.opponent,
                constants.WEATHER: self.weather,
                constants.FIELD: self.field,
                constants.TRICK_ROOM: self.trick_room
            }


class Side:
    __slots__ = ('active', 'reserve', 'wish', 'side_conditions', 'future_sight')

    def __init__(self, active, reserve, wish=(0,0), side_conditions=None, future_sight=(0,0)):
        self.active = active
        self.reserve = reserve
        self.wish = wish
        if side_conditions is None:
            self.side_conditions = defaultdict(int)
        else:
            self.side_conditions = defaultdict(int, side_conditions)
        self.future_sight = future_sight

    def get_switches(self):
        switches = []
        for pkmn_name, pkmn in self.reserve.items():
            if pkmn.hp > 0:
                switches.append("{} {}".format(constants.SWITCH_STRING, pkmn_name))
        return switches

    def trapped(self, opponent_active):
        if self.active.item == 'shedshell' or 'ghost' in self.active.types:
            return False
        elif constants.PARTIALLY_TRAPPED in self.active.volatile_status:
            return True
        elif opponent_active.ability == 'shadowtag':
            return True
        elif opponent_active.ability == 'magnetpull' and 'steel' in self.active.types:
            return True
        elif opponent_active.ability == 'arenatrap' and self.active.is_grounded():
            return True
        else:
            return False

    @classmethod
    def from_dict(cls, side_dict):
        return Side(
            Pokemon.from_dict(side_dict[constants.ACTIVE]),
            {p[constants.ID]: Pokemon.from_dict(p) for p in side_dict[constants.RESERVE].values()},
            side_dict[constants.WISH],
            defaultdict(int, side_dict[constants.SIDE_CONDITIONS]),
            side_dict[constants.FUTURE_SIGHT]
        )

    def __repr__(self):
        return str({
            constants.ACTIVE: self.active,
            constants.RESERVE: self.reserve,
            constants.WISH: self.wish,
            constants.SIDE_CONDITIONS: dict(self.side_conditions),
            constants.FUTURE_SIGHT: self.future_sight
        })


class Pokemon:
    __slots__ = (
        'id',
        'level',
        'types',
        'hp',
        'max_hp',
        'nature',
        'ability',
        'item',
        'stats',
        'nature',
        'evs',
        'ivs',
        'stat_boosts',
        'status',
        'volatile_status',
        'moves',
        'terastallized',
        'burn_multiplier'
    )

    def __init__(
        self,
        identifier,
        level,
        ability,
        item,
        nature="serious",
        evs=(85,) * 6,
        ivs=(31,) * 6,
        stat_boosts=None,
        status=None,
        terastallized=False,
        volatile_status=None,
        moves=None
    ):
        self.id = identifier
        self.level = level
        self.types = pokedex[self.id][constants.TYPES]
        self.ability = ability
        self.item = item
        base_stats = pokedex[self.id][constants.BASESTATS]
        self.ivs = tuple(ivs.values()) if isinstance(ivs, dict) else ivs
        self.evs = tuple(evs.values()) if isinstance(evs, dict) else evs
        self.stats = calculate_stats(base_stats, self.level, nature=nature, evs=self.evs, ivs=self.ivs)

        self.max_hp = self.stats.pop(constants.HITPOINTS)
        self.hp = self.max_hp
        if self.id == 'shedinja':
            self.hp = 1
            self.max_hp = 1
        self.nature = nature
        if stat_boosts is None:
            self.stat_boosts = {stat: 0 for stat in constants.STAT_STRINGS_ALL}
        else:
            self.stat_boosts = {stat: stat_boosts.get(stat, 0) for stat in constants.STAT_STRINGS_ALL}
        self.status = status
        self.terastallized = terastallized
        self.volatile_status = volatile_status or set()
        #assert 4 >= len(moves) > 0
        self.moves = [{'id': move, 'disabled': False, 'current_pp': int(1.6 * all_move_json[move]['pp'])} for move in moves]

        # evaluation relies on a multiplier for the burn status
        # it is calculated here to save time during evaluation
        self.burn_multiplier = self.calculate_burn_multiplier()

    # TODO: these properties should all be deprecated and future code should use dict access
    @property
    def maxhp(self):
        return self.max_hp

    @maxhp.setter
    def maxhp(self, value):
        self.max_hp = value

    @property
    def attack(self):
        return self.stats[constants.ATTACK]

    @attack.setter
    def attack(self, value):
        self.stats[constants.ATTACK] = value

    @property
    def defense(self):
        return self.stats[constants.DEFENSE]

    @defense.setter
    def defense(self, value):
        self.stats[constants.DEFENSE] = value

    @property
    def special_attack(self):
        return self.stats[constants.SPECIAL_ATTACK]

    @special_attack.setter
    def special_attack(self, value):
        self.stats[constants.SPECIAL_ATTACK] = value

    @property
    def special_defense(self):
        return self.stats[constants.SPECIAL_DEFENSE]

    @special_defense.setter
    def special_defense(self, value):
        self.stats[constants.SPECIAL_DEFENSE] = value

    @property
    def speed(self):
        return self.stats[constants.SPEED]

    @speed.setter
    def speed(self, value):
        self.stats[constants.SPEED] = value

    @property
    def attack_boost(self):
        return self.stat_boosts[constants.ATTACK]

    @attack_boost.setter
    def attack_boost(self, value):
        self.stat_boosts[constants.ATTACK] = value

    @property
    def defense_boost(self):
        return self.stat_boosts[constants.DEFENSE]

    @defense_boost.setter
    def defense_boost(self, value):
        self.stat_boosts[constants.DEFENSE] = value

    @property
    def special_attack_boost(self):
        return self.stat_boosts[constants.SPECIAL_ATTACK]

    @special_attack_boost.setter
    def special_attack_boost(self, value):
        self.stat_boosts[constants.SPECIAL_ATTACK] = value

    @property
    def special_defense_boost(self):
        return self.stat_boosts[constants.SPECIAL_DEFENSE]

    @special_defense_boost.setter
    def special_defense_boost(self, value):
        self.stat_boosts[constants.SPECIAL_DEFENSE] = value

    @property
    def speed_boost(self):
        return self.stat_boosts[constants.SPEED]

    @speed_boost.setter
    def speed_boost(self, value):
        self.stat_boosts[constants.SPEED] = value

    @property
    def accuracy_boost(self):
        return self.stat_boosts[constants.ACCURACY]

    @accuracy_boost.setter
    def accuracy_boost(self, value):
        self.stat_boosts[constants.ACCURACY] = value

    @property
    def evasion_boost(self):
        return self.stat_boosts[constants.EVASION]

    @evasion_boost.setter
    def evasion_boost(self, value):
        self.stat_boosts[constants.EVASION] = value

    def calculate_burn_multiplier(self):
        # this will result in a positive evaluation for a burned pokemon
        if self.ability in ['guts', 'marvelscale', 'quickfeet']:
            return -2

        # +1 to the multiplier for each physical move
        burn_multiplier = len([m for m in self.moves if all_move_json[m['id']][
            constants.CATEGORY] == constants.PHYSICAL])

        # evaluation could use more than 4 moves for opponent's pokemon - dont go over 4
        burn_multiplier = min(4, burn_multiplier)

        # dont make this as punishing for special attackers
        if self.special_attack > self.attack:
            burn_multiplier = int(burn_multiplier / 2)

        return burn_multiplier

    def get_highest_stat(self):
        return max(self.stats, key=lambda x: x[1])

    def get_boost_from_boost_string(self, boost_string):
        return self.stat_boosts.get(boost_string, 0)

    def forced_move(self):
        if "phantomforce" in self.volatile_status:
            return "phantomforce"
        elif "shadowforce" in self.volatile_status:
            return "shadowforce"
        elif "dive" in self.volatile_status:
            return "dive"
        elif "dig" in self.volatile_status:
            return "dig"
        elif "bounce" in self.volatile_status:
            return "bounce"
        elif "fly" in self.volatile_status:
            return "fly"
        else:
            return None

    def item_can_be_removed(self):
        return not (
            self.item is None or
            self.ability == 'stickyhold' or
            'substitute' in self.volatile_status or
            self.id in constants.POKEMON_CANNOT_HAVE_ITEMS_REMOVED or
            self.id.endswith('mega') and self.id != 'yanmega' or  # yeah this is hacky but who are you to judge?
            self.id.startswith("genesect") and self.item.endswith("drive") or
            self.id.startswith("arceus") and self.item.endswith("plate") or
            self.id.startswith("silvally") and self.item.endswith("memory") or
            # any(self.id.startswith(i) and self.id != i for i in constants.UNKOWN_POKEMON_FORMES) or
            self.item.endswith('iumz'))


    @classmethod
    def from_state_pokemon_dict(cls, d):
        return Pokemon(
            identifier=d[constants.ID],
            level=d[constants.LEVEL],
            ability=d[constants.ABILITY],
            item=d[constants.ITEM],
            nature=d[constants.NATURE],
            evs=d[constants.EVS],
            ivs=d.get(constants.IVS, (31,)*6),
            stat_boosts=d[constants.BOOSTS],
            status=d[constants.STATUS],
            terastallized=d[constants.TERASTALLIZED],
            volatile_status=d[constants.VOLATILE_STATUS],
            moves=d[constants.MOVES]
        )

    @classmethod
    def from_dict(cls, d):
        return Pokemon(
            identifier=d.get(constants.ID, False) or d[constants.NAME],
            level=d[constants.LEVEL],
            ability=d[constants.ABILITY],
            nature=d[constants.NATURE],
            evs=d[constants.EVS],
            ivs=d.get(constants.IVS, (31,) * 6),
            stat_boosts={stat: 0 for stat in constants.STAT_STRINGS_ALL},
            status=d.get(constants.STATUS, 0) or None,
            terastallized=d.get(constants.TERASTALLIZED, 0) or None,
            volatile_status=set(d.get(constants.VOLATILE_STATUS, set())),
            moves=d[constants.MOVES],
            item=d[constants.ITEM]
        )

    def calculate_boosted_stats(self):
        return {stat: boost_multiplier_lookup[self.stat_boosts[stat]] * self.stats[stat] for stat in constants.STAT_STRINGS}

    def is_grounded(self):
        if 'flying' in self.types or self.ability == 'levitate' or self.item == 'airballoon':
            return False
        return True

    # TODO: make this not ugly cause goddamn
    def __repr__(self):
        return str(
            {
                constants.ID: self.id,
                constants.LEVEL: self.level,
                constants.TYPES: self.types,
                constants.HITPOINTS: self.hp,
                constants.MAXHP: self.max_hp,
                constants.ABILITY: self.ability,
                constants.ITEM: self.item,
                constants.STAT_STRINGS: self.stats,
                constants.NATURE: self.nature,
                constants.EVS: self.evs,
                constants.STAT_BOOST_STRINGS_ALL: self.stat_boosts,
                constants.STATUS: self.status,
                constants.TERASTALLIZED: self.terastallized,
                constants.VOLATILE_STATUS: list(self.volatile_status),
                constants.MOVES: self.moves
            })


class TransposeInstruction:
    __slots__ = ('percentage', 'instructions', 'frozen')

    def __init__(self, percentage, instructions, frozen=False):
        self.percentage = percentage
        self.instructions = instructions
        self.frozen = frozen

    def update_percentage(self, modifier):
        self.percentage *= modifier

    def add_instruction(self, instruction):
        self.instructions.append(instruction)

    def has_same_instructions_as(self, other):
        return self.instructions == other.instructions

    def __copy__(self):
        return TransposeInstruction(self.percentage, copy(self.instructions), self.frozen)

    def __repr__(self):
        return "{}: {}".format(self.percentage, str(self.instructions))

    def __eq__(self, other):
        return self.percentage == other.percentage and \
            self.instructions == other.instructions and \
            self.frozen == other.frozen


class StateMutator:

    def __init__(self, state):
        self.state = state
        self.apply_instructions = {
            constants.MUTATOR_SWITCH: self.switch,
            constants.MUTATOR_APPLY_VOLATILE_STATUS: self.apply_volatile_status,
            constants.MUTATOR_REMOVE_VOLATILE_STATUS: self.remove_volatile_status,
            constants.MUTATOR_DAMAGE: self.damage,
            constants.MUTATOR_HEAL: self.heal,
            constants.MUTATOR_BOOST: self.boost,
            constants.MUTATOR_UNBOOST: self.unboost,
            constants.MUTATOR_APPLY_STATUS: self.apply_status,
            constants.MUTATOR_REMOVE_STATUS: self.remove_status,
            constants.MUTATOR_SIDE_START: self.side_start,
            constants.MUTATOR_SIDE_END: self.side_end,
            constants.MUTATOR_WISH_START: self.start_wish,
            constants.MUTATOR_WISH_DECREMENT: self.decrement_wish,
            constants.MUTATOR_FUTURESIGHT_START: self.start_futuresight,
            constants.MUTATOR_FUTURESIGHT_DECREMENT: self.decrement_futuresight,
            constants.MUTATOR_DISABLE_MOVE: self.disable_move,
            constants.MUTATOR_ENABLE_MOVE: self.enable_move,
            constants.MUTATOR_WEATHER_START: self.start_weather,
            constants.MUTATOR_FIELD_START: self.start_field,
            constants.MUTATOR_FIELD_END: self.end_field,
            constants.MUTATOR_TOGGLE_TRICKROOM: self.toggle_trickroom,
            constants.MUTATOR_CHANGE_TYPE: self.change_types,
            constants.MUTATOR_CHANGE_ITEM: self.change_item,
            constants.MUTATOR_CHANGE_STATS: self.change_stats
        }
        self.reverse_instructions = {
            constants.MUTATOR_SWITCH: self.reverse_switch,
            constants.MUTATOR_APPLY_VOLATILE_STATUS: self.remove_volatile_status,
            constants.MUTATOR_REMOVE_VOLATILE_STATUS: self.apply_volatile_status,
            constants.MUTATOR_DAMAGE: self.heal,
            constants.MUTATOR_HEAL: self.damage,
            constants.MUTATOR_BOOST: self.unboost,
            constants.MUTATOR_UNBOOST: self.boost,
            constants.MUTATOR_APPLY_STATUS: self.remove_status,
            constants.MUTATOR_REMOVE_STATUS: self.apply_status,
            constants.MUTATOR_SIDE_START: self.reverse_side_start,
            constants.MUTATOR_SIDE_END: self.reverse_side_end,
            constants.MUTATOR_WISH_START: self.reserve_start_wish,
            constants.MUTATOR_WISH_DECREMENT: self.reverse_decrement_wish,
            constants.MUTATOR_FUTURESIGHT_START: self.reverse_start_futuresight,
            constants.MUTATOR_FUTURESIGHT_DECREMENT: self.reverse_decrement_futuresight,
            constants.MUTATOR_DISABLE_MOVE: self.enable_move,
            constants.MUTATOR_ENABLE_MOVE: self.disable_move,
            constants.MUTATOR_WEATHER_START: self.reverse_start_weather,
            constants.MUTATOR_FIELD_START: self.reverse_start_field,
            constants.MUTATOR_FIELD_END: self.reverse_end_field,
            constants.MUTATOR_TOGGLE_TRICKROOM: self.toggle_trickroom,
            constants.MUTATOR_CHANGE_TYPE: self.reverse_change_types,
            constants.MUTATOR_CHANGE_ITEM: self.reverse_change_item,
            constants.MUTATOR_CHANGE_STATS: self.reverse_change_stats
        }

    def apply_one(self, instruction):
        method = self.apply_instructions[instruction[0]]
        method(*instruction[1:])

    def apply(self, instructions):
        for instruction in instructions:
            method = self.apply_instructions[instruction[0]]
            method(*instruction[1:])

    def reverse(self, instructions):
        for instruction in reversed(instructions):
            method = self.reverse_instructions[instruction[0]]
            method(*instruction[1:])

    def get_side(self, side):
        return getattr(self.state, side)

    def disable_move(self, side, move_name):
        side = self.get_side(side)
        try:
            move = next(filter(lambda x: x[constants.ID] == move_name, side.active.moves))
        except StopIteration:
            raise ValueError("{} not in pokemon's moves: {}".format(move_name, side.active.moves))

        move[constants.DISABLED] = True

    def enable_move(self, side, move_name):
        side = self.get_side(side)
        try:
            move = next(filter(lambda x: x[constants.ID] == move_name, side.active.moves))
        except StopIteration:
            raise ValueError("{} not in pokemon's moves: {}".format(move_name, side.active.moves))

        move[constants.DISABLED] = False

    def switch(self, side, _, switch_pokemon_name):
        # the second parameter to this function is the current active pokemon
        # this value must be here for reversing purposes
        side = self.get_side(side)

        side.reserve[side.active.id] = side.active
        side.active = side.reserve.pop(switch_pokemon_name)

    def reverse_switch(self, side, previous_active, current_active):
        self.switch(side, current_active, previous_active)

    def apply_volatile_status(self, side, volatile_status):
        side = self.get_side(side)
        side.active.volatile_status.add(volatile_status)

    def remove_volatile_status(self, side, volatile_status):
        side = self.get_side(side)
        side.active.volatile_status.remove(volatile_status)

    def damage(self, side, amount):
        side = self.get_side(side)
        side.active.hp -= amount

    def heal(self, side, amount):
        side = self.get_side(side)
        side.active.hp += amount

    def boost(self, side, stat, amount):
        side = self.get_side(side)
        side.active.stat_boosts[stat] += amount
        side.active.stat_boosts[stat] = max(-6, min(side.active.stat_boosts[stat], 6))

    def unboost(self, side, stat, amount):
        self.boost(side, stat, -1*amount)

    def apply_status(self, side, status):
        side = self.get_side(side)
        side.active.status = status

    def remove_status(self, side, _):
        # the second parameter of this function is the status being removed
        # this value must be here for reverse purposes
        self.apply_status(side, None)

    def side_start(self, side, effect, amount):
        side = self.get_side(side)
        side.side_conditions[effect] += amount

    def reverse_side_start(self, side, effect, amount):
        side = self.get_side(side)
        side.side_conditions[effect] -= amount

    def side_end(self, side, effect, amount):
        side = self.get_side(side)
        side.side_conditions[effect] -= amount

    def reverse_side_end(self, side, effect, amount):
        self.side_start(side, effect, amount)

    def start_futuresight(self, side, pkmn_name, _):
        # the second parameter is the current futuresight_amount
        # it is here for reversing purposes
        side = self.get_side(side)
        side.future_sight = (3, pkmn_name)

    def reverse_start_futuresight(self, side, _, old_pkmn_name):
        side = self.get_side(side)
        side.future_sight = (0, old_pkmn_name)

    def decrement_futuresight(self, side):
        side = self.get_side(side)
        side.future_sight = (side.future_sight[0] - 1, side.future_sight[1])

    def reverse_decrement_futuresight(self, side):
        side = self.get_side(side)
        side.future_sight = (side.future_sight[0] + 1, side.future_sight[1])

    def start_wish(self, side, health, _):
        # the third parameter is the current wish amount
        # it is here for reversing purposes
        side = self.get_side(side)
        side.wish = (2, health)

    def reserve_start_wish(self, side, _, previous_wish_amount):
        side = self.get_side(side)
        side.wish = (0, previous_wish_amount)

    def decrement_wish(self, side):
        side = self.get_side(side)
        side.wish = (side.wish[0] - 1, side.wish[1])

    def reverse_decrement_wish(self, side):
        side = self.get_side(side)
        side.wish = (side.wish[0] + 1, side.wish[1])

    def start_weather(self, weather, _):
        # the second parameter is the current weather
        # the value is here for reversing purposes
        self.state.weather = weather

    def reverse_start_weather(self, _, old_weather):
        self.state.weather = old_weather

    def start_field(self, field, _):
        # the second parameter is the current field
        # the value is here for reversing purposes
        self.state.field = field

    def reverse_start_field(self, _, old_field):
        self.state.field = old_field

    def end_field(self, _):
        # the second parameter is the current field
        # the value is here for reversing purposes
        self.state.field = None

    def reverse_end_field(self, old_field):
        self.state.field = old_field

    def toggle_trickroom(self):
        self.state.trick_room ^= True

    def change_types(self, side, new_types, _):
        # the third parameter is the current types of the active pokemon
        # they must be here for reversing purposes
        side = self.get_side(side)
        side.active.types = new_types

    def reverse_change_types(self, side, _, old_types):
        side = self.get_side(side)
        side.active.types = old_types

    def change_item(self, side, new_item, _):
        # the third parameter is the current item
        # it must be here for reversing purposes
        side = self.get_side(side)
        side.active.item = new_item

    def reverse_change_item(self, side, _, old_item):
        side = self.get_side(side)
        side.active.item = old_item

    def change_stats(self, side, new_stats, _):
        # the third parameter is the old stats
        # is must be here for reversing purposes
        side = self.get_side(side)
        side.active.max_hp = new_stats[0]
        side.active.stats = new_stats[1:]
    def reverse_change_stats(self, side, _, old_stats):
        # the second parameter are the new stats
        side = self.get_side(side)
        side.active.maxhp = old_stats[0]
        side.active.stats = old_stats[1:]
