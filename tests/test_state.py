import unittest

import constants
from showdown.engine.objects import State
from showdown.battle import Pokemon as StatePokemon
from showdown.engine.objects import Pokemon


class TestPokemonInit(unittest.TestCase):

    def test_state_serialization_and_loading_results_in_the_same_state(self):
        state_json = {'user': {'active': {'id': 'tornadustherian', 'level': 100, 'hp': 0, 'maxhp': 0, 'ability': 'regenerator', 'item': 'fightiniumz', 'attack': 212, 'defense': 197, 'special-attack': 319, 'special-defense': 216, 'speed': 375, 'attack_boost': -1, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'accuracy_boost': 1, 'evasion_boost': 1, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'taunt', 'disabled': False, 'current_pp': 32}, {'id': 'hurricane', 'disabled': False, 'current_pp': 16}, {'id': 'focusblast', 'disabled': False, 'current_pp': 8}, {'id': 'defog', 'disabled': False, 'current_pp': 24}], 'types': ['flying'], 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'reserve': {'greninja': {'id': 'greninja', 'level': 100, 'hp': 285, 'maxhp': 285, 'ability': 'battlebond', 'item': 'choicespecs', 'attack': 203, 'defense': 171, 'special-attack': 305, 'special-defense': 178, 'speed': 377, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'accuracy_boost': 1, 'evasion_boost': 1, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'surf', 'disabled': False, 'current_pp': 24}, {'id': 'darkpulse', 'disabled': False, 'current_pp': 24}, {'id': 'icebeam', 'disabled': False, 'current_pp': 16}, {'id': 'watershuriken', 'disabled': False, 'current_pp': 32}], 'types': ['water', 'dark'], 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'mawile': {'id': 'mawile', 'level': 100, 'hp': 261.0, 'maxhp': 261, 'ability': 'intimidate', 'item': 'mawilite', 'attack': 295, 'defense': 206, 'special-attack': 131, 'special-defense': 146, 'speed': 180, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'accuracy_boost': 1, 'evasion_boost': 1, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'suckerpunch', 'disabled': False, 'current_pp': 8}, {'id': 'playrough', 'disabled': False, 'current_pp': 16}, {'id': 'thunderpunch', 'disabled': False, 'current_pp': 24}, {'id': 'firefang', 'disabled': False, 'current_pp': 24}], 'types': ['steel', 'fairy'], 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'ferrothorn': {'id': 'ferrothorn', 'level': 100, 'hp': 352.0, 'maxhp': 352, 'ability': 'ironbarbs', 'item': 'leftovers', 'attack': 224, 'defense': 299, 'special-attack': 144, 'special-defense': 364, 'speed': 68, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'accuracy_boost': 1, 'evasion_boost': 1, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'spikes', 'disabled': False, 'current_pp': 32}, {'id': 'leechseed', 'disabled': False, 'current_pp': 16}, {'id': 'knockoff', 'disabled': False, 'current_pp': 32}, {'id': 'gyroball', 'disabled': False, 'current_pp': 8}], 'types': ['grass', 'steel'], 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'heatran': {'id': 'heatran', 'level': 100, 'hp': 385, 'maxhp': 385, 'ability': 'flashfire', 'item': 'leftovers', 'attack': 194, 'defense': 248, 'special-attack': 296, 'special-defense': 332, 'speed': 201, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'accuracy_boost': 1, 'evasion_boost': 1, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'taunt', 'disabled': False, 'current_pp': 32}, {'id': 'magmastorm', 'disabled': False, 'current_pp': 8}, {'id': 'earthpower', 'disabled': False, 'current_pp': 16}, {'id': 'toxic', 'disabled': False, 'current_pp': 16}], 'types': ['fire', 'steel'], 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'garchomp': {'id': 'garchomp', 'level': 100, 'hp': 379, 'maxhp': 379, 'ability': 'roughskin', 'item': 'rockyhelmet', 'attack': 296, 'defense': 317, 'special-attack': 176, 'special-defense': 206, 'speed': 282, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'accuracy_boost': 1, 'evasion_boost': 1, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'stealthrock', 'disabled': False, 'current_pp': 32}, {'id': 'earthquake', 'disabled': False, 'current_pp': 16}, {'id': 'toxic', 'disabled': False, 'current_pp': 16}, {'id': 'roar', 'disabled': False, 'current_pp': 32}], 'types': ['dragon', 'ground'], 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}}, 'wish': (0, 0), 'futuresight': (0, 0), 'side_conditions': {'toxic_count': 0, 'tailwind': 0, 'stealthrock': 0, 'spikes': 0, 'stickyweb': 0, 'toxicspikes': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0}}, 'opponent': {'active': {'id': 'landorustherian', 'level': 100, 'hp': 319.0, 'maxhp': 319, 'ability': 'intimidate', 'item': 'choicescarf', 'attack': 389, 'defense': 216, 'special-attack': 223.63636363636363, 'special-defense': 197, 'speed': 309.1, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'accuracy_boost': 1, 'evasion_boost': 1, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'earthquake', 'disabled': False, 'current_pp': 16}, {'id': 'uturn', 'disabled': False, 'current_pp': 32}, {'id': 'stealthrock', 'disabled': False, 'current_pp': 32}, {'id': 'defog', 'disabled': False, 'current_pp': 24}, {'id': 'stoneedge', 'disabled': False, 'current_pp': 8}], 'types': ['ground', 'flying'], 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'reserve': {'ferrothorn': {'id': 'ferrothorn', 'level': 100, 'hp': 352.0, 'maxhp': 352, 'ability': 'ironbarbs', 'item': 'leftovers', 'attack': 224, 'defense': 304, 'special-attack': 158.4, 'special-defense': 326, 'speed': 69.09090909090908, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'accuracy_boost': 1, 'evasion_boost': 1, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'leechseed', 'disabled': False, 'current_pp': 16}, {'id': 'gyroball', 'disabled': False, 'current_pp': 8}, {'id': 'stealthrock', 'disabled': False, 'current_pp': 32}, {'id': 'powerwhip', 'disabled': False, 'current_pp': 16}], 'types': ['grass', 'steel'], 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'rotomwash': {'id': 'rotomwash', 'level': 100, 'hp': 304.0, 'maxhp': 304, 'ability': 'levitate', 'item': 'leftovers', 'attack': 150.9090909090909, 'defense': 330.0, 'special-attack': 246, 'special-defense': 250, 'speed': 222, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'accuracy_boost': 1, 'evasion_boost': 1, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'hydropump', 'disabled': False, 'current_pp': 8}, {'id': 'voltswitch', 'disabled': False, 'current_pp': 32}, {'id': 'willowisp', 'disabled': False, 'current_pp': 24}, {'id': 'defog', 'disabled': False, 'current_pp': 24}], 'types': ['electric', 'water'], 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'mawile': {'id': 'mawile', 'level': 100, 'hp': 303.0, 'maxhp': 303, 'ability': 'intimidate', 'item': 'leftovers', 'attack': 295.90000000000003, 'defense': 206, 'special-attack': 132.72727272727272, 'special-defense': 148, 'speed': 136, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'accuracy_boost': 1, 'evasion_boost': 1, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'playrough', 'disabled': False, 'current_pp': 16}, {'id': 'ironhead', 'disabled': False, 'current_pp': 24}, {'id': 'suckerpunch', 'disabled': False, 'current_pp': 8}, {'id': 'swordsdance', 'disabled': False, 'current_pp': 32}], 'types': ['steel', 'fairy'], 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'greninja': {'id': 'greninja', 'level': 100, 'hp': 285.0, 'maxhp': 285, 'ability': 'protean', 'item': 'choicescarf', 'attack': 205.45454545454544, 'defense': 170, 'special-attack': 305, 'special-defense': 179, 'speed': 377.3, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'accuracy_boost': 1, 'evasion_boost': 1, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'icebeam', 'disabled': False, 'current_pp': 16}, {'id': 'gunkshot', 'disabled': False, 'current_pp': 8}, {'id': 'uturn', 'disabled': False, 'current_pp': 32}, {'id': 'hydropump', 'disabled': False, 'current_pp': 8}], 'types': ['water', 'dark'], 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}, 'scolipede': {'id': 'scolipede', 'level': 100, 'hp': 261.0, 'maxhp': 261, 'ability': 'speedboost', 'item': 'wateriumz', 'attack': 328.90000000000003, 'defense': 214, 'special-attack': 132.72727272727272, 'special-defense': 175, 'speed': 323, 'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0, 'accuracy_boost': 1, 'evasion_boost': 1, 'status': None, 'volatileStatus': [], 'moves': [{'id': 'swordsdance', 'disabled': False, 'current_pp': 32}, {'id': 'earthquake', 'disabled': False, 'current_pp': 16}, {'id': 'megahorn', 'disabled': False, 'current_pp': 16}, {'id': 'poisonjab', 'disabled': False, 'current_pp': 32}], 'types': ['bug', 'poison'], 'nature': 'serious', 'evs': (85, 85, 85, 85, 85, 85)}}, 'wish': (0, 0), 'futuresight': (0, 0), 'side_conditions': {'toxic_count': 0, 'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0, 'stealthrock': 0, 'spikes': 0, 'stickyweb': 0, 'toxicspikes': 0}}, 'weather': 1, 'field': 2, 'trickroom': 3}
        state = State.from_dict(state_json)

        # str(state) gives a string representing the state-dict
        new_state_dict = eval(str(state))

        self.assertEqual(state_json, new_state_dict)

    def test_pokemon_init_gives_correct_number_of_physical_moves(self):
        # 2 moves that are physical
        moves = [
          {constants.ID: 'flamethrower'},
          {constants.ID: 'flareblitz'},
          {constants.ID: 'flamewheel'},
          {constants.ID: 'reflect'},
        ]

        state_pkmn_dict = StatePokemon('charizardmegax', 100).to_dict()
        state_pkmn_dict[constants.MOVES] = moves
        pkmn = Pokemon.from_state_pokemon_dict(state_pkmn_dict)

        self.assertEqual(2, pkmn.burn_multiplier)


