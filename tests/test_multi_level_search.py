import unittest
from unittest import mock

import constants

from collections import defaultdict
from showdown.search.select_best_move import get_move_combination_scores
from showdown.decide.decide import decide_random_from_average_and_safest
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
        safest = decide_random_from_average_and_safest(scores)

        self.assertEqual(move_string, safest)

    def test_double_pokemon_faint_with_opponent_options_remaining_results_in_a_decision(self):

        state_dict = {'self': {'active': {'id': 'talonflame', 'level': 78, 'hp': 0, 'maxhp': 250, 'ability': 'galewings', 'item': None, 'baseStats': {'hp': 78, 'attack': 81, 'defense': 71, 'special-attack': 74, 'special-defense': 69, 'speed': 126}, 'attack': 171, 'defense': 156, 'special-attack': 161, 'special-defense': 153, 'speed': 242, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [], 'types': ['fire', 'flying'], 'canMegaEvo': False}, 'reserve': {'xerneas': {'id': 'xerneas', 'level': 73, 'hp': 0, 'maxhp': 304, 'ability': 'fairyaura', 'item': None, 'baseStats': {'hp': 126, 'attack': 131, 'defense': 95, 'special-attack': 131, 'special-defense': 98, 'speed': 99}, 'attack': 234, 'defense': 181, 'special-attack': 234, 'special-defense': 186, 'speed': 187, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'thunderbolt', 'disabled': False, 'current_pp': 24}, {'id': 'geomancy', 'disabled': False, 'current_pp': 16}, {'id': 'moonblast', 'disabled': False, 'current_pp': 24}, {'id': 'hiddenpowerfire60', 'disabled': False, 'current_pp': 24}], 'types': ['fairy'], 'canMegaEvo': False}, 'golurk': {'id': 'golurk', 'level': 83, 'hp': 283, 'maxhp': 283, 'ability': 'ironfist', 'item': None, 'baseStats': {'hp': 89, 'attack': 124, 'defense': 80, 'special-attack': 55, 'special-defense': 80, 'speed': 55}, 'attack': 254, 'defense': 180, 'special-attack': 139, 'special-defense': 180, 'speed': 139, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'rockpolish', 'disabled': False, 'current_pp': 32}, {'id': 'earthquake', 'disabled': False, 'current_pp': 16}, {'id': 'icepunch', 'disabled': False, 'current_pp': 24}, {'id': 'shadowpunch', 'disabled': False, 'current_pp': 32}], 'types': ['ground', 'ghost'], 'canMegaEvo': False}, 'kingler': {'id': 'kingler', 'level': 81, 'hp': 222, 'maxhp': 222, 'ability': 'sheerforce', 'item': None, 'baseStats': {'hp': 55, 'attack': 130, 'defense': 115, 'special-attack': 50, 'special-defense': 50, 'speed': 75}, 'attack': 257, 'defense': 233, 'special-attack': 128, 'special-defense': 128, 'speed': 168, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'liquidation', 'disabled': False, 'current_pp': 16}, {'id': 'knockoff', 'disabled': False, 'current_pp': 32}, {'id': 'superpower', 'disabled': False, 'current_pp': 8}, {'id': 'rockslide', 'disabled': False, 'current_pp': 16}], 'types': ['water'], 'canMegaEvo': False}, 'escavalier': {'id': 'escavalier', 'level': 79, 'hp': 240, 'maxhp': 240, 'ability': 'swarm', 'item': None, 'baseStats': {'hp': 70, 'attack': 135, 'defense': 105, 'special-attack': 60, 'special-defense': 105, 'speed': 20}, 'attack': 259, 'defense': 211, 'special-attack': 140, 'special-defense': 211, 'speed': 77, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'megahorn', 'disabled': False, 'current_pp': 16}, {'id': 'ironhead', 'disabled': False, 'current_pp': 24}, {'id': 'drillrun', 'disabled': False, 'current_pp': 16}, {'id': 'pursuit', 'disabled': False, 'current_pp': 32}], 'types': ['bug', 'steel'], 'canMegaEvo': False}, 'altaria': {'id': 'altaria', 'level': 77, 'hp': 242, 'maxhp': 242, 'ability': 'naturalcure', 'item': None, 'baseStats': {'hp': 75, 'attack': 70, 'defense': 90, 'special-attack': 70, 'special-defense': 105, 'speed': 80}, 'attack': 152, 'defense': 183, 'special-attack': 152, 'special-defense': 206, 'speed': 168, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'earthquake', 'disabled': False, 'current_pp': 16}, {'id': 'return', 'disabled': False, 'current_pp': 32}, {'id': 'roost', 'disabled': False, 'current_pp': 16}, {'id': 'dracometeor', 'disabled': False, 'current_pp': 8}], 'types': ['dragon', 'flying'], 'canMegaEvo': False}}, 'side_conditions': {'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0, 'stealthrock': 0, 'spikes': 0, 'stickyweb': 0, 'toxicspikes': 0}, 'trapped': False}, 'opponent': {'active': {'id': 'rotomfrost', 'level': 83, 'hp': 0, 'maxhp': 219, 'ability': 'levitate', 'item': 'Life Orb', 'baseStats': {'hp': 50, 'attack': 65, 'defense': 107, 'special-attack': 105, 'special-defense': 107, 'speed': 86}, 'attack': 156, 'defense': 225, 'special-attack': 222, 'special-defense': 225, 'speed': 190, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'blizzard', 'disabled': False, 'current_pp': 8}, {'id': 'thunderbolt', 'disabled': False, 'current_pp': 24}], 'types': ['electric', 'ice'], 'canMegaEvo': False}, 'reserve': {'audinomega': {'id': 'audinomega', 'level': 81, 'hp': 0, 'maxhp': 299, 'ability': 'healer', 'item': None, 'baseStats': {'hp': 103, 'attack': 60, 'defense': 126, 'special-attack': 80, 'special-defense': 126, 'speed': 50}, 'attack': 144, 'defense': 251, 'special-attack': 176, 'special-defense': 251, 'speed': 128, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'dazzlinggleam', 'disabled': False, 'current_pp': 16}], 'types': ['normal', 'fairy'], 'canMegaEvo': False}}, 'side_conditions': {'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0, 'Wish': 0}, 'trapped': False}, 'weather': None, 'field': None, 'forceSwitch': True, 'wait': False}
        self.state = State.from_dict(state_dict)
        self.mutator = StateMutator(self.state)

        scores = get_move_combination_scores(self.mutator, 2)
        safest = decide_random_from_average_and_safest(scores)

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
                # this boosting move will allow a guaranteed ko on move # 2
                'id': move_string,
                'disabled': False,
                'current_pp': 16
            }
        ]
        self.state.opponent.active.moves = [
            {
                # this boosting move will allow a guaranteed ko on move # 2
                'id': move_string,
                'disabled': False,
                'current_pp': 16
            }
        ]

        scores = get_move_combination_scores(self.mutator, 2)
        safest = decide_random_from_average_and_safest(scores)

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
                # this boosting move will allow a guaranteed ko on move # 2
                'id': move_string,
                'disabled': False,
                'current_pp': 16
            }
        ]
        self.state.opponent.active.moves = [
            {
                # this boosting move will allow a guaranteed ko on move # 2
                'id': move_string,
                'disabled': False,
                'current_pp': 16
            }
        ]

        scores = get_move_combination_scores(self.mutator, 2)
        safest = decide_random_from_average_and_safest(scores)

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
        safest = decide_random_from_average_and_safest(scores)

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
        safest = decide_random_from_average_and_safest(scores)

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
        safest = decide_random_from_average_and_safest(scores)

        # assert that levitate causes return to be the better move
        self.assertEqual("return", safest)


if __name__ == '__main__':
    unittest.main()
