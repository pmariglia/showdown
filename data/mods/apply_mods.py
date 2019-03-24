import os
import json
import constants
from data import all_move_json
from data import pokedex


CURRENT_GEN = 7
PWD = os.path.dirname(os.path.abspath(__file__))


def apply_move_mods(gen_number):
    for gen_number in reversed(range(gen_number, CURRENT_GEN)):
        with open("{}/gen{}_move_mods.json".format(PWD, gen_number), 'r') as f:
            move_mods = json.load(f)
        for move, modifications in move_mods.items():
            all_move_json[move].update(modifications)


def apply_pokedex_mods(gen_number):
    for gen_number in reversed(range(gen_number, CURRENT_GEN)):
        with open("{}/gen{}_pokedex_mods.json".format(PWD, gen_number), 'r') as f:
            pokedex_mods = json.load(f)
        for pokemon, modifications in pokedex_mods.items():
            pokedex[pokemon].update(modifications)


def apply_gen_4_mods():
    constants.HIDDEN_POWER_TYPE_STRING_INDEX = -2
    constants.HIDDEN_POWER_ACTIVE_MOVE_BASE_DAMAGE_STRING = "70"
    constants.HIDDEN_POWER_RESERVE_MOVE_BASE_DAMAGE_STRING = "70"
    constants.REQUEST_DICT_ABILITY = "baseAbility"
    apply_move_mods(4)
    apply_pokedex_mods(4)


def apply_gen_5_mods():
    constants.HIDDEN_POWER_TYPE_STRING_INDEX = -2
    constants.HIDDEN_POWER_ACTIVE_MOVE_BASE_DAMAGE_STRING = "70"
    constants.HIDDEN_POWER_RESERVE_MOVE_BASE_DAMAGE_STRING = "70"
    constants.REQUEST_DICT_ABILITY = "baseAbility"
    apply_move_mods(5)
    apply_pokedex_mods(5)


def apply_gen_6_mods():
    constants.REQUEST_DICT_ABILITY = "baseAbility"
    apply_move_mods(6)
    apply_pokedex_mods(6)


def apply_mods(game_mode):
    if "gen4" in game_mode:
        apply_gen_4_mods()
    elif "gen5" in game_mode:
        apply_gen_5_mods()
    elif "gen6" in game_mode:
        apply_gen_6_mods()
