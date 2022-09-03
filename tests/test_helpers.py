import unittest

from showdown.battle import Move
from showdown.engine.helpers import get_pokemon_info_from_condition
from showdown.engine.helpers import normalize_name
from showdown.engine.helpers import set_makes_sense
from showdown.engine.helpers import spreads_are_alike
from showdown.engine.helpers import remove_duplicate_spreads
from showdown.engine.objects import State


class TestBattleIsOver(unittest.TestCase):
    def setUp(self):
        self.state_json = {'user': {'active': {'id': 'keldeo', 'level': 100, 'hp': 323, 'maxhp': 344, 'ability': 'justified', 'item': None, 'baseStats': {'hp': 91, 'attack': 72, 'defense': 90, 'special-attack': 129, 'special-defense': 90, 'speed': 108}, 'attack': 201, 'defense': 237, 'special-attack': 315, 'special-defense': 237, 'speed': 273, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 1, 'special_defense_boost': 1, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'calmmind', 'disabled': False, 'current_pp': 31}, {'id': 'hydropump', 'disabled': False, 'current_pp': 7}, {'id': 'secretsword', 'disabled': False, 'current_pp': 15}, {'id': 'taunt', 'disabled': False, 'current_pp': 32}], 'types': ['water', 'fighting'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'reserve': {'landorustherian': {'id': 'landorustherian', 'level': 100, 'hp': 319, 'maxhp': 340, 'ability': 'intimidate', 'item': None, 'baseStats': {'hp': 89, 'attack': 145, 'defense': 90, 'special-attack': 105, 'special-defense': 80, 'speed': 91}, 'attack': 347, 'defense': 237, 'special-attack': 267, 'special-defense': 217, 'speed': 239, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'stealthrock', 'disabled': False, 'current_pp': 32}, {'id': 'earthquake', 'disabled': False, 'current_pp': 16}, {'id': 'explosion', 'disabled': False, 'current_pp': 8}, {'id': 'swordsdance', 'disabled': False, 'current_pp': 32}], 'types': ['ground', 'flying'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'tornadustherian': {'id': 'tornadustherian', 'level': 100, 'hp': 362, 'maxhp': 320, 'ability': 'regenerator', 'item': None, 'baseStats': {'hp': 79, 'attack': 100, 'defense': 80, 'special-attack': 110, 'special-defense': 90, 'speed': 121}, 'attack': 257, 'defense': 217, 'special-attack': 277, 'special-defense': 237, 'speed': 299, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'hurricane', 'disabled': False, 'current_pp': 16}, {'id': 'defog', 'disabled': False, 'current_pp': 24}, {'id': 'knockoff', 'disabled': False, 'current_pp': 32}, {'id': 'uturn', 'disabled': False, 'current_pp': 32}], 'types': ['flying'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'diancie': {'id': 'diancie', 'level': 100, 'hp': 241, 'maxhp': 262, 'ability': 'clearbody', 'item': None, 'baseStats': {'hp': 50, 'attack': 100, 'defense': 150, 'special-attack': 100, 'special-defense': 150, 'speed': 50}, 'attack': 257, 'defense': 357, 'special-attack': 257, 'special-defense': 357, 'speed': 157, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'moonblast', 'disabled': False, 'current_pp': 24}, {'id': 'diamondstorm', 'disabled': False, 'current_pp': 8}, {'id': 'substitute', 'disabled': False, 'current_pp': 16}, {'id': 'endeavor', 'disabled': False, 'current_pp': 8}], 'types': ['rock', 'fairy'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'victini': {'id': 'victini', 'level': 100, 'hp': 341, 'maxhp': 362, 'ability': 'victorystar', 'item': None, 'baseStats': {'hp': 100, 'attack': 100, 'defense': 100, 'special-attack': 100, 'special-defense': 100, 'speed': 100}, 'attack': 257, 'defense': 257, 'special-attack': 257, 'special-defense': 257, 'speed': 257, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'vcreate', 'disabled': False, 'current_pp': 8}, {'id': 'boltstrike', 'disabled': False, 'current_pp': 8}, {'id': 'uturn', 'disabled': False, 'current_pp': 32}, {'id': 'finalgambit', 'disabled': False, 'current_pp': 8}], 'types': ['psychic', 'fire'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'bisharp': {'id': 'bisharp', 'level': 100, 'hp': 271, 'maxhp': 292, 'ability': 'defiant', 'item': None, 'baseStats': {'hp': 65, 'attack': 125, 'defense': 100, 'special-attack': 60, 'special-defense': 70, 'speed': 70}, 'attack': 307, 'defense': 257, 'special-attack': 177, 'special-defense': 197, 'speed': 197, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'knockoff', 'disabled': False, 'current_pp': 32}, {'id': 'ironhead', 'disabled': False, 'current_pp': 24}, {'id': 'suckerpunch', 'disabled': False, 'current_pp': 8}, {'id': 'swordsdance', 'disabled': False, 'current_pp': 32}], 'types': ['dark', 'steel'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}}, 'wish': (0, 0), 'futuresight': (0, 0), 'side_conditions': {'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0, 'stealthrock': 0, 'spikes': 0, 'stickyweb': 0, 'toxicspikes': 0}, 'trapped': False}, 'opponent': {'active': {'id': 'manaphy', 'level': 100, 'hp': 86.88, 'maxhp': 362, 'ability': 'hydration', 'item': 'Leftovers', 'baseStats': {'hp': 100, 'attack': 100, 'defense': 100, 'special-attack': 100, 'special-defense': 100, 'speed': 100}, 'attack': 257, 'defense': 257, 'special-attack': 257, 'special-defense': 257, 'speed': 257, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 6, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'tailglow', 'disabled': False, 'current_pp': 32}], 'types': ['water'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'reserve': {'mamoswine': {'id': 'mamoswine', 'level': 100, 'hp': 382, 'maxhp': 382, 'ability': None, 'item': None, 'baseStats': {'hp': 110, 'attack': 130, 'defense': 80, 'special-attack': 70, 'special-defense': 60, 'speed': 80}, 'attack': 317, 'defense': 217, 'special-attack': 197, 'special-defense': 177, 'speed': 217, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [], 'types': ['ice', 'ground'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'alakazam': {'id': 'alakazam', 'level': 100, 'hp': 272, 'maxhp': 272, 'ability': None, 'item': None, 'baseStats': {'hp': 55, 'attack': 50, 'defense': 45, 'special-attack': 135, 'special-defense': 95, 'speed': 120}, 'attack': 157, 'defense': 147, 'special-attack': 327, 'special-defense': 247, 'speed': 297, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [], 'types': ['psychic'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'stakataka': {'id': 'stakataka', 'level': 100, 'hp': 284, 'maxhp': 284, 'ability': 'beastboost', 'item': None, 'baseStats': {'hp': 61, 'attack': 131, 'defense': 211, 'special-attack': 53, 'special-defense': 101, 'speed': 13}, 'attack': 319, 'defense': 479, 'special-attack': 163, 'special-defense': 259, 'speed': 83, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [], 'types': ['rock', 'steel'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'moltres': {'id': 'moltres', 'level': 100, 'hp': 342, 'maxhp': 342, 'ability': None, 'item': None, 'baseStats': {'hp': 90, 'attack': 100, 'defense': 90, 'special-attack': 125, 'special-defense': 85, 'speed': 90}, 'attack': 257, 'defense': 237, 'special-attack': 307, 'special-defense': 227, 'speed': 237, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [], 'types': ['fire', 'flying'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'gliscor': {'id': 'gliscor', 'level': 100, 'hp': 312, 'maxhp': 312, 'ability': None, 'item': None, 'baseStats': {'hp': 75, 'attack': 95, 'defense': 125, 'special-attack': 45, 'special-defense': 75, 'speed': 95}, 'attack': 247, 'defense': 307, 'special-attack': 147, 'special-defense': 207, 'speed': 247, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [], 'types': ['ground', 'flying'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}}, 'wish': (0, 0), 'futuresight': (0, 0), 'side_conditions': {'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0, 'stealthrock': 0, 'spikes': 0, 'stickyweb': 0, 'toxicspikes': 0}, 'trapped': False}, 'weather': None, 'field': None, 'forceSwitch': False, 'wait': False, 'trickroom': False}
        self.state = State.from_dict(self.state_json)

    def test_returns_true_when_all_pokemon_for_user_are_dead(self):
        self.state.user.active.hp = 0
        for pkmn in self.state.user.reserve.values():
            pkmn.hp = 0

        self.assertTrue(self.state.battle_is_finished())

    def test_returns_true_when_all_pokemon_for_opponent_are_dead(self):
        self.state.opponent.active.hp = 0
        for pkmn in self.state.opponent.reserve.values():
            pkmn.hp = 0

        self.assertTrue(self.state.battle_is_finished())

    def test_returns_false_when_all_pokemon_are_alive(self):
        self.assertFalse(self.state.battle_is_finished())

    def test_returns_false_when_only_active_is_dead(self):
        self.state.opponent.active.hp = 0
        self.assertFalse(self.state.battle_is_finished())

    def test_returns_false_when_only_reserve_are_dead(self):
        for pkmn in self.state.user.reserve.values():
            pkmn.hp = 0
        self.assertFalse(self.state.battle_is_finished())

    def test_returns_false_when_all_pokemon_are_alive_for_opponent(self):
        self.assertFalse(self.state.battle_is_finished())

    def test_returns_false_when_only_active_is_dead_for_opponent(self):
        self.state.opponent.active.hp = 0
        self.assertFalse(self.state.battle_is_finished())

    def test_returns_false_when_only_reserve_are_dead_for_opponent(self):
        for pkmn in self.state.opponent.reserve.values():
            pkmn.hp = 0
        self.assertFalse(self.state.battle_is_finished())