class TestPokemon(unittest.TestCase):
    def setUp(self):
        self.pokemon = Pokemon.from_state_pokemon_dict(
          StatePokemon('pikachu', 100).to_dict()
        )

    def test_pokemon_item_can_be_removed_returns_true_in_basic_case(self):
        self.pokemon.item = constants.UNKNOWN_ITEM
        self.assertTrue(self.pokemon.item_can_be_removed())

    def test_item_can_be_removed_returns_false_if_item_is_none(self):
        self.pokemon.item = None
        self.assertFalse(self.pokemon.item_can_be_removed())

    def test_item_can_be_removed_returns_false_if_pokemon_is_silvallybug(self):
        self.pokemon.id = 'silvallybug'
        self.pokemon.item = 'bugmemory'
        self.assertFalse(self.pokemon.item_can_be_removed())

    def test_item_can_be_removed_returns_true_if_pokemon_is_silvallynormal(self):
        self.pokemon.id = 'silvally'
        self.pokemon.item = 'choicescarf'
        self.assertTrue(self.pokemon.item_can_be_removed())

    def test_item_can_be_removed_returns_false_if_pokemon_has_substitute(self):
        self.pokemon.volatile_status.add('substitute')
        self.assertFalse(self.pokemon.item_can_be_removed())

    def test_item_can_be_removed_returns_false_if_pokemon_is_holding_zcrystal(self):
        self.pokemon.item = 'fightiniumz'
        self.assertFalse(self.pokemon.item_can_be_removed())

    def test_item_can_be_removed_returns_false_if_target_is_kyogreprimal(self):
        self.pokemon.id = 'kyogreprimal'
        self.assertFalse(self.pokemon.item_can_be_removed())
