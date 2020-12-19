import os
import json
import logging
import constants
import data
from data import all_move_json
from data import pokedex
from showdown.engine import damage_calculator

logger = logging.getLogger(__name__)

CURRENT_GEN = 8
PWD = os.path.dirname(os.path.abspath(__file__))


PRE_PHYSICAL_SPECIAL_SPLIT_CATEGORY_LOOKUP = {
    "normal": constants.PHYSICAL,
    "fighting": constants.PHYSICAL,
    "flying": constants.PHYSICAL,
    "poison": constants.PHYSICAL,
    "ground": constants.PHYSICAL,
    "rock": constants.PHYSICAL,
    "bug": constants.PHYSICAL,
    "ghost": constants.PHYSICAL,
    "steel": constants.PHYSICAL,
    "fire": constants.SPECIAL,
    "water": constants.SPECIAL,
    "grass": constants.SPECIAL,
    "electric": constants.SPECIAL,
    "psychic": constants.SPECIAL,
    "ice": constants.SPECIAL,
    "dragon": constants.SPECIAL,
    "dark": constants.SPECIAL,
}


def apply_move_mods(gen_number):
    logger.debug("Applying move mod for gen {}".format(gen_number))
    for gen_number in reversed(range(gen_number, CURRENT_GEN)):
        with open("{}/gen{}_move_mods.json".format(PWD, gen_number), 'r') as f:
            move_mods = json.load(f)
        for move, modifications in move_mods.items():
            all_move_json[move].update(modifications)


def apply_pokedex_mods(gen_number):
    logger.debug("Applying dex mod for gen {}".format(gen_number))
    for gen_number in reversed(range(gen_number, CURRENT_GEN)):
        with open("{}/gen{}_pokedex_mods.json".format(PWD, gen_number), 'r') as f:
            pokedex_mods = json.load(f)
        for pokemon, modifications in pokedex_mods.items():
            pokedex[pokemon].update(modifications)


def set_random_battle_sets(gen_number):
    logger.debug("Setting random battle sets for gen {}".format(gen_number))
    with open("{}/random_battle_sets_gen{}.json".format(PWD, gen_number), 'r') as f:
        data.random_battle_sets = json.load(f)


def apply_gen_3_mods():
    # no pokedex mods in gen3 (apparently)
    constants.HIDDEN_POWER_TYPE_STRING_INDEX = -2
    constants.HIDDEN_POWER_ACTIVE_MOVE_BASE_DAMAGE_STRING = "70"
    constants.HIDDEN_POWER_RESERVE_MOVE_BASE_DAMAGE_STRING = "70"
    constants.REQUEST_DICT_ABILITY = "baseAbility"
    apply_move_mods(3)
    undo_physical_special_split()


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


def apply_gen_7_mods():
    apply_move_mods(7)
    apply_pokedex_mods(7)


def undo_physical_special_split():
    for move_name, move_data in all_move_json.items():
        if move_data[constants.CATEGORY] in constants.DAMAGING_CATEGORIES:
            try:
                move_data[constants.CATEGORY] = PRE_PHYSICAL_SPECIAL_SPLIT_CATEGORY_LOOKUP[move_data[constants.TYPE]]
            except KeyError:
                pass


def apply_mods(game_mode):
    if "gen3" in game_mode:
        apply_gen_3_mods()
    if "gen4" in game_mode:
        apply_gen_4_mods()
    elif "gen5" in game_mode:
        apply_gen_5_mods()
    elif "gen6" in game_mode:
        apply_gen_6_mods()
    elif "gen7" in game_mode:
        apply_gen_7_mods()

    if str(CURRENT_GEN) not in game_mode[:4]:
        set_random_battle_sets(7)  # use random battle sets from gen7 if we are not in gen8
        damage_calculator.TERRAIN_DAMAGE_BOOST = 1.5  # terrain gave a 1.5x damage boost prior to gen8