class TestSpreadsAreAlike(unittest.TestCase):
    def test_two_similar_spreads_are_alike(self):
        s1 = ('jolly', '0,0,0,252,4,252')
        s2 = ('jolly', '0,0,4,252,0,252')

        self.assertTrue(spreads_are_alike(s1, s2))

    def test_different_natures_are_not_alike(self):
        s1 = ('jolly', '0,0,0,252,4,252')
        s2 = ('modest', '0,0,4,252,0,252')

        self.assertFalse(spreads_are_alike(s1, s2))

    def test_custom_is_not_the_same_as_max_values(self):
        s1 = ('jolly', '16,0,0,252,0,240')
        s2 = ('modest', '0,0,4,252,0,252')

        self.assertFalse(spreads_are_alike(s1, s2))

    def test_very_similar_returns_true(self):
        s1 = ('modest', '16,0,0,252,0,240')
        s2 = ('modest', '28,0,4,252,0,252')

        self.assertTrue(spreads_are_alike(s1, s2))


class TestRemoveDuplicateSpreads(unittest.TestCase):
    def test_only_one_spread_remains_when_all_are_alike(self):
        s1 = ('jolly', '0,0,0,252,4,252')
        s2 = ('jolly', '0,0,4,252,0,252')
        s3 = ('jolly', '0,4,0,252,0,252')
        s4 = ('jolly', '4,0,0,252,0,252')

        spreads = [s1, s2, s3, s4]

        expected_result = [s1]

        self.assertEqual(expected_result, remove_duplicate_spreads(spreads))

    def test_different_spreads_remain(self):
        s1 = ('jolly', '0,0,0,252,4,252')
        s2 = ('adamant', '0,0,4,252,0,252')
        s3 = ('jolly', '0,4,0,252,0,252')
        s4 = ('jolly', '4,0,0,252,0,252')

        spreads = [s1, s2, s3, s4]

        expected_result = [s1, s2]

        self.assertEqual(expected_result, remove_duplicate_spreads(spreads))

    def test_all_spreads_remain(self):
        s1 = ('jolly', '0,0,0,252,4,252')
        s2 = ('adamant', '0,0,4,252,0,252')
        s3 = ('jolly', '0,108,0,148,0,252')
        s4 = ('adamant', '104,0,0,152,0,252')

        spreads = [s1, s2, s3, s4]

        expected_result = [s1, s2, s3, s4]

        self.assertEqual(expected_result, remove_duplicate_spreads(spreads))


