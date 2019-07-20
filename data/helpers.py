import operator

import constants

import data
from data import all_random_battle_sets
from data.parse_smogon_stats import get_smogon_stats_file_name
from data.parse_smogon_stats import get_pokemon_information

from data.parse_smogon_stats import moves_string
from data.parse_smogon_stats import spreads_string
from data.parse_smogon_stats import ability_string
from data.parse_smogon_stats import item_string

from config import logger


# these items will either reveal themselves automatically, or not have a meaningful impact to the bot
# therefore, we do not want to assign them to a pokemon as a guess
PASS_ITEMS = {
    'leftovers',
    'focussash',
    'blacksludge',
    'lifeorb'
}


def _get_random_battle_set(pkmn):
    return all_random_battle_sets[pkmn]


def _get_standard_battle_set(pkmn):
    try:
        return data.standard_battle_sets[pkmn]
    except KeyError:
        possible_names = [p for p in data.standard_battle_sets if pkmn.startswith(p)]
        if not possible_names:
            raise KeyError
        else:
            new_name = possible_names[0]
            logger.debug("{} not in the sets lookup, using {} instead".format(pkmn, new_name))
            return data.standard_battle_sets[new_name]


def get_all_possible_moves_for_random_battle(pkmn_name, known_moves):
    try:
        sets = _get_random_battle_set(pkmn_name)
    except KeyError:
        logger.warning("{} not in the sets lookup".format(pkmn_name))
        return []

    new_moves = list()
    for key in sets[constants.SETS]:
        this_set_moves = key.split('|')
        if all(m in this_set_moves for m in known_moves):
            for m in filter(lambda x: x not in new_moves + known_moves, this_set_moves):
                new_moves.append(m)

    return new_moves


def get_most_likely_ability_for_random_battle(pkmn_name):
    try:
        sets = _get_random_battle_set(pkmn_name)
    except KeyError:
        logger.warning("{} not in the sets lookup".format(pkmn_name))
        return None

    abilities = sets[constants.ABILITIES]
    if not abilities:
        logger.warning("{} has no abilities in the random battle lookup!")
        return None

    return sorted(abilities.items(), key=operator.itemgetter(1), reverse=True)[0][0]


def get_most_likely_item_for_random_battle_pokemon(pkmn_name):
    try:
        sets = _get_random_battle_set(pkmn_name)
    except KeyError:
        logger.warning("{} not in the sets lookup".format(pkmn_name))
        return None

    best_item = None
    best_value = float('-inf')
    for item, value in sets[constants.ITEMS].items():
        if value > best_value and item not in PASS_ITEMS:
            best_item = item
            best_value = value

    return best_item


def get_all_possible_moves_for_standard_battle(pkmn_name, known_moves):
    try:
        sets = _get_standard_battle_set(pkmn_name)
    except KeyError:
        logger.warning("{} not in the sets lookup".format(pkmn_name))
        return []

    new_move_count = 6 - len(known_moves)
    moves_added = 0
    new_moves = list()
    for m in sets[moves_string][:6]:
        if m not in known_moves:
            if constants.HIDDEN_POWER in m:
                m = "{}{}".format(m, constants.HIDDEN_POWER_ACTIVE_MOVE_BASE_DAMAGE_STRING)
            new_moves.append(m)
            moves_added += 1
        if moves_added == new_move_count:
            return new_moves

    return new_moves


def get_most_likely_ability_for_standard_battle(pkmn_name):
    try:
        sets = _get_standard_battle_set(pkmn_name)
    except KeyError:
        logger.warning("{} not in the sets lookup".format(pkmn_name))
        return None

    return sets[ability_string][0]


def get_most_likely_item_for_standard_battle_pokemon(pkmn_name):
    try:
        sets = _get_standard_battle_set(pkmn_name)
    except KeyError:
        logger.warning("{} not in the sets lookup".format(pkmn_name))
        return None

    for item in sets[item_string]:
        if item not in PASS_ITEMS:
            return item
    else:
        return None


def get_most_likely_spread_for_standard_battle(pkmn_name):
    try:
        sets = _get_standard_battle_set(pkmn_name)
    except KeyError:
        logger.warning("{} not in the sets lookup".format(pkmn_name))
        return 'serious', "85,85,85,85,85,85"

    return sets[spreads_string][0]


def get_standard_battle_sets(battle_mode):
    if any(battle_mode.endswith(s) for s in constants.SMOGON_HAS_STATS_PAGE_SUFFIXES):
        smogon_stats_file_name = get_smogon_stats_file_name(battle_mode)
        logger.debug("Making HTTP request to {} for usage stats".format(smogon_stats_file_name))
        smogon_usage_data = get_pokemon_information(smogon_stats_file_name)
    else:
        # use ALL data for a mode like battle-factory
        logger.debug("Making HTTP request for ALL usage stats\nplease wait...")
        ou_data = get_pokemon_information(get_smogon_stats_file_name("gen7ou"))
        uu_data = get_pokemon_information(get_smogon_stats_file_name("gen7uu"))
        ru_data = get_pokemon_information(get_smogon_stats_file_name("gen7ru"))
        nu_data = get_pokemon_information(get_smogon_stats_file_name("gen7nu"))
        pu_data = get_pokemon_information(get_smogon_stats_file_name("gen7pu"))
        lc_data = get_pokemon_information(get_smogon_stats_file_name("gen7lc"))

        smogon_usage_data = ou_data
        for pkmn_data in [uu_data, ru_data, nu_data, pu_data, lc_data]:
            for pkmn_name in pkmn_data:
                if pkmn_name not in smogon_usage_data:
                    smogon_usage_data[pkmn_name] = pkmn_data[pkmn_name]

    return smogon_usage_data
