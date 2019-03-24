from collections import defaultdict
from showdown.search.select_best_move import get_move_combination_scores
from showdown.search.objects import State
from showdown.search.objects import Side
from showdown.state.pokemon import Pokemon as StatePokemon
from showdown.search.objects import Pokemon
from showdown.search.state_mutator import StateMutator


from config import logger
import logging

logger.setLevel(logging.CRITICAL)


state = State(
    Side(
        Pokemon.from_state_pokemon_dict(StatePokemon("raichu", 73).to_dict()),
        {
            "xatu": Pokemon.from_state_pokemon_dict(StatePokemon("xatu", 81).to_dict()),
            "starmie": Pokemon.from_state_pokemon_dict(StatePokemon("starmie", 81).to_dict()),
            "gyarados": Pokemon.from_state_pokemon_dict(StatePokemon("gyarados", 81).to_dict()),
            "dragonite": Pokemon.from_state_pokemon_dict(StatePokemon("dragonite", 81).to_dict()),
            "hitmonlee": Pokemon.from_state_pokemon_dict(StatePokemon("hitmonlee", 81).to_dict()),
        },
        defaultdict(lambda: 0),
        False
    ),
    Side(
        Pokemon.from_state_pokemon_dict(StatePokemon("aromatisse", 81).to_dict()),
        {
            "yveltal": Pokemon.from_state_pokemon_dict(StatePokemon("yveltal", 73).to_dict()),
            "slurpuff": Pokemon.from_state_pokemon_dict(StatePokemon("slurpuff", 73).to_dict()),
            "victini": Pokemon.from_state_pokemon_dict(StatePokemon("victini", 73).to_dict()),
            "toxapex": Pokemon.from_state_pokemon_dict(StatePokemon("toxapex", 73).to_dict()),
            "bronzong": Pokemon.from_state_pokemon_dict(StatePokemon("bronzong", 73).to_dict()),
        },
        defaultdict(lambda: 0),
        False
    ),
    None,
    None,
    False,
    False
)


state.self.active.moves = [
    {
        "id": "thunderbolt",
        "disabled": False
    },
    {
        "id": "surf",
        "disabled": False
    },
    {
        "id": "nastyplot",
        "disabled": False
    },
    {
        "id": "substitute",
        "disabled": False
    },
]

mutator = StateMutator(state)
state_instructions = get_move_combination_scores(mutator, depth=3)
