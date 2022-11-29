from copy import copy
from copy import deepcopy

import constants
from data import all_move_json


pokemon_type_indicies = {
    'normal': 0,
    'fire': 1,
    'water': 2,
    'electric': 3,
    'grass': 4,
    'ice': 5,
    'fighting': 6,
    'poison': 7,
    'ground': 8,
    'flying': 9,
    'psychic': 10,
    'bug': 11,
    'rock': 12,
    'ghost': 13,
    'dragon': 14,
    'dark': 15,
    'steel': 16,
    'fairy': 17,

    # ??? and typeless are the same thing
    'typeless': 18,
    '???': 18,
}

damage_multipication_array = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1/2, 0, 1, 1, 1/2, 1, 1],
                              [1, 1/2, 1/2, 1, 2, 2, 1, 1, 1, 1, 1, 2, 1/2, 1, 1/2, 1, 2, 1, 1],
                              [1, 2, 1/2, 1, 1/2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1/2, 1, 1, 1, 1],
                              [1, 1, 2, 1/2, 1/2, 1, 1, 1, 0, 2, 1, 1, 1, 1, 1/2, 1, 1, 1, 1],
                              [1, 1/2, 2, 1, 1/2, 1, 1, 1/2, 2, 1/2, 1, 1/2, 2, 1, 1/2, 1, 1/2, 1, 1],
                              [1, 1/2, 1/2, 1, 2, 1/2, 1, 1, 2, 2, 1, 1, 1, 1, 2, 1, 1/2, 1, 1],
                              [2, 1, 1, 1, 1, 2, 1, 1/2, 1, 1/2, 1/2, 1/2, 2, 0, 1, 2, 2, 1/2, 1],
                              [1, 1, 1, 1, 2, 1, 1, 1/2, 1/2, 1, 1, 1, 1/2, 1/2, 1, 1, 0, 2, 1],
                              [1, 2, 1, 2, 1/2, 1, 1, 2, 1, 0, 1, 1/2, 2, 1, 1, 1, 2, 1, 1],
                              [1, 1, 1, 1/2, 2, 1, 2, 1, 1, 1, 1, 2, 1/2, 1, 1, 1, 1/2, 1, 1],
                              [1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1/2, 1, 1, 1, 1, 0, 1/2, 1, 1],
                              [1, 1/2, 1, 1, 2, 1, 1/2, 1/2, 1, 1/2, 2, 1, 1, 1/2, 1, 2, 1/2, 1/2, 1],
                              [1, 2, 1, 1, 1, 2, 1/2, 1, 1/2, 2, 1, 2, 1, 1, 1, 1, 1/2, 1, 1],
                              [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1/2, 1, 1, 1],
                              [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1/2, 0, 1],
                              [1, 1, 1, 1, 1, 1, 1/2, 1, 1, 1, 2, 1, 1, 2, 1, 1/2, 1, 1/2, 1],
                              [1, 1/2, 1/2, 1/2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1/2, 2, 1],
                              [1, 1/2, 1, 1, 1, 1, 2, 1/2, 1, 1, 1, 1, 1, 1, 2, 2, 1/2, 1, 1],
                              [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]


SPECIAL_LOGIC_MOVES = {
    "seismictoss": lambda attacker, defender: [int(attacker.level)] if "ghost" not in defender.types else None,
    "nightshade": lambda attacker, defender: [int(attacker.level)] if "normal" not in defender.types else None,
    "superfang": lambda attacker, defender: [int(defender.hp / 2)] if "ghost" not in defender.types else None,
    "naturesmadness": lambda attacker, defender: [int(defender.hp / 2)],
    "finalgambit": lambda attacker, defender: [int(attacker.hp)] if "ghost" not in defender.types else None,
    "endeavor": lambda attacker, defender: [int(defender.hp - attacker.hp)] if defender.hp > attacker.hp and "ghost" not in defender.types else None,
    "painsplit": lambda attacker, defender: [defender.hp - (attacker.hp + defender.hp)/2],
}


TERRAIN_DAMAGE_BOOST = 1.3


