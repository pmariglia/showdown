import ntpath
import re
from datetime import datetime
from dateutil import relativedelta

import requests

import constants
from showdown.helpers import normalize_name

NEW_PKMN_INDICATOR = """ +----------------------------------------+ \\n +----------------------------------------+"""

SECTION_END_STRING = "----------"
OTHER_STRING = "other"
MOVES_STRING = "moves"
ITEM_STRING = "items"
SPREADS_STRING = "spreads"
ABILITY_STRING = "abilities"

PERCENTAGES_REGEX = '(\d+\.\d+%)'


def get_smogon_stats_file_name(game_mode, month_delta=1):
    """
    Gets the smogon stats url based on the game mode
    Uses the previous-month's statistics
    """

    # blitz comes and goes - use the non-blitz version
    if game_mode.endswith('blitz'):
        game_mode = game_mode[:-5]

    # always use the `-0` file - the higher ladder is for noobs
    smogon_url = "https://www.smogon.com/stats/{}-{}/moveset/{}-0.txt"

    previous_month = datetime.now() - relativedelta.relativedelta(months=month_delta)
    year = previous_month.year
    month = "{:02d}".format(previous_month.month)

    return smogon_url.format(year, month, game_mode)


def get_pokemon_information(smogon_stats_url):
    """Parses a Smogon stats document, such as: 'https://www.smogon.com/stats/2019-02/moveset/gen7ou-1825.txt'
       Returns a dictionary containing the most likely spreads, items, and moves for each pokemon in order of likelihood
    """
    r = requests.get(smogon_stats_url)
    if r.status_code == 404:
        r = requests.get(get_smogon_stats_file_name(ntpath.basename(smogon_stats_url.replace('-0.txt', '')), month_delta=2))

    split_string = str(r.content).split(NEW_PKMN_INDICATOR)

    pokemon_information = dict()
    for pokemon_data in split_string:
        segments = pokemon_data.split('|')
        it = iter(segments)
        pokemon_name = normalize_name(segments[1])
        pokemon_information[pokemon_name] = dict()
        pokemon_information[pokemon_name][SPREADS_STRING] = list()
        pokemon_information[pokemon_name][ITEM_STRING] = list()
        pokemon_information[pokemon_name][MOVES_STRING] = list()
        pokemon_information[pokemon_name][ABILITY_STRING] = list()
        for segment in it:
            if normalize_name(segment) == SPREADS_STRING:
                while SECTION_END_STRING not in segment:
                    segment = next(it)
                    if ':' in segment:
                        split_segment = segment.split()
                        spread = split_segment[0]
                        nature = normalize_name(spread.split(':')[0])
                        evs = spread.split(':')[1].replace('/', ',')
                        percentage = float(re.search(PERCENTAGES_REGEX, segment).group()[:-1])
                        pokemon_information[pokemon_name][SPREADS_STRING].append((nature, evs, percentage))

            elif normalize_name(segment) == ITEM_STRING:
                while SECTION_END_STRING not in segment:
                    segment = next(it)
                    if '%' in segment:
                        item = normalize_name(re.sub(PERCENTAGES_REGEX, '', segment).strip())
                        percentage = float(re.search(PERCENTAGES_REGEX, segment).group()[:-1])
                        if item != OTHER_STRING:
                            pokemon_information[pokemon_name][ITEM_STRING].append((item, percentage))

            elif normalize_name(segment) == MOVES_STRING:
                while SECTION_END_STRING not in segment:
                    segment = next(it)
                    if '%' in segment:
                        move = normalize_name(re.sub(PERCENTAGES_REGEX, '', segment).strip())
                        percentage = float(re.search(PERCENTAGES_REGEX, segment).group()[:-1])
                        if move != OTHER_STRING:
                            if constants.HIDDEN_POWER in move:
                                move = "{}60".format(move)
                            pokemon_information[pokemon_name][MOVES_STRING].append((move, percentage))

            elif normalize_name(segment) == ABILITY_STRING:
                while SECTION_END_STRING not in segment:
                    segment = next(it)
                    if '%' in segment:
                        ability = normalize_name(re.sub(PERCENTAGES_REGEX, '', segment).strip())
                        percentage = float(re.search(PERCENTAGES_REGEX, segment).group()[:-1])
                        if ability != OTHER_STRING:
                            pokemon_information[pokemon_name][ABILITY_STRING].append((ability, percentage))

    return pokemon_information
