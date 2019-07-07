import constants
from copy import copy

import data
from data.helpers import get_standard_battle_sets

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
        self.trick_room = False

        self.started = False
        self.rqid = None

        self.force_switch = False
        self.wait = False

        self.battle_type = None

        self.time_remaining = 240

    def initialize_team_preview(self, user_json, opponent_pokemon, battle_mode):
        self.user.from_json(user_json, first_turn=True)
        self.user.reserve.insert(0, self.user.active)
        self.user.active = None

        for pkmn_string in opponent_pokemon:
            pokemon = Pokemon.from_switch_string(pkmn_string)
            self.opponent.reserve.append(pokemon)

        smogon_usage_data = get_standard_battle_sets(battle_mode)
        data.standard_battle_sets = smogon_usage_data

        self.started = True
        self.rqid = user_json[constants.RQID]

    def start_random_battle(self, user_json, opponent_switch_string):
        self.user.from_json(user_json, first_turn=True)

        pkmn_information = opponent_switch_string.split('|')[3]
        pkmn = Pokemon.from_switch_string(pkmn_information)
        self.opponent.active = pkmn

        self.started = True
        self.rqid = user_json[constants.RQID]

    def prepare_random_battle(self):
        self.opponent.active.guess_random_battle_attributes()
        for pkmn in filter(lambda x: x.is_alive(), self.opponent.reserve):
            pkmn.guess_random_battle_attributes()

    def prepare_standard_battle(self):
        self.opponent.active.guess_standard_battle_attributes()
        for pkmn in filter(lambda x: x.is_alive(), self.opponent.reserve):
            pkmn.guess_standard_battle_attributes()

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

        state = State(user, opponent, self.weather, self.field, self.trick_room, self.force_switch, self.wait)
        return state