def _calculate_damage(attacker, defender, move, conditions=None, calc_type='average'):
    # This function assumes the `move` dictionary has already been updated to account for move/item/ability special-effects
    # You may want to use `calculate_damage`

    acceptable_calc_types = ['average', 'min', 'max', 'min_max', 'min_max_average', 'all']
    if calc_type not in acceptable_calc_types:
        raise ValueError("{} is not one of {}".format(calc_type, acceptable_calc_types))

    attacking_move = get_move(move)
    if attacking_move is None:
        raise TypeError("Invalid move: {}".format(move))

    attacking_type = attacking_move.get(constants.CATEGORY)
    if attacking_type == constants.PHYSICAL:
        attack = constants.ATTACK
        defense = constants.DEFENSE
    elif attacking_type == constants.SPECIAL:
        attack = constants.SPECIAL_ATTACK
        defense = constants.SPECIAL_DEFENSE
    else:
        return None

    try:
        return SPECIAL_LOGIC_MOVES[attacking_move[constants.ID]](attacker, defender)
    except KeyError:
        pass

    if attacking_move[constants.BASE_POWER] == 0:
        return [0]

    if conditions is None:
        conditions = {}

    attacking_stats = attacker.calculate_boosted_stats()
    defending_stats = defender.calculate_boosted_stats()

    if attacker.ability == 'unaware':
        if defense == constants.DEFENSE:
            defending_stats[defense] = defender.defense
        elif defense == constants.SPECIAL_DEFENSE:
            defending_stats[defense] = defender.special_defense
    if defender.ability == 'unaware':
        if attack == constants.ATTACK:
            attacking_stats[attack] = attacker.attack
        elif defense == constants.SPECIAL_ATTACK:
            attacking_stats[attack] = attacker.special_attack

    defending_types = defender.types
    if attacking_move[constants.ID] == 'thousandarrows' and 'flying' in defending_types:
        defending_types = copy(defender.types)
        defending_types.remove('flying')
    if attacking_move[constants.TYPE] == 'ground' and constants.ROOST in defender.volatile_status:
        defending_types = copy(defender.types)
        try:
            defending_types.remove('flying')
        except ValueError:
            pass

    # rock types get 1.5x SPDEF in sand
    try:
        if conditions[constants.WEATHER] == constants.SAND and 'rock' in defender.types:
            defending_stats[constants.SPECIAL_DEFENSE] = int(defending_stats[constants.SPECIAL_DEFENSE] * 1.5)
    except KeyError:
        pass

    damage = int(int((2 * attacker.level) / 5) + 2) * attacking_move[constants.BASE_POWER]
    damage = int(damage * attacking_stats[attack] / defending_stats[defense])
    damage = int(damage / 50) + 2
    damage *= calculate_modifier(attacker, defender, defending_types, attacking_move, conditions)

    damage_rolls = get_damage_rolls(damage, calc_type)

    return list(set(damage_rolls))


def is_super_effective(move_type, defending_pokemon_types):
    multiplier = type_effectiveness_modifier(move_type, defending_pokemon_types)
    return multiplier > 1


def is_not_very_effective(move_type, defending_pokemon_types):
    multiplier = type_effectiveness_modifier(move_type, defending_pokemon_types)
    return multiplier < 1


def calculate_modifier(attacker, defender, defending_types, attacking_move, conditions):

    modifier = 1
    modifier *= type_effectiveness_modifier(attacking_move[constants.TYPE], defending_types)
    modifier *= weather_modifier(attacking_move, conditions.get(constants.WEATHER))
    modifier *= stab_modifier(attacker, attacking_move)
    modifier *= burn_modifier(attacker, attacking_move)
    modifier *= terrain_modifier(attacker, defender, attacking_move, conditions.get(constants.TERRAIN))
    modifier *= volatile_status_modifier(attacking_move, attacker, defender)

    if attacker.ability != 'infiltrator':
        modifier *= light_screen_modifier(attacking_move, conditions.get(constants.LIGHT_SCREEN))
        modifier *= reflect_modifier(attacking_move, conditions.get(constants.REFLECT))
        modifier *= aurora_veil_modifier(conditions.get(constants.AURORA_VEIL))

    return modifier


def get_move(move):
    if isinstance(move, dict):
        return move
    if isinstance(move, str):
        return deepcopy(all_move_json.get(move, None))
    else:
        return None