class TestSetMakesSense(unittest.TestCase):
    def test_standard_set_makes_sense(self):
        nature = 'jolly'
        spread = '0,0,0,252,4,252'
        item = 'unknown_item'
        ability = 'intimidate'
        moves = []

        self.assertTrue(set_makes_sense(nature, spread, item, ability, moves))

    def test_swordsdance_with_choiceband_does_not_make_sense(self):
        nature = 'jolly'
        spread = '0,0,0,252,4,252'
        item = 'choiceband'
        ability = 'intimidate'
        moves = [Move('swordsdance')]

        self.assertFalse(set_makes_sense(nature, spread, item, ability, moves))

    def test_nastyplot_with_choicespecs_does_not_make_sense(self):
        nature = 'jolly'
        spread = '0,0,0,252,4,252'
        item = 'choicespecs'
        ability = 'intimidate'
        moves = [Move('nastyplot')]

        self.assertFalse(set_makes_sense(nature, spread, item, ability, moves))

    def test_multiple_move_nastyplot_with_choicespecs_does_not_make_sense(self):
        nature = 'jolly'
        spread = '0,0,0,252,4,252'
        item = 'choicespecs'
        ability = 'intimidate'
        moves = [
            Move('nastyplot'),
            Move('darkpulse'),
            Move('thunderbolt'),
        ]

        self.assertFalse(set_makes_sense(nature, spread, item, ability, moves))

    def test_trick_with_scarf_makes_sense(self):
        nature = 'jolly'
        spread = '0,0,0,252,4,252'
        item = 'choicescarf'
        ability = 'intimidate'
        moves = [
            Move('trick'),
            Move('darkpulse'),
            Move('thunderbolt'),
        ]

        self.assertTrue(set_makes_sense(nature, spread, item, ability, moves))


