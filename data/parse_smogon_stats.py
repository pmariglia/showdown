import re
from datetime import datetime
from dateutil import relativedelta

import requests
from showdown.helpers import normalize_name

new_pokemon_indicator = """ +----------------------------------------+ \\n +----------------------------------------+"""

section_end_string = "----------"
other_string = "other"
moves_string = "moves"
item_string = "items"
spreads_string = "spreads"
ability_string = "abilities"

PERCENTAGES_REGEX = '[\d\.% ]'


def get_smogon_stats_file_name(game_mode):
    """
    Gets the smogon stats url based on the game mode
    Uses the previous-month's statistics
    """

    # always use the `-0` file - the higher ladder is for noobs
    smogon_url = "https://www.smogon.com/stats/{}-{}/moveset/{}-0.txt"

    previous_month = datetime.now() - relativedelta.relativedelta(months=2)
    year = previous_month.year
    month = "{:02d}".format(previous_month.month)

    return smogon_url.format(year, month, game_mode)


def get_pokemon_information(smogon_stats_url):
    """Parses a Smogon stats document, such as: 'https://www.smogon.com/stats/2019-02/moveset/gen7ou-1825.txt'
       Returns a dictionary containing the most likely spreads, items, and moves for each pokemon in order of likelihood
    """
    r = requests.get(smogon_stats_url)

    split_string = str(r.content).split(new_pokemon_indicator)

    pokemon_information = dict()
    for pokemon_data in split_string:
        segments = pokemon_data.split('|')
        it = iter(segments)
        pokemon_name = normalize_name(segments[1])
        pokemon_information[pokemon_name] = dict()
        pokemon_information[pokemon_name][spreads_string] = list()
        pokemon_information[pokemon_name][item_string] = list()
        pokemon_information[pokemon_name][moves_string] = list()
        pokemon_information[pokemon_name][ability_string] = list()
        for segment in it:
            if normalize_name(segment) == spreads_string:
                while section_end_string not in segment:
                    segment = next(it)
                    if ':' in segment:
                        split_segment = segment.split()
                        spread = split_segment[0]
                        nature = normalize_name(spread.split(':')[0])
                        evs = spread.split(':')[1].replace('/', ',')
                        pokemon_information[pokemon_name][spreads_string].append((nature, evs))

            elif normalize_name(segment) == item_string:
                while section_end_string not in segment:
                    segment = next(it)
                    if '%' in segment:
                        item = normalize_name(re.sub(PERCENTAGES_REGEX, '', segment).strip())
                        if item != other_string:
                            pokemon_information[pokemon_name][item_string].append(item)

            elif normalize_name(segment) == moves_string:
                while section_end_string not in segment:
                    segment = next(it)
                    if '%' in segment:
                        move = normalize_name(re.sub(PERCENTAGES_REGEX, '', segment).strip())
                        if move != other_string:
                            pokemon_information[pokemon_name][moves_string].append(move)

            elif normalize_name(segment) == ability_string:
                while section_end_string not in segment:
                    segment = next(it)
                    if '%' in segment:
                        ability = normalize_name(re.sub(PERCENTAGES_REGEX, '', segment).strip())
                        if ability != other_string:
                            pokemon_information[pokemon_name][ability_string].append(ability)

    return pokemon_information
