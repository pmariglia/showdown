import constants

import data
from data import pokedex
from data.parse_smogon_stats import get_smogon_stats_file_name
from data.parse_smogon_stats import get_pokemon_information

from data.parse_smogon_stats import MOVES_STRING
from data.parse_smogon_stats import SPREADS_STRING
from data.parse_smogon_stats import ABILITY_STRING
from data.parse_smogon_stats import ITEM_STRING

import logging
logger = logging.getLogger(__name__)


# these items will either reveal themselves automatically, or do not have a meaningful impact to the bot
# therefore, we do not want to assign them to a pokemon as a guess
PASS_ITEMS = {
    'leftovers',
    'focussash',
    'blacksludge',
    'airballoon'
}

# these abilities either reveal themselves automatically, or do not have a meaningful impact to the bot
# therefore, we do not want to assign them to a pokemon as a guess
PASS_ABILITIES = {
    'moldbreaker',
    'pressure',
    'trace',
    'download'
}

MAX_STANDARD_BATTLE_MOVES = 6


def get_pokemon_sets(pkmn):
    try:
        return data.pokemon_sets[pkmn]
    except KeyError:
        possible_names = [p for p in data.pokemon_sets if pkmn.startswith(p)]
        if not possible_names:
            raise KeyError
        else:
            new_name = possible_names[0]
            logger.debug("{} not in the sets lookup, using {} instead".format(pkmn, new_name))
            return data.pokemon_sets[new_name]


def get_all_possible_moves_for_random_battle(pkmn_name, known_moves):
    try:
        sets = data.random_battle_sets[pkmn_name]
    except KeyError:
        logger.warning("{} not in the random-battle sets lookup".format(pkmn_name))
        return []

    new_moves = list()
    for key in sets[constants.SETS]:
        this_set_moves = key.split('|')
        if all(m in this_set_moves for m in known_moves):
            for m in filter(lambda x: x not in new_moves + known_moves, this_set_moves):
                new_moves.append(m)

    if not new_moves:
        for m, _ in sets[constants.MOVES]:
            if m not in known_moves:
                new_moves.append(m)

    return new_moves


def get_most_likely_ability_for_random_battle(pkmn_name):
    try:
        sets = data.random_battle_sets[pkmn_name]
    except KeyError:
        logger.warning("{} not in the random-battle sets lookup".format(pkmn_name))
        return None

    abilities = sets[constants.ABILITIES]
    if not abilities:
        logger.warning("{} has no abilities in the random-battle lookup!")
        return None

    best_ability = None
    best_value = float('-inf')
    for ability, value in sorted(abilities, key=lambda x: x[1], reverse=True):
        if value > best_value and ability not in PASS_ABILITIES:
            best_value = value
            best_ability = ability

    return best_ability


def get_most_likely_item_for_random_battle(pkmn_name):
    try:
        sets = data.random_battle_sets[pkmn_name]
    except KeyError:
        logger.warning("{} not in the random-battle sets lookup".format(pkmn_name))
        return None

    best_item = None
    best_value = float('-inf')
    for item, value in sets[constants.ITEMS]:
        if value > best_value and item not in PASS_ITEMS:
            best_item = item
            best_value = value

    return best_item


def get_all_likely_moves(pkmn_name, known_moves):
    try:
        sets = get_pokemon_sets(pkmn_name)
    except KeyError:
        logger.warning("{} not in the sets lookup".format(pkmn_name))
        return get_all_possible_moves_for_random_battle(pkmn_name, known_moves)

    new_move_count = MAX_STANDARD_BATTLE_MOVES - len(known_moves)
    moves_added = 0
    new_moves = list()
    for m in [mv[0] for mv in sets[MOVES_STRING]]:
        if m not in known_moves:
            new_moves.append(m)
            moves_added += 1
        if moves_added == new_move_count:
            return new_moves

    return new_moves


def get_most_likely_ability(pkmn_name):
    try:
        sets = get_pokemon_sets(pkmn_name)
    except KeyError:
        logger.warning("{} not in the sets lookup, using random battle abilities".format(pkmn_name))
        return get_most_likely_ability_for_random_battle(pkmn_name)

    return sets[ABILITY_STRING][0][0]


def get_most_likely_item(pkmn_name):
    try:
        sets = get_pokemon_sets(pkmn_name)
    except KeyError:
        logger.warning("{} not in the sets lookup, using random battle items".format(pkmn_name))
        return get_most_likely_item_for_random_battle(pkmn_name)

    for item in [i[0] for i in sets[ITEM_STRING]]:
        if item not in PASS_ITEMS:
            return item
    else:
        return None


def get_most_likely_spread(pkmn_name):
    try:
        sets = get_pokemon_sets(pkmn_name)
    except KeyError:
        logger.warning("{} not in the sets lookup".format(pkmn_name))
        return 'serious', "85,85,85,85,85,85", 0

    return sets[SPREADS_STRING][0]


def get_standard_battle_sets(battle_mode, pokemon_names=None):
    if any(battle_mode.endswith(s) for s in constants.SMOGON_HAS_STATS_PAGE_SUFFIXES):
        smogon_stats_file_name = get_smogon_stats_file_name(battle_mode)
        logger.debug("Making HTTP request to {} for usage stats".format(smogon_stats_file_name))
        smogon_usage_data = get_pokemon_information(smogon_stats_file_name, pkmn_names=pokemon_names)
    else:
        # use ALL data for a mode like battle-factory
        logger.debug("Making HTTP request for ALL usage stats\nplease wait...")
        ubers_data = get_pokemon_information(get_smogon_stats_file_name("gen8ubers"), pkmn_names=pokemon_names)
        ou_data = get_pokemon_information(get_smogon_stats_file_name("gen8ou"), pkmn_names=pokemon_names)
        uu_data = get_pokemon_information(get_smogon_stats_file_name("gen8uu"), pkmn_names=pokemon_names)
        ru_data = get_pokemon_information(get_smogon_stats_file_name("gen8ru"), pkmn_names=pokemon_names)
        nu_data = get_pokemon_information(get_smogon_stats_file_name("gen8nu"), pkmn_names=pokemon_names)
        pu_data = get_pokemon_information(get_smogon_stats_file_name("gen8pu"), pkmn_names=pokemon_names)
        lc_data = get_pokemon_information(get_smogon_stats_file_name("gen8lc"), pkmn_names=pokemon_names)

        smogon_usage_data = lc_data
        for pkmn_data in [pu_data, nu_data, ru_data, uu_data, ou_data, ubers_data]:
            for pkmn_name in pkmn_data:
                if pkmn_name not in smogon_usage_data:
                    smogon_usage_data[pkmn_name] = pkmn_data[pkmn_name]

    return smogon_usage_data


def get_mega_pkmn_name(pkmn_name):
    mega_name = "{}mega".format(pkmn_name)
    if mega_name in pokedex:
        return mega_name
    elif mega_name + "x" in pokedex:  # for megas with two evolutions, return the x version
        return mega_name + "x"
    return None
