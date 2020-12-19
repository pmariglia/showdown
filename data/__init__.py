import os
import json

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
