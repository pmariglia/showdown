import requests
from showdown.helpers import normalize_name

new_pokemon_indicator = """ +----------------------------------------+ \\n +----------------------------------------+"""

section_end_string = "----------"
spreads_string = "spreads"


def get_new_spreads(smogon_stats_url):
    """Parses a Smogon stats document, such as: 'https://www.smogon.com/stats/2019-02/moveset/gen7ou-1825.txt'
       Returns a dictionary containing the most common spreads for the pokemon in the file
    """
    r = requests.get(smogon_stats_url)

    split_string = str(r.content).split(new_pokemon_indicator)

    spreads = dict()
    for pokemon_data in split_string:
        segments = pokemon_data.split('|')
        it = iter(segments)
        pokemon_name = normalize_name(segments[1])
        spreads[pokemon_name] = list()
        for segment in it:
            if normalize_name(segment) == spreads_string:
                while section_end_string not in segment:
                    segment = next(it)
                    if ':' in segment:
                        split_segment = segment.split()
                        spread = split_segment[0]
                        nature = normalize_name(spread.split(':')[0])
                        evs = spread.split(':')[1].replace('/', ',')
                        spreads[pokemon_name].append((nature, evs))

    return spreads