def get_damage_rolls(damage, calc_type):
    if calc_type == 'average':
        damage *= 0.925
        return [int(damage)]
    elif calc_type == 'min':
        return [int(damage * 0.85)]
    elif calc_type == 'max':
        return [int(damage)]
    elif calc_type == 'min_max':
        return [
            int(damage * 0.85),
            int(damage)
        ]
    elif calc_type == 'min_max_average':
        return [
            int(damage * 0.85),
            int(damage * 0.925),
            int(damage)
        ]
    elif calc_type == 'all':
        return [
            int(damage * 0.85),
            int(damage * 0.86),
            int(damage * 0.87),
            int(damage * 0.88),
            int(damage * 0.89),
            int(damage * 0.90),
            int(damage * 0.91),
            int(damage * 0.92),
            int(damage * 0.93),
            int(damage * 0.94),
            int(damage * 0.95),
            int(damage * 0.96),
            int(damage * 0.97),
            int(damage * 0.98),
            int(damage * 0.99),
            int(damage)
        ]


def type_effectiveness_modifier(attacking_move_type, defending_types):
    modifier = 1
    attacking_type_index = pokemon_type_indicies[attacking_move_type]
    for pkmn_type in defending_types:
        defending_type_index = pokemon_type_indicies[pkmn_type]
        modifier *= damage_multipication_array[attacking_type_index][defending_type_index]

    return modifier


def weather_modifier(attacking_move, weather):
    if not isinstance(weather, str):
        return 1

    if weather == constants.SUN and attacking_move[constants.TYPE] == 'fire':
        return 1.5
    elif weather == constants.SUN and attacking_move[constants.TYPE] == 'water':
        return 0.5
    elif weather == constants.RAIN and attacking_move[constants.TYPE] == 'water':
        return 1.5
    elif weather == constants.RAIN and attacking_move[constants.TYPE] == 'fire':
        return 0.5
    elif weather == constants.HEAVY_RAIN and attacking_move[constants.TYPE] == 'fire':
        return 0
    elif weather == constants.HEAVY_RAIN and attacking_move[constants.TYPE] == 'water':
        return 1.5
    elif weather == constants.DESOLATE_LAND and attacking_move[constants.TYPE] == 'water':
        return 0
    elif weather == constants.DESOLATE_LAND and attacking_move[constants.TYPE] == 'fire':
        return 1.5
    return 1


def stab_modifier(attacking_pokemon, attacking_move):
    if attacking_move[constants.TYPE] in [t for t in attacking_pokemon.types]:
        return 1.5
    
    return 1


def burn_modifier(attacking_pokemon, attacking_move):
    if constants.BURN == attacking_pokemon.status and attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        return 0.5
    return 1


def light_screen_modifier(attacking_move, light_screen):
    if light_screen and attacking_move[constants.CATEGORY] == constants.SPECIAL:
        return 0.5
    return 1


def reflect_modifier(attacking_move, reflect):
    if reflect and attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        return 0.5
    return 1


def aurora_veil_modifier(aurora_veil):
    if aurora_veil:
        return 0.5
    return 1


def terrain_modifier(attacker, defender, attacking_move, terrain):
    if terrain == constants.ELECTRIC_TERRAIN and attacking_move[constants.TYPE] == 'electric' and attacker.is_grounded():
        return TERRAIN_DAMAGE_BOOST
    elif terrain == constants.GRASSY_TERRAIN and attacking_move[constants.TYPE] == 'grass' and attacker.is_grounded():
        return TERRAIN_DAMAGE_BOOST
    elif terrain == constants.GRASSY_TERRAIN and attacking_move[constants.ID] == 'earthquake':
        return 0.5
    elif terrain == constants.MISTY_TERRAIN and attacking_move[constants.TYPE] == 'dragon' and defender.is_grounded():
        return 0.5
    elif terrain == constants.PSYCHIC_TERRAIN and attacking_move[constants.TYPE] == 'psychic' and attacker.is_grounded():
        return TERRAIN_DAMAGE_BOOST
    elif terrain == constants.PSYCHIC_TERRAIN and attacking_move[constants.PRIORITY] > 0 and defender.is_grounded():
        return 0
    return 1


