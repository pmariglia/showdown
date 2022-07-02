import os
import json
import logging

logger = logging.getLogger(__name__)

PWD = os.path.dirname(os.path.abspath(__file__))

move_json_location = os.path.join(PWD, 'moves.json')
with open(move_json_location) as f:
    all_move_json = json.load(f)

pkmn_json_location = os.path.join(PWD, 'pokedex.json')
with open(pkmn_json_location, 'r') as f:
    pokedex = json.loads(f.read())

random_battle_set_location = os.path.join(PWD, 'random_battle_sets.json')
with open(random_battle_set_location, 'r') as f:
    random_battle_sets = json.load(f)


pokemon_sets = random_battle_sets
effectiveness = {}
ou_sets = None


def get_ou_sets(pkmn_names):
    sets = os.path.join(PWD, 'ou_sets.json')
    with open(sets, 'r') as f:
        sets_dict = json.load(f)["pokemon"]

    result = {}
    for pkmn in pkmn_names:
        try:
            result[pkmn] = sets_dict[pkmn]
        except KeyError:
            logger.warning("No pokemon information being added for {}".format(pkmn))

    return result


def get_ou_team(pkmn_names):
    sets = os.path.join(PWD, 'ou_sets.json')
    with open(sets, 'r') as f:
        teams_dict = json.load(f)["teams"]

    pkmn_lookup = "|".join(pkmn_names)
    try:
        return teams_dict[pkmn_lookup][0]
    except KeyError:
        return None
