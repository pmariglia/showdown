"""
Parses a text file with lines containing the format:
    pkmn_name|level|move1|move2|move3|move4|ability|item

Creates a JSON file with the data arranged in a way that the bot can use to understand
This was made for the purposes of random battles
"""

import json
import constants
from showdown.helpers import normalize_name

fp = "sets.txt"
pokedex_path = "../pokedex.json"


all_pokemon_dict = dict()


def add_thing_to_dict_or_increment(d, second_key, thing):
    if thing in d[second_key]:
        d[second_key][thing] += 1
    else:
        d[second_key][thing] = 1


with open(pokedex_path, 'r') as f:
    pokedex = json.load(f)


with open(fp, 'r') as f:
    lines = f.readlines()

for l in lines:
    split_lines = l.strip().split('|')
    if len(split_lines) != 8:
        continue
    pkmn = split_lines[0]
    level = int(split_lines[1])
    if pkmn in ['unown', 'ditto']:
        moves = [split_lines[2]]
        ability = split_lines[3]
        item = split_lines[4]
    else:
        moves = split_lines[2:6]
        ability = split_lines[6]
        item = split_lines[7]

    if item.endswith("ite") and item != "eviolite":
        pkmn = pkmn + "mega"
        ability = normalize_name(pokedex[pkmn]["most_likely_ability"])
    elif item.endswith("itex"):
        pkmn = pkmn + "megax"
        ability = normalize_name(pokedex[pkmn]["most_likely_ability"])
    elif item.endswith("itey"):
        pkmn = pkmn + "megay"
        ability = normalize_name(pokedex[pkmn]["most_likely_ability"])

    identifier = "{}".format(pkmn)
    if identifier in all_pokemon_dict:
        all_pokemon_dict[identifier][constants.COUNT] += 1
    else:
        all_pokemon_dict[identifier] = {constants.SETS: dict(), constants.MOVES: dict(), constants.ABILITIES: dict(), constants.ITEMS: dict(), constants.COUNT: 1}

    this_pkmn_dict = all_pokemon_dict[identifier]
    for i, m in enumerate(moves[:]):
        if m == 'return':
            m = 'return102'
            moves[i] = 'return102'
        add_thing_to_dict_or_increment(this_pkmn_dict, constants.MOVES, m)

    this_set = "|".join(sorted(moves))  # + "|" + ability + "|" + item

    moves_identifier = "|".join(sorted(moves))

    add_thing_to_dict_or_increment(this_pkmn_dict, constants.ABILITIES, ability)
    add_thing_to_dict_or_increment(this_pkmn_dict, constants.ITEMS, item)
    add_thing_to_dict_or_increment(this_pkmn_dict, constants.SETS, this_set)


with open("out.json", 'w') as f:
    json.dump(all_pokemon_dict, f, indent=4, sort_keys=True)