def volatile_status_modifier(attacking_move, attacker, defender):
    modifier = 1
    if 'magnetrise' in defender.volatile_status and attacking_move[constants.TYPE] == 'ground' and attacking_move[constants.ID] != 'thousandarrows':
        modifier *= 0
    if 'flashfire' in attacker.volatile_status and attacking_move[constants.TYPE] == 'fire':
        modifier *= 1.5
    if 'tarshot' in defender.volatile_status and attacking_move[constants.TYPE] == 'fire':
        modifier *= 2
    if 'phantomforce' in defender.volatile_status:
        modifier *= 0
    if 'shadowforce' in defender.volatile_status:
        modifier *= 0
    if (
        'dive' in defender.volatile_status and
        attacker.ability != "noguard" and
        defender.ability != "noguard" and
        attacking_move[constants.ID] not in [
            "surf", "whirlpool"
        ]
    ):
        modifier *= 0
    if (
        'dig' in defender.volatile_status and
        attacker.ability != "noguard" and
        defender.ability != "noguard" and
        attacking_move[constants.ID] not in [
            "earthquake", "magnitude", "fissure"
        ]
    ):
        modifier *= 0
    if (
        (
            "fly" in defender.volatile_status or
            "bounce" in defender.volatile_status
        ) and
        attacker.ability != "noguard" and
        defender.ability != "noguard" and
        attacking_move[constants.ID] not in [
            "gust", "thunder", "twister", "skyuppercut", "hurricane", "thousandarrows", "smackdown"
        ]
    ):
        modifier *= 0
    return modifier


def calculate_damage(state, attacking_side_string, attacking_move, defending_move, calc_type='average'):
    # a wrapper for `_calculate_damage` that takes into account move/item/ability special-effects
    from showdown.engine.find_state_instructions import update_attacking_move
    from showdown.engine.find_state_instructions import user_moves_first

    attacking_move_dict = get_move(attacking_move)
    if defending_move.startswith(constants.SWITCH_STRING + " "):
        defending_move_dict = {constants.SWITCH_STRING: defending_move.split(constants.SWITCH_STRING)[-1]}
    else:
        defending_move_dict = get_move(defending_move)

    if attacking_side_string == constants.USER:
        attacking_side = state.user
        defending_side = state.opponent
    elif attacking_side_string == constants.OPPONENT:
        attacking_side = state.opponent
        defending_side = state.user
    else:
        raise ValueError("attacking_side_string must be one of: ['self', 'opponent']")

    conditions = {
        constants.REFLECT: defending_side.side_conditions[constants.REFLECT],
        constants.LIGHT_SCREEN: defending_side.side_conditions[constants.LIGHT_SCREEN],
        constants.AURORA_VEIL: defending_side.side_conditions[constants.AURORA_VEIL],
        constants.WEATHER: state.weather,
        constants.TERRAIN: state.field
    }

    attacker_moves_first = user_moves_first(state, attacking_move_dict, defending_move_dict)

    if constants.CHARGE in attacking_move_dict[constants.FLAGS]:
        attacking_move_dict = attacking_move_dict.copy()
        # a charge move doesn't need to charge when only calculating damage
        attacking_move_dict[constants.FLAGS].pop(constants.CHARGE, None)

    attacking_move_dict = update_attacking_move(
        attacking_side.active,
        defending_side.active,
        attacking_move_dict,
        defending_move_dict,
        attacker_moves_first,
        state.weather,
        state.field
    )

    return _calculate_damage(attacking_side.active, defending_side.active, attacking_move_dict, conditions=conditions, calc_type=calc_type)


def calculate_futuresight_damage(state, attacking_side_string, future_sight_user, calc_type='average'):
    if attacking_side_string == constants.USER:
        attacking_side = state.user
        defending_side = state.opponent
    else:
        attacking_side = state.opponent
        defending_side = state.user

    if attacking_side.active.id == future_sight_user:
        attacker = attacking_side.active
    else:
        attacker = attacking_side.reserve[future_sight_user]

    defender = defending_side.active

    attacking_move_dict = {
        "accuracy": 100,
        "basePower": 120,
        "category": "special",
        "flags": {},
        "id": "futuresight",
        "name": "Future Sight",
        "priority": 0,
        "secondary": False,
        "target": "normal",
        "type": "psychic",
        "pp": 10
    }

    conditions = {
        constants.REFLECT: defending_side.side_conditions[constants.REFLECT],
        constants.LIGHT_SCREEN: defending_side.side_conditions[constants.LIGHT_SCREEN],
        constants.AURORA_VEIL: defending_side.side_conditions[constants.AURORA_VEIL],
        constants.WEATHER: state.weather,
        constants.TERRAIN: state.field
    }

    return _calculate_damage(
        attacker,
        defender,
        attacking_move_dict,
        conditions=conditions,
        calc_type=calc_type
    )
