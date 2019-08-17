import constants
from data import all_move_json
from collections import namedtuple


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
    'typeless': 18
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


def _get_damage_multiplier(move_type, defending_pokemon_types):
    multiplier = 1
    for pkmn_type in defending_pokemon_types:
        multiplier *= damage_multipication_array[pokemon_type_indicies[move_type]][pokemon_type_indicies[pkmn_type]]
    return multiplier


def is_super_effective(move_type, defending_pokemon_types):
    multiplier = _get_damage_multiplier(move_type, defending_pokemon_types)
    return multiplier > 1


def is_not_very_effective(move_type, defending_pokemon_types):
    multiplier = _get_damage_multiplier(move_type, defending_pokemon_types)
    return multiplier < 1


class DamageCalculator:

    def __init__(self):
        self.special_logic = {
            "seismictoss",
            "nightshade",
            "superfang",
            "naturesmadness",
            "finalgambit",
            "endeavor"
        }

    def calculate_modifier(self, attacker, defender, attacking_move, conditions: dict):

        modifier = 1
        modifier *= type_effectiveness_modifier(attacking_move, defender)
        modifier *= weather_modifier(attacking_move, conditions.get(constants.WEATHER))
        modifier *= stab_modifier(attacker, attacking_move)
        modifier *= burn_modifier(attacker, attacking_move)
        modifier *= terrain_modifier(attacker, defender, attacking_move, conditions.get(constants.TERRAIN))

        if attacker.ability != 'infiltrator':
            modifier *= light_screen_modifier(attacking_move, conditions.get(constants.LIGHT_SCREEN))
            modifier *= reflect_modifier(attacking_move, conditions.get(constants.REFLECT))
            modifier *= aurora_veil_modifier(conditions.get(constants.AURORA_VEIL))

        return modifier

    def _get_move(self, move):
        if isinstance(move, dict):
            return move
        if isinstance(move, str):
            move = clean_string(move)
            return all_move_json.get(move, None)
        else:
            return None

    def _get_damage_rolls(self, damage, calc_type):
        if calc_type == 'average':
            damage *= 0.925
            return [int(damage)]
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

    def calculate_damage(self, attacker, defender, attacking_move, conditions: dict=None, calc_type='average'):
        acceptable_calc_types = ['average', 'max', 'min_max', 'min_max_average', 'all']
        if calc_type not in acceptable_calc_types:
            raise ValueError("{} is not one of {}".format(calc_type, acceptable_calc_types))

        attacking_move = self._get_move(attacking_move)
        if attacking_move is None:
            raise TypeError("Invalid move")

        attacking_type = clean_string(attacking_move.get(constants.CATEGORY))
        if attacking_type == constants.PHYSICAL:
            attack = constants.ATTACK
            defense = constants.DEFENSE
        elif attacking_type == constants.SPECIAL:
            attack = constants.SPECIAL_ATTACK
            defense = constants.SPECIAL_DEFENSE
        else:
            return None

        if attacking_move[constants.ID] in self.special_logic:
            return special_logic(attacking_move[constants.ID], attacker, defender)

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

        # rock types get 1.5x SPDEF in sand
        try:
            if conditions[constants.WEATHER] == constants.SAND and 'rock' in defender.types:
                defending_stats[constants.SPECIAL_DEFENSE] = int(defending_stats[constants.SPECIAL_DEFENSE] * 1.5)
        except KeyError:
            pass

        damage = int(int((2 * attacker.level) / 5) + 2) * attacking_move[constants.BASE_POWER]
        damage = int(damage * attacking_stats[attack] / defending_stats[defense])
        damage = int(damage / 50) + 2
        damage *= self.calculate_modifier(attacker, defender, attacking_move, conditions)

        damage_rolls = self._get_damage_rolls(damage, calc_type)

        return list(set(damage_rolls))


def special_logic(move_name, attacker, defender):
    if move_name == "seismictoss" and "ghost" not in defender.types:
        return [int(attacker.level)]
    elif move_name == "nightshade" and "normal" not in defender.types:
        return [int(attacker.level)]
    elif move_name == "superfang" and "ghost" not in defender.types:
        return [int(defender.hp / 2)]
    elif move_name == "naturesmadness":
        return [int(defender.hp / 2)]
    elif move_name == "finalgambit" and "ghost" not in defender.types:
        return [int(attacker.hp)]
    elif move_name == "endeavor" and "ghost" not in defender.types:
        if defender.hp > attacker.hp:
            return [int(defender.hp - attacker.hp)]
        else:
            return [0]


def clean_string(s):
    return s.lower().replace(' ', '')


def type_effectiveness_modifier(attacking_move, defending_pokemon):
    modifier = 1
    attacking_type_index = pokemon_type_indicies[clean_string(attacking_move[constants.TYPE])]
    for pkmn_type in defending_pokemon.types:
        defending_type_index = pokemon_type_indicies[clean_string(pkmn_type)]
        modifier *= damage_multipication_array[attacking_type_index][defending_type_index]

    return modifier


def weather_modifier(attacking_move: namedtuple, weather: str):
    if not isinstance(weather, str):
        return 1

    weather = clean_string(weather)

    if clean_string(weather) == constants.SUN and clean_string(attacking_move[constants.TYPE]) == 'fire':
        return 1.5
    elif weather == constants.RAIN and clean_string(attacking_move[constants.TYPE]) == 'water':
        return 1.5
    elif weather == constants.DESOLATE_LAND and clean_string(attacking_move[constants.TYPE]) == 'water':
        return 0
    return 1


def stab_modifier(attacking_pokemon, attacking_move):
    if clean_string(attacking_move[constants.TYPE]) in [clean_string(t) for t in attacking_pokemon.types]:
        return 1.5

    return 1


def burn_modifier(attacking_pokemon, attacking_move):
    if constants.BURN == attacking_pokemon.status and clean_string(attacking_move[constants.CATEGORY]) == constants.PHYSICAL:
        return 0.5
    return 1


def light_screen_modifier(attacking_move: namedtuple, light_screen: bool):
    if light_screen and clean_string(attacking_move[constants.CATEGORY]) == constants.SPECIAL:
        return 0.5
    return 1


def reflect_modifier(attacking_move: namedtuple, reflect: bool):
    if reflect and clean_string(attacking_move[constants.CATEGORY]) == constants.PHYSICAL:
        return 0.5
    return 1


def aurora_veil_modifier(aurora_veil: bool):
    if aurora_veil:
        return 0.5
    return 1


def terrain_modifier(attacker, defender, attacking_move, terrain):
    if terrain == constants.ELECTRIC_TERRAIN and attacking_move[constants.TYPE] == 'electric' and attacker.is_grounded():
        return 1.5
    elif terrain == constants.GRASSY_TERRAIN and attacking_move[constants.TYPE] == 'grass' and attacker.is_grounded():
        return 1.5
    elif terrain == constants.GRASSY_TERRAIN and attacking_move[constants.ID] == 'earthquake':
        return 0.5
    elif terrain == constants.MISTY_TERRAIN and attacking_move[constants.TYPE] == 'dragon' and defender.is_grounded():
        return 0.5
    elif terrain == constants.PSYCHIC_TERRAIN and attacking_move[constants.TYPE] == 'psychic' and attacker.is_grounded():
        return 1.5
    elif terrain == constants.PSYCHIC_TERRAIN and attacking_move[constants.PRIORITY] > 0:
        return 0
    return 1
