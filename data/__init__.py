import os
import json

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