class TestNormalizeName(unittest.TestCase):
    def test_removes_nonascii_characters(self):
        n = 'Flabébé'
        expected_result = 'flabebe'
        result = normalize_name(n)

        self.assertEqual(expected_result, result)


class TestGetPokemonInfoFromCondition(unittest.TestCase):
    def setUp(self):
        self.state_json = {'user': {'active': {'id': 'keldeo', 'level': 100, 'hp': 323, 'maxhp': 344, 'ability': 'justified', 'item': None, 'baseStats': {'hp': 91, 'attack': 72, 'defense': 90, 'special-attack': 129, 'special-defense': 90, 'speed': 108}, 'attack': 201, 'defense': 237, 'special-attack': 315, 'special-defense': 237, 'speed': 273, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 1, 'special_defense_boost': 1, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'calmmind', 'disabled': False, 'current_pp': 31}, {'id': 'hydropump', 'disabled': False, 'current_pp': 7}, {'id': 'secretsword', 'disabled': False, 'current_pp': 15}, {'id': 'taunt', 'disabled': False, 'current_pp': 32}], 'types': ['water', 'fighting'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'reserve': {'landorustherian': {'id': 'landorustherian', 'level': 100, 'hp': 319, 'maxhp': 340, 'ability': 'intimidate', 'item': None, 'baseStats': {'hp': 89, 'attack': 145, 'defense': 90, 'special-attack': 105, 'special-defense': 80, 'speed': 91}, 'attack': 347, 'defense': 237, 'special-attack': 267, 'special-defense': 217, 'speed': 239, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'stealthrock', 'disabled': False, 'current_pp': 32}, {'id': 'earthquake', 'disabled': False, 'current_pp': 16}, {'id': 'explosion', 'disabled': False, 'current_pp': 8}, {'id': 'swordsdance', 'disabled': False, 'current_pp': 32}], 'types': ['ground', 'flying'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'tornadustherian': {'id': 'tornadustherian', 'level': 100, 'hp': 362, 'maxhp': 320, 'ability': 'regenerator', 'item': None, 'baseStats': {'hp': 79, 'attack': 100, 'defense': 80, 'special-attack': 110, 'special-defense': 90, 'speed': 121}, 'attack': 257, 'defense': 217, 'special-attack': 277, 'special-defense': 237, 'speed': 299, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'hurricane', 'disabled': False, 'current_pp': 16}, {'id': 'defog', 'disabled': False, 'current_pp': 24}, {'id': 'knockoff', 'disabled': False, 'current_pp': 32}, {'id': 'uturn', 'disabled': False, 'current_pp': 32}], 'types': ['flying'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'diancie': {'id': 'diancie', 'level': 100, 'hp': 241, 'maxhp': 262, 'ability': 'clearbody', 'item': None, 'baseStats': {'hp': 50, 'attack': 100, 'defense': 150, 'special-attack': 100, 'special-defense': 150, 'speed': 50}, 'attack': 257, 'defense': 357, 'special-attack': 257, 'special-defense': 357, 'speed': 157, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'moonblast', 'disabled': False, 'current_pp': 24}, {'id': 'diamondstorm', 'disabled': False, 'current_pp': 8}, {'id': 'substitute', 'disabled': False, 'current_pp': 16}, {'id': 'endeavor', 'disabled': False, 'current_pp': 8}], 'types': ['rock', 'fairy'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'victini': {'id': 'victini', 'level': 100, 'hp': 341, 'maxhp': 362, 'ability': 'victorystar', 'item': None, 'baseStats': {'hp': 100, 'attack': 100, 'defense': 100, 'special-attack': 100, 'special-defense': 100, 'speed': 100}, 'attack': 257, 'defense': 257, 'special-attack': 257, 'special-defense': 257, 'speed': 257, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'vcreate', 'disabled': False, 'current_pp': 8}, {'id': 'boltstrike', 'disabled': False, 'current_pp': 8}, {'id': 'uturn', 'disabled': False, 'current_pp': 32}, {'id': 'finalgambit', 'disabled': False, 'current_pp': 8}], 'types': ['psychic', 'fire'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'bisharp': {'id': 'bisharp', 'level': 100, 'hp': 271, 'maxhp': 292, 'ability': 'defiant', 'item': None, 'baseStats': {'hp': 65, 'attack': 125, 'defense': 100, 'special-attack': 60, 'special-defense': 70, 'speed': 70}, 'attack': 307, 'defense': 257, 'special-attack': 177, 'special-defense': 197, 'speed': 197, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'knockoff', 'disabled': False, 'current_pp': 32}, {'id': 'ironhead', 'disabled': False, 'current_pp': 24}, {'id': 'suckerpunch', 'disabled': False, 'current_pp': 8}, {'id': 'swordsdance', 'disabled': False, 'current_pp': 32}], 'types': ['dark', 'steel'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}}, 'wish': (0, 0), 'futuresight': (0, 0), 'side_conditions': {'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0, 'stealthrock': 0, 'spikes': 0, 'stickyweb': 0, 'toxicspikes': 0}, 'trapped': False}, 'opponent': {'active': {'id': 'manaphy', 'level': 100, 'hp': 86.88, 'maxhp': 362, 'ability': 'hydration', 'item': 'Leftovers', 'baseStats': {'hp': 100, 'attack': 100, 'defense': 100, 'special-attack': 100, 'special-defense': 100, 'speed': 100}, 'attack': 257, 'defense': 257, 'special-attack': 257, 'special-defense': 257, 'speed': 257, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 6, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'tailglow', 'disabled': False, 'current_pp': 32}], 'types': ['water'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'reserve': {'mamoswine': {'id': 'mamoswine', 'level': 100, 'hp': 382, 'maxhp': 382, 'ability': None, 'item': None, 'baseStats': {'hp': 110, 'attack': 130, 'defense': 80, 'special-attack': 70, 'special-defense': 60, 'speed': 80}, 'attack': 317, 'defense': 217, 'special-attack': 197, 'special-defense': 177, 'speed': 217, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [], 'types': ['ice', 'ground'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'alakazam': {'id': 'alakazam', 'level': 100, 'hp': 272, 'maxhp': 272, 'ability': None, 'item': None, 'baseStats': {'hp': 55, 'attack': 50, 'defense': 45, 'special-attack': 135, 'special-defense': 95, 'speed': 120}, 'attack': 157, 'defense': 147, 'special-attack': 327, 'special-defense': 247, 'speed': 297, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [], 'types': ['psychic'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'stakataka': {'id': 'stakataka', 'level': 100, 'hp': 284, 'maxhp': 284, 'ability': 'beastboost', 'item': None, 'baseStats': {'hp': 61, 'attack': 131, 'defense': 211, 'special-attack': 53, 'special-defense': 101, 'speed': 13}, 'attack': 319, 'defense': 479, 'special-attack': 163, 'special-defense': 259, 'speed': 83, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [], 'types': ['rock', 'steel'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'moltres': {'id': 'moltres', 'level': 100, 'hp': 342, 'maxhp': 342, 'ability': None, 'item': None, 'baseStats': {'hp': 90, 'attack': 100, 'defense': 90, 'special-attack': 125, 'special-defense': 85, 'speed': 90}, 'attack': 257, 'defense': 237, 'special-attack': 307, 'special-defense': 227, 'speed': 237, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [], 'types': ['fire', 'flying'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'gliscor': {'id': 'gliscor', 'level': 100, 'hp': 312, 'maxhp': 312, 'ability': None, 'item': None, 'baseStats': {'hp': 75, 'attack': 95, 'defense': 125, 'special-attack': 45, 'special-defense': 75, 'speed': 95}, 'attack': 247, 'defense': 307, 'special-attack': 147, 'special-defense': 207, 'speed': 247, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [], 'types': ['ground', 'flying'], 'canMegaEvo': False, 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}}, 'wish': (0, 0), 'futuresight': (0, 0), 'side_conditions': {'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0, 'stealthrock': 0, 'spikes': 0, 'stickyweb': 0, 'toxicspikes': 0}, 'trapped': False}, 'weather': None, 'field': None, 'forceSwitch': False, 'wait': False, 'trickroom': False}
        self.state = State.from_dict(self.state_json)

    def test_basic_case(self):
        condition_string = '100/100'
        expected_results = 100, 100, None

        self.assertEqual(expected_results, get_pokemon_info_from_condition(condition_string))

    def test_burned_case(self):
        condition_string = '100/100 brn'
        expected_results = 100, 100, 'brn'

        self.assertEqual(expected_results, get_pokemon_info_from_condition(condition_string))

    def test_poisoned_case(self):
        condition_string = '121/403 psn'
        expected_results = 121, 403, 'psn'

        self.assertEqual(expected_results, get_pokemon_info_from_condition(condition_string))

    def test_fainted_case(self):
        condition_string = '0/100 fnt'

        self.assertEqual(0, get_pokemon_info_from_condition(condition_string)[0])
