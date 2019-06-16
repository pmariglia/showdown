import os
import json

from config import logger

PWD = os.path.dirname(os.path.abspath(__file__))

move_json_location = PWD + '/moves.json'
with open(move_json_location) as f:
    all_move_json = json.load(f)

pkmn_json_location = PWD + '/pokedex.json'
with open(pkmn_json_location, 'r') as f:
    pokedex = json.loads(f.read())


move_set_json_location = PWD + '/random_battle_moves.json'
with open(move_set_json_location) as f:
    all_move_sets = json.load(f)


def get_most_likely_spread(pokemon_name):
    with open("{}/spreads.json".format(PWD), 'r') as pokemon_spreads:
        j = json.load(pokemon_spreads)
    try:
        most_likely_spread = j[pokemon_name][0]
        logger.debug("Spread assumption for {}: {}".format(pokemon_name, most_likely_spread))
    except KeyError:
        logger.debug("No spreads found for {}, using random-battle spreads".format(pokemon_name))
        return 'serious', [85, 85, 85, 85, 85, 85]
    nature = most_likely_spread[0]
    evs = most_likely_spread[1].split(',')
    evs = [int(e) for e in evs]

    return nature, evs
