import json
import logging
from importlib import resources as impresources
from sim import resources

base = impresources.files(resources)

logger = logging.getLogger(__name__)

move_json_location = base / "moves.json"
with move_json_location.open("rt") as f:
    all_move_json = json.load(f)

pkmn_json_location = base / "pokedex.json"
with pkmn_json_location.open("rt") as f:
    pokedex = json.loads(f.read())

random_battle_set_location = base / "random_battle_sets.json"
with random_battle_set_location.open("rt") as f:
    random_battle_sets = json.load(f)


pokemon_sets = random_battle_sets
effectiveness = {}
team_datasets = None
