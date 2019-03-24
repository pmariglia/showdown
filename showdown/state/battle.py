import constants
from copy import copy
from data import get_spread
from showdown.state.battler import Battler
from showdown.state.pokemon import Pokemon
from showdown.search.objects import State
from showdown.search.objects import Side
from showdown.search.objects import Pokemon as TransposePokemon


class Battle:

    def __init__(self, battle_tag):
        self.battle_tag = battle_tag
        self.user = Battler()
        self.opponent = Battler()
        self.weather = None
        self.field = None

        self.started = False
        self.rqid = None

        self.force_switch = False
        self.wait = False

    def initialize_team_preview(self, user_json, opponent_pokemon):
        self.user.from_json(user_json, first_turn=True)
        self.user.reserve.insert(0, self.user.active)
        self.user.active = None
        for pkmn_string in opponent_pokemon:
            pokemon = Pokemon.from_switch_string(pkmn_string)
            nature, evs = get_spread(pokemon.name)
            pokemon.set_spread(nature, evs)
            self.opponent.reserve.append(pokemon)

        self.started = True
        self.rqid = user_json[constants.RQID]

    def start_random_battle(self, user_json, opponent_switch_string):
        self.user.from_json(user_json, first_turn=True)

        pkmn_information = opponent_switch_string.split('|')[3]
        pkmn = Pokemon.from_switch_string(pkmn_information)
        self.opponent.active = pkmn

        self.started = True
        self.rqid = user_json[constants.RQID]

    def to_object(self):
        if not self.started:
            raise ValueError("Battle needs to be started first")

        user_active = TransposePokemon.from_state_pokemon_dict(self.user.active.to_dict())
        user_reserve = dict()
        for mon in self.user.reserve:
            user_reserve[mon.name] = TransposePokemon.from_state_pokemon_dict(mon.to_dict())

        opponent_active = TransposePokemon.from_state_pokemon_dict(self.opponent.active.to_dict())
        opponent_reserve = dict()
        for mon in self.opponent.reserve:
            opponent_reserve[mon.name] = TransposePokemon.from_state_pokemon_dict(mon.to_dict())

        user = Side(user_active, user_reserve, copy(self.user.side_conditions), self.user.trapped)
        opponent = Side(opponent_active, opponent_reserve, copy(self.opponent.side_conditions), self.opponent.trapped)

        state = State(user, opponent, self.weather, self.field, self.force_switch, self.wait)
        return state
