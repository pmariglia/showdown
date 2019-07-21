import unittest
from unittest import mock

import constants

from collections import defaultdict
from showdown.search.select_best_move import get_move_combination_scores
from showdown.decide.decide import decide_from_safest
from showdown.search import select_best_move
from showdown.search.objects import State
from showdown.search.objects import Side
from showdown.state.pokemon import Pokemon as StatePokemon
from showdown.search.objects import Pokemon
from showdown.search.state_mutator import StateMutator


class TestSelectBestMove(unittest.TestCase):
    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                dict(),
                defaultdict(lambda: 0),
                False
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("aromatisse", 81).to_dict()),
                dict(),
                defaultdict(lambda: 0),
                False
            ),
            None,
            None,
            False,
            False,
            False
        )

        self.state.self.active.hp = 100
        self.state.self.active.maxhp = 100
        self.state.self.active.attack = 100
        self.state.self.active.defense = 100
        self.state.self.active.special_attack = 100
        self.state.self.active.special_defense = 100
        self.state.self.active.speed = 99
        self.state.self.active.moves = [
            {
                'id': 'return',
                'disabled': False,
                'current_pp': 16
            }
        ]
        self.state.opponent.active.hp = 100
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.attack = 100
        self.state.opponent.active.defense = 100
        self.state.opponent.active.special_attack = 100
        self.state.opponent.active.special_defense = 100
        self.state.opponent.active.speed = 100
        self.state.opponent.active.moves = [
            {
                'id': 'return',
                'disabled': False,
                'current_pp': 16
            }
        ]
        self.mutator = StateMutator(self.state)

    def test_two_level_search_always_boosts_when_kill_is_guaranteed(self):
        """The state is set up such that each pokemon has 100 HP and RETURN will do 85 damage

           This test asserts that when the bot is given the option to dragon-dance and guarantee a
           kill on turn #2, it goes for it"""

        # ensure that the opposing pokemon has no moves from the data lookup
        select_best_move.get_move_set = mock.MagicMock(return_value=set())

        move_string = 'dragondance'
        self.state.self.active.moves.append(
            {
                # this boosting move will allow a guaranteed ko on move # 2
                'id': move_string,
                'disabled': False,
                'current_pp': 16
            }
        )

        scores = get_move_combination_scores(self.mutator, 2)
        safest = decide_from_safest(scores)

        self.assertEqual(move_string, safest)

    def test_double_pokemon_faint_with_opponent_options_remaining_results_in_a_decision(self):

        state_dict = {'self': {'active': {'id': 'talonflame', 'level': 78, 'hp': 0, 'maxhp': 250, 'ability': 'galewings', 'item': None, 'baseStats': {'hp': 78, 'attack': 81, 'defense': 71, 'special-attack': 74, 'special-defense': 69, 'speed': 126}, 'attack': 171, 'defense': 156, 'special-attack': 161, 'special-defense': 153, 'speed': 242, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [], 'types': ['fire', 'flying'], 'canMegaEvo': False}, 'reserve': {'xerneas': {'id': 'xerneas', 'level': 73, 'hp': 0, 'maxhp': 304, 'ability': 'fairyaura', 'item': None, 'baseStats': {'hp': 126, 'attack': 131, 'defense': 95, 'special-attack': 131, 'special-defense': 98, 'speed': 99}, 'attack': 234, 'defense': 181, 'special-attack': 234, 'special-defense': 186, 'speed': 187, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'thunderbolt', 'disabled': False, 'current_pp': 24}, {'id': 'geomancy', 'disabled': False, 'current_pp': 16}, {'id': 'moonblast', 'disabled': False, 'current_pp': 24}, {'id': 'hiddenpowerfire60', 'disabled': False, 'current_pp': 24}], 'types': ['fairy'], 'canMegaEvo': False}, 'golurk': {'id': 'golurk', 'level': 83, 'hp': 283, 'maxhp': 283, 'ability': 'ironfist', 'item': None, 'baseStats': {'hp': 89, 'attack': 124, 'defense': 80, 'special-attack': 55, 'special-defense': 80, 'speed': 55}, 'attack': 254, 'defense': 180, 'special-attack': 139, 'special-defense': 180, 'speed': 139, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'rockpolish', 'disabled': False, 'current_pp': 32}, {'id': 'earthquake', 'disabled': False, 'current_pp': 16}, {'id': 'icepunch', 'disabled': False, 'current_pp': 24}, {'id': 'shadowpunch', 'disabled': False, 'current_pp': 32}], 'types': ['ground', 'ghost'], 'canMegaEvo': False}, 'kingler': {'id': 'kingler', 'level': 81, 'hp': 222, 'maxhp': 222, 'ability': 'sheerforce', 'item': None, 'baseStats': {'hp': 55, 'attack': 130, 'defense': 115, 'special-attack': 50, 'special-defense': 50, 'speed': 75}, 'attack': 257, 'defense': 233, 'special-attack': 128, 'special-defense': 128, 'speed': 168, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'liquidation', 'disabled': False, 'current_pp': 16}, {'id': 'knockoff', 'disabled': False, 'current_pp': 32}, {'id': 'superpower', 'disabled': False, 'current_pp': 8}, {'id': 'rockslide', 'disabled': False, 'current_pp': 16}], 'types': ['water'], 'canMegaEvo': False}, 'escavalier': {'id': 'escavalier', 'level': 79, 'hp': 240, 'maxhp': 240, 'ability': 'swarm', 'item': None, 'baseStats': {'hp': 70, 'attack': 135, 'defense': 105, 'special-attack': 60, 'special-defense': 105, 'speed': 20}, 'attack': 259, 'defense': 211, 'special-attack': 140, 'special-defense': 211, 'speed': 77, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'megahorn', 'disabled': False, 'current_pp': 16}, {'id': 'ironhead', 'disabled': False, 'current_pp': 24}, {'id': 'drillrun', 'disabled': False, 'current_pp': 16}, {'id': 'pursuit', 'disabled': False, 'current_pp': 32}], 'types': ['bug', 'steel'], 'canMegaEvo': False}, 'altaria': {'id': 'altaria', 'level': 77, 'hp': 242, 'maxhp': 242, 'ability': 'naturalcure', 'item': None, 'baseStats': {'hp': 75, 'attack': 70, 'defense': 90, 'special-attack': 70, 'special-defense': 105, 'speed': 80}, 'attack': 152, 'defense': 183, 'special-attack': 152, 'special-defense': 206, 'speed': 168, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'earthquake', 'disabled': False, 'current_pp': 16}, {'id': 'return', 'disabled': False, 'current_pp': 32}, {'id': 'roost', 'disabled': False, 'current_pp': 16}, {'id': 'dracometeor', 'disabled': False, 'current_pp': 8}], 'types': ['dragon', 'flying'], 'canMegaEvo': False}}, 'side_conditions': {'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0, 'stealthrock': 0, 'spikes': 0, 'stickyweb': 0, 'toxicspikes': 0}, 'trapped': False}, 'opponent': {'active': {'id': 'rotomfrost', 'level': 83, 'hp': 0, 'maxhp': 219, 'ability': 'levitate', 'item': 'Life Orb', 'baseStats': {'hp': 50, 'attack': 65, 'defense': 107, 'special-attack': 105, 'special-defense': 107, 'speed': 86}, 'attack': 156, 'defense': 225, 'special-attack': 222, 'special-defense': 225, 'speed': 190, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'blizzard', 'disabled': False, 'current_pp': 8}, {'id': 'thunderbolt', 'disabled': False, 'current_pp': 24}], 'types': ['electric', 'ice'], 'canMegaEvo': False}, 'reserve': {'audinomega': {'id': 'audinomega', 'level': 81, 'hp': 0, 'maxhp': 299, 'ability': 'healer', 'item': None, 'baseStats': {'hp': 103, 'attack': 60, 'defense': 126, 'special-attack': 80, 'special-defense': 126, 'speed': 50}, 'attack': 144, 'defense': 251, 'special-attack': 176, 'special-defense': 251, 'speed': 128, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'dazzlinggleam', 'disabled': False, 'current_pp': 16}], 'types': ['normal', 'fairy'], 'canMegaEvo': False}}, 'side_conditions': {'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0, 'Wish': 0}, 'trapped': False}, 'weather': None, 'field': None, 'forceSwitch': True, 'wait': False, 'trickroom': False}
        self.state = State.from_dict(state_dict)
        self.mutator = StateMutator(self.state)

        scores = get_move_combination_scores(self.mutator, 2)
        safest = decide_from_safest(scores)

        self.assertTrue(safest.startswith(constants.SWITCH_STRING))

    def test_battle_ending_stops_the_calculations_early(self):

        self.state.self.reserve = {
            'caterpie': Pokemon.from_state_pokemon_dict(StatePokemon("caterpie", 100).to_dict()),
            'weedle': Pokemon.from_state_pokemon_dict(StatePokemon("weedle", 100).to_dict()),
            'pidgey': Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict()),
            'rattata': Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
            'metapod': Pokemon.from_state_pokemon_dict(StatePokemon("metapod", 100).to_dict()),
        }
        for pkmn in self.state.self.reserve.values():
            pkmn.hp = 0

        self.state.opponent.reserve = {
            'caterpie': Pokemon.from_state_pokemon_dict(StatePokemon("caterpie", 100).to_dict()),
            'weedle': Pokemon.from_state_pokemon_dict(StatePokemon("weedle", 100).to_dict()),
            'pidgey': Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict()),
            'rattata': Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
            'metapod': Pokemon.from_state_pokemon_dict(StatePokemon("metapod", 100).to_dict()),
        }
        for pkmn in self.state.opponent.reserve.values():
            pkmn.hp = 0

        self.state.self.active.speed = 100
        self.state.opponent.active.speed = 99

        # opponent is 1-hit ko
        self.state.opponent.active.hp = 1

        # ensure that the opposing pokemon has no moves from the data lookup
        select_best_move.get_move_set = mock.MagicMock(return_value=set())

        move_string = 'tackle'
        self.state.self.active.moves = [
            {
                'id': move_string,
                'disabled': False,
                'current_pp': 16
            }
        ]
        self.state.opponent.active.moves = [
            {
                'id': move_string,
                'disabled': False,
                'current_pp': 16
            }
        ]

        scores = get_move_combination_scores(self.mutator, 2)
        safest = decide_from_safest(scores)

        self.assertEqual(move_string, safest)

    def test_fainted_opponent_without_seeing_reserves_results_in_valid_move(self):

        self.state.self.reserve = {
            'caterpie': Pokemon.from_state_pokemon_dict(StatePokemon("caterpie", 100).to_dict()),
            'weedle': Pokemon.from_state_pokemon_dict(StatePokemon("weedle", 100).to_dict()),
            'pidgey': Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict()),
            'rattata': Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
            'metapod': Pokemon.from_state_pokemon_dict(StatePokemon("metapod", 100).to_dict()),
        }
        for pkmn in self.state.self.reserve.values():
            pkmn.hp = 0

        self.state.opponent.reserve = {}

        self.state.self.active.speed = 100
        self.state.opponent.active.speed = 99

        # opponent is 1-hit ko
        self.state.opponent.active.hp = 1

        # ensure that the opposing pokemon has no moves from the data lookup
        select_best_move.get_move_set = mock.MagicMock(return_value=set())

        move_string = 'tackle'
        self.state.self.active.moves = [
            {
                'id': move_string,
                'disabled': False,
                'current_pp': 16
            }
        ]
        self.state.opponent.active.moves = [
            {
                'id': move_string,
                'disabled': False,
                'current_pp': 16
            }
        ]

        scores = get_move_combination_scores(self.mutator, 2)
        safest = decide_from_safest(scores)

        self.assertEqual(move_string, safest)

    def test_only_way_to_win_is_to_die(self):
        """The Eevee in reserves can OHKO the opponent's active and only pokemon
           However, switching to the Eevee while the opponent attacks will result in a death
           This test asserts that the bot can find the optimal strategy which is to sack the active Pikachu, and win
           on the next turn"""

        # ensure that the opposing pokemon has no moves from the data lookup
        select_best_move.get_move_set = mock.MagicMock(return_value=set())

        # guaranteed switch
        reserve_pkmn = Pokemon.from_state_pokemon_dict(StatePokemon("eevee", 100).to_dict())
        reserve_pkmn.hp = 5
        reserve_pkmn.maxhp = 80
        reserve_pkmn.attack = 100
        reserve_pkmn.defense = 100
        reserve_pkmn.special_attack = 100
        reserve_pkmn.special_defense = 100
        reserve_pkmn.speed = 101
        reserve_pkmn.moves = [
            {
                'id': 'return',
                'disabled': False,
                'current_pp': 16
            }
        ]

        self.state.self.reserve["eevee"] = reserve_pkmn

        # guarantee that the active pokemon will die in 1 hit (provided it is slower, which it should be)
        # 100 ATK return vs 100 Defense should do 85 DMG with no STAB
        self.state.self.active.hp = 5

        # given 3 moves to look ahead, the safest move should be to use return, die, and win on the next turn
        scores = get_move_combination_scores(self.mutator, 3)
        safest = decide_from_safest(scores)

        self.assertEqual("return", safest)

    def test_only_way_to_win_is_to_switch_out_and_free_choice_decision(self):
        """The Blastoise currently in is locked into `Return` via it's Choice-Scarf
           It can OHKO the Golem with `Surf`, but it needs to switch out and sack the Eevee
           This test asserts that with a search depth of 3, the bot can find the guaranteed win
           The winning move is to switch to Eevee, freeing up Surf, sack the Eevee, and come back in with Scarf-Surf"""

        # ensure that the opposing pokemon has no moves from the data lookup
        select_best_move.get_move_set = mock.MagicMock(return_value=set())

        self.state.opponent.active = Pokemon.from_state_pokemon_dict(StatePokemon("golem", 100).to_dict())
        self.state.opponent.active.speed = 100  # opponent is faster than both of our pokemon (without choicescarf)
        self.state.opponent.active.moves = [
            {
                'id': 'return',
                'disabled': False,
                'current_pp': 16
            }
        ]

        # reserve pokemon
        reserve_pkmn = Pokemon.from_state_pokemon_dict(StatePokemon("eevee", 100).to_dict())
        reserve_pkmn.hp = 5
        reserve_pkmn.moves = [
            {
                'id': 'return',
                'disabled': False,
                'current_pp': 16
            }
        ]
        self.state.self.reserve["eevee"] = reserve_pkmn

        self.state.self.active = Pokemon.from_state_pokemon_dict(StatePokemon("blastoise", 100).to_dict())
        self.state.self.active.speed = 99  # slower than Golem without scarf
        self.state.self.active.item = 'choicescarf'
        self.state.self.active.moves = [
            {
                'id': 'return',
                'disabled': False,
                'current_pp': 16
            },
            {
                'id': 'surf',
                'disabled': True,  # surf is disabled
                'current_pp': 16
            }
        ]

        # guarantee that the active Blastoise will die in 1 hit (provided it is slower, which it is)
        self.state.self.active.hp = 5

        # given 3 moves to look ahead, the safest move should be to sack Eevee, switch Blastoise back in,
        # and win on the next turn with Scarf-Surf
        scores = get_move_combination_scores(self.mutator, 3)
        safest = decide_from_safest(scores)

        self.assertEqual("switch eevee", safest)

    def test_only_way_to_win_is_to_not_earthquake_into_levitate(self):
        """This test gives a situation where the bot and the opponent both have one pokemon left
           The bot's pokemon is faster
           Both the bot and the user can KO the other in 2 moves, and neither has a priority move
           This means that the bot should win in 2 moves
           The opponent's type means it is weak to earthquake, but it has the ability levitate
           Earthquake would KO in 1 move, however the opponent is immune
           This test asserts that the non-earthquake move is selected"""

        # ensure that the opposing pokemon has no moves from the data lookup
        select_best_move.get_move_set = mock.MagicMock(return_value=set())

        # give the bot an OHKO move versus the enemy
        self.state.self.active.moves.append(
            {
                "id": "earthquake",
                "disabled": False,
            }
        )

        # make the enemy immune to earthquake
        self.state.opponent.active.ability = "levitate"

        # make the bot faster than the opponent
        self.state.opponent.active.speed = 100
        self.state.self.active.speed = 101

        scores = get_move_combination_scores(self.mutator, 2)
        safest = decide_from_safest(scores)

        # assert that levitate causes return to be the better move
        self.assertEqual("return", safest)

    def test_guaranteed_win_through_an_ability_giving_boosted_speed_on_the_next_move(self):
        """Slurpuff has no item and the ability 'unburden'
           This is a guaranteed win because the Kommo-o has no priority
           Searching two levels should guarantee the win from this switch"""

        self.mutator.state = State.from_dict({'self': {'active': {'id': 'bisharp', 'level': 77, 'hp': 0, 'maxhp': 227, 'ability': 'defiant', 'item': 'focussash', 'baseStats': {'hp': 65, 'attack': 125, 'defense': 100, 'special-attack': 60, 'special-defense': 70, 'speed': 70}, 'attack': 237, 'defense': 199, 'special-attack': 137, 'special-defense': 152, 'speed': 152, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'suckerpunch', 'disabled': False, 'current_pp': 8}, {'id': 'swordsdance', 'disabled': False, 'current_pp': 32}, {'id': 'ironhead', 'disabled': False, 'current_pp': 24}, {'id': 'knockoff', 'disabled': False, 'current_pp': 32}], 'types': ['dark', 'steel'], 'canMegaEvo': False}, 'reserve': {'golduck': {'id': 'golduck', 'level': 84, 'hp': 245, 'maxhp': 272, 'ability': 'cloudnine', 'item': 'lifeorb', 'baseStats': {'hp': 80, 'attack': 82, 'defense': 78, 'special-attack': 95, 'special-defense': 80, 'speed': 85}, 'attack': 186, 'defense': 179, 'special-attack': 208, 'special-defense': 183, 'speed': 191, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': 'slp', 'volatileStatus': [], 'moves': [{'id': 'scald', 'disabled': False, 'current_pp': 24}, {'id': 'encore', 'disabled': False, 'current_pp': 8}, {'id': 'psyshock', 'disabled': False, 'current_pp': 16}, {'id': 'icebeam', 'disabled': False, 'current_pp': 16}], 'types': ['water'], 'canMegaEvo': False}, 'donphan': {'id': 'donphan', 'level': 79, 'hp': 57, 'maxhp': 272, 'ability': 'sturdy', 'item': 'leftovers', 'baseStats': {'hp': 90, 'attack': 120, 'defense': 120, 'special-attack': 60, 'special-defense': 60, 'speed': 50}, 'attack': 235, 'defense': 235, 'special-attack': 140, 'special-defense': 140, 'speed': 125, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'stealthrock', 'disabled': False, 'current_pp': 32}, {'id': 'rapidspin', 'disabled': False, 'current_pp': 64}, {'id': 'iceshard', 'disabled': False, 'current_pp': 48}, {'id': 'earthquake', 'disabled': False, 'current_pp': 16}], 'types': ['ground'], 'canMegaEvo': False}, 'slurpuff': {'id': 'slurpuff', 'level': 80, 'hp': 127, 'maxhp': 262, 'ability': 'unburden', 'item': '', 'baseStats': {'hp': 82, 'attack': 80, 'defense': 86, 'special-attack': 85, 'special-defense': 75, 'speed': 72}, 'attack': 174, 'defense': 184, 'special-attack': 182, 'special-defense': 166, 'speed': 161, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'dazzlinggleam', 'disabled': False, 'current_pp': 16}, {'id': 'calmmind', 'disabled': False, 'current_pp': 32}, {'id': 'surf', 'disabled': False, 'current_pp': 24}, {'id': 'flamethrower', 'disabled': False, 'current_pp': 24}], 'types': ['fairy'], 'canMegaEvo': False}, 'kingdra': {'id': 'kingdra', 'level': 80, 'hp': 0, 'maxhp': 251, 'ability': 'swiftswim', 'item': 'damprock', 'baseStats': {'hp': 75, 'attack': 95, 'defense': 95, 'special-attack': 95, 'special-defense': 95, 'speed': 85}, 'attack': 198, 'defense': 198, 'special-attack': 198, 'special-defense': 198, 'speed': 182, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'outrage', 'disabled': False, 'current_pp': 16}, {'id': 'dragondance', 'disabled': False, 'current_pp': 32}, {'id': 'waterfall', 'disabled': False, 'current_pp': 24}, {'id': 'raindance', 'disabled': False, 'current_pp': 8}], 'types': ['water', 'dragon'], 'canMegaEvo': False}, 'grumpig': {'id': 'grumpig', 'level': 84, 'hp': 0, 'maxhp': 272, 'ability': 'thickfat', 'item': 'leftovers', 'baseStats': {'hp': 80, 'attack': 45, 'defense': 65, 'special-attack': 90, 'special-defense': 110, 'speed': 80}, 'attack': 124, 'defense': 157, 'special-attack': 199, 'special-defense': 233, 'speed': 183, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'whirlwind', 'disabled': False, 'current_pp': 32}, {'id': 'toxic', 'disabled': False, 'current_pp': 16}, {'id': 'reflect', 'disabled': False, 'current_pp': 32}, {'id': 'psychic', 'disabled': False, 'current_pp': 16}], 'types': ['psychic'], 'canMegaEvo': False}}, 'side_conditions': {'toxic_count': 0, 'stealthrock': 1}, 'trapped': False}, 'opponent': {'active': {'id': 'kommoo', 'level': 77, 'hp': 242, 'maxhp': 242, 'ability': 'bulletproof', 'item': 'unknown', 'baseStats': {'hp': 75, 'attack': 110, 'defense': 125, 'special-attack': 100, 'special-defense': 105, 'speed': 85}, 'attack': 214, 'defense': 237, 'special-attack': 199, 'special-defense': 206, 'speed': 175, 'attack_boost': 0, 'defense_boost': -1, 'special_attack_boost': 0, 'special_defense_boost': -1, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'closecombat', 'disabled': False, 'current_pp': 8}], 'types': ['dragon', 'fighting'], 'canMegaEvo': False}, 'reserve': {'torkoal': {'id': 'torkoal', 'level': 84, 'hp': 0, 'maxhp': 255, 'ability': 'drought', 'item': 'unknown', 'baseStats': {'hp': 70, 'attack': 85, 'defense': 140, 'special-attack': 85, 'special-defense': 70, 'speed': 20}, 'attack': 191, 'defense': 283, 'special-attack': 191, 'special-defense': 166, 'speed': 82, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'yawn', 'disabled': False, 'current_pp': 16}], 'types': ['fire'], 'canMegaEvo': False}, 'heracrossmega': {'id': 'heracrossmega', 'level': 76, 'hp': 0, 'maxhp': 247, 'ability': 'skilllink', 'item': 'unknown', 'baseStats': {'hp': 80, 'attack': 185, 'defense': 115, 'special-attack': 40, 'special-defense': 105, 'speed': 75}, 'attack': 325, 'defense': 219, 'special-attack': 105, 'special-defense': 204, 'speed': 158, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'swordsdance', 'disabled': False, 'current_pp': 32}, {'id': 'closecombat', 'disabled': False, 'current_pp': 8}], 'types': ['bug', 'fighting'], 'canMegaEvo': False}, 'zebstrika': {'id': 'zebstrika', 'level': 84, 'hp': 0, 'maxhp': 263, 'ability': 'lightningrod', 'item': 'unknown', 'baseStats': {'hp': 75, 'attack': 100, 'defense': 63, 'special-attack': 80, 'special-defense': 63, 'speed': 116}, 'attack': 216, 'defense': 154, 'special-attack': 183, 'special-defense': 154, 'speed': 243, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'hiddenpower', 'disabled': False, 'current_pp': 24}], 'types': ['electric'], 'canMegaEvo': False}, 'heatran': {'id': 'heatran', 'level': 75, 'hp': 0, 'maxhp': 260, 'ability': 'flashfire', 'item': None, 'baseStats': {'hp': 91, 'attack': 90, 'defense': 106, 'special-attack': 130, 'special-defense': 106, 'speed': 77}, 'attack': 179, 'defense': 203, 'special-attack': 239, 'special-defense': 203, 'speed': 159, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'fireblast', 'disabled': False, 'current_pp': 8}, {'id': 'stealthrock', 'disabled': False, 'current_pp': 32}], 'types': ['fire', 'steel'], 'canMegaEvo': False}, 'gardevoir': {'id': 'gardevoir', 'level': 79, 'hp': 0, 'maxhp': 237, 'ability': 'swiftswim', 'item': 'unknown', 'baseStats': {'hp': 68, 'attack': 65, 'defense': 65, 'special-attack': 125, 'special-defense': 115, 'speed': 80}, 'attack': 148, 'defense': 148, 'special-attack': 243, 'special-defense': 227, 'speed': 172, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': 'tox', 'volatileStatus': [], 'moves': [{'id': 'shadowball', 'disabled': False, 'current_pp': 24}], 'types': ['psychic', 'fairy'], 'canMegaEvo': False}}, 'side_conditions': {'toxic_count': 0}, 'trapped': False}, 'weather': 'none', 'field': None, 'forceSwitch': True, 'wait': False, 'trickroom': False})

        scores = get_move_combination_scores(self.mutator, 2)
        safest = decide_from_safest(scores)

        self.assertEqual("switch slurpuff", safest)


if __name__ == '__main__':
    unittest.main()
