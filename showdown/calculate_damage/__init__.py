from .damage_calculator import DamageCalculator
from .damage_calculator import damage_multipication_array
from .damage_calculator import pokemon_type_indicies


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
