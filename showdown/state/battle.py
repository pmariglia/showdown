import constants
from config import logger
from copy import copy
from data.parse_smogon_stats import get_smogon_stats_file_name
from data.parse_smogon_stats import get_pokemon_information
from data.parse_smogon_stats import moves_string
from data.parse_smogon_stats import spreads_string
from data.parse_smogon_stats import ability_string
from data.parse_smogon_stats import item_string
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

        self.time_remaining = 240

    def initialize_team_preview(self, user_json, opponent_pokemon, battle_mode):
        self.user.from_json(user_json, first_turn=True)
        self.user.reserve.insert(0, self.user.active)
        self.user.active = None

        if any(battle_mode.endswith(s) for s in constants.SMOGON_HAS_STATS_PAGE_SUFFIXES):
            smogon_stats_file_name = get_smogon_stats_file_name(battle_mode)
            logger.debug("Making HTTP request to {} for usage stats".format(smogon_stats_file_name))
            smogon_usage_data = get_pokemon_information(smogon_stats_file_name)
        else:
            # use ALL data for a mode like battle-factory
            logger.debug("Making HTTP request for ALL usage stats\nplease wait...")
            ou_data = get_pokemon_information(get_smogon_stats_file_name("gen7ou"))
            uu_data = get_pokemon_information(get_smogon_stats_file_name("gen7uu"))
            ru_data = get_pokemon_information(get_smogon_stats_file_name("gen7ru"))
            nu_data = get_pokemon_information(get_smogon_stats_file_name("gen7nu"))
            pu_data = get_pokemon_information(get_smogon_stats_file_name("gen7pu"))
            lc_data = get_pokemon_information(get_smogon_stats_file_name("gen7lc"))

            smogon_usage_data = ou_data
            for pkmn_data in [uu_data, ru_data, nu_data, pu_data, lc_data]:
                for pkmn_name in pkmn_data:
                    if pkmn_name not in smogon_usage_data:
                        smogon_usage_data[pkmn_name] = pkmn_data[pkmn_name]

        for pkmn_string in opponent_pokemon:
            pokemon = Pokemon.from_switch_string(pkmn_string)
            try:
                nature, evs = smogon_usage_data[pokemon.name][spreads_string][0]
                logger.debug("Spread assumption for {}: {}, {}".format(pokemon.name, nature, evs))
            except (KeyError, ValueError, IndexError):
                nature, evs = 'serious', "85,85,85,85,85,85"
                logger.debug("No spreads found for {}, using random-battle spreads".format(pokemon.name))
            pokemon.set_spread(nature, evs)

            try:
                item = smogon_usage_data[pokemon.name][item_string][0]
                pokemon.item = item
                logger.debug("Item assumption for {}: {}".format(pokemon.name, item))
            except (KeyError, ValueError, IndexError):
                logger.debug("No item found for {}".format(pokemon.name))

            try:
                moves = smogon_usage_data[pokemon.name][moves_string][:4]
                logger.debug("Moves assumption for {}: {}".format(pokemon.name, moves))
                for m in moves:
                    if constants.HIDDEN_POWER in m:
                        m = "{}{}".format(m, constants.HIDDEN_POWER_ACTIVE_MOVE_BASE_DAMAGE_STRING)
                    pokemon.add_move(m)
            except (KeyError, ValueError, IndexError):
                logger.debug("No moves found for {}".format(pokemon.name))

            try:
                ability = smogon_usage_data[pokemon.name][ability_string][0]
                logger.debug("Ability assumption for {}: {}".format(pokemon.name, ability))
                pokemon.ability = ability
            except (KeyError, ValueError, IndexError):
                logger.debug("No ability found for {}".format(pokemon.name))

            self.opponent.reserve.append(pokemon)

        # ensure this gets garbage collected
        del smogon_usage_data

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

        state = State(user, opponent, self.weather, self.field, self.trick_room, self.force_switch, self.wait)
        return state
