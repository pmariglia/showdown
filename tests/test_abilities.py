import unittest
from unittest.mock import MagicMock
import constants
from showdown.engine.special_effects.abilities.modify_attack_against import ability_modify_attack_against
from showdown.engine.special_effects.abilities.modify_attack_being_used import ability_modify_attack_being_used


class TestLevitate(unittest.TestCase):
    def setUp(self):
        self.state = dict()
        self.ability_name = "levitate"

    def test_ground_move_does_zero_damage_against_pokemon_with_levitate(self):
        move = {
            constants.NAME: "cool_move",
            constants.TYPE: "ground",
            constants.TARGET: constants.NORMAL
        }

        expected_move = {
            constants.NAME: "cool_move",
            constants.TYPE: "ground",
            constants.BASE_POWER: 0,
            constants.TARGET: constants.NORMAL
        }

        self.assertEqual(expected_move, ability_modify_attack_against(self.ability_name, move, None, None))

    def test_normal_move_does_zero_damage_against_pokemon_with_levitate(self):
        move = {
            constants.NAME: "cool_move",
            constants.TYPE: "flying",
            constants.TARGET: constants.NORMAL
        }
        self.assertEqual(move, ability_modify_attack_against(self.ability_name, move, None, None))


class TestAdaptability(unittest.TestCase):
    def setUp(self):
        self.state = dict()
        self.ability_name = 'adaptability'

    def test_boosts_damage_when_move_type_is_in_pokemon_types(self):
        move = {
            constants.NAME: "cool_move",
            constants.TYPE: "normal",
            constants.BASE_POWER: 100
        }
        pkmn = MagicMock()
        pkmn.types = ['normal', 'flying']

        expected_move = {
            constants.NAME: "cool_move",
            constants.TYPE: "normal",
            constants.BASE_POWER: int(400/3)
        }

        self.assertEqual(expected_move, ability_modify_attack_being_used(self.ability_name, move, pkmn, None, False, None))

    def test_does_not_boost_damage_when_it_does_not_need_to(self):
        move = {
            constants.NAME: "cool_move",
            constants.TYPE: "dark"
        }
        pkmn = MagicMock()
        pkmn.types = ['ghost', 'flying']
        self.assertEqual(move, ability_modify_attack_being_used(self.ability_name, move, pkmn, None, False, None))


class TestAerilate(unittest.TestCase):
    def setUp(self):
        self.ability_name = 'aerilate'

    def test_boosts_move_and_changes_type_to_flying(self):
        move = {
            constants.NAME: "cool_move",
            constants.TYPE: "normal",
            constants.BASE_POWER: 100
        }

        expected_move = {
            constants.NAME: "cool_move",
            constants.TYPE: "flying",
            constants.BASE_POWER: 120
        }

        self.assertEqual(expected_move, ability_modify_attack_being_used(self.ability_name, move, None, None, False, None))

    def test_does_not_modify_flying_move(self):
        move = {
            constants.NAME: "cool_move",
            constants.TYPE: "flying",
            constants.BASE_POWER: 100
        }

        expected_move = {
            constants.NAME: "cool_move",
            constants.TYPE: "flying",
            constants.BASE_POWER: 100
        }

        self.assertEqual(expected_move, ability_modify_attack_being_used(self.ability_name, move, None, None, False, None))


class TestMegaLauncher(unittest.TestCase):
    def setUp(self):
        self.state = dict()
        self.ability_name = "megalauncher"

    def test_mega_launcher_boosts_darkpulse(self):

        move = {
            "accuracy": 100,
            "basePower": 80,
            "category": "special",
            "flags": {
                "protect": 1,
                "pulse": 1,
                "mirror": 1,
                "distance": 1
            },
            "id": "darkpulse",
            "name": "Dark Pulse",
            "priority": 0,
            "secondary": {
                "chance": 20,
                "volatileStatus": "flinch"
            },
            "target": "any",
            "type": "dark",
            "pp": 15
        }
        expected_move_power = 120
        pkmn = MagicMock()
        actual_power = ability_modify_attack_being_used(self.ability_name, move, pkmn, None, False, None)[constants.BASE_POWER]

        self.assertEqual(expected_move_power, actual_power)

    def test_mega_launcher_does_not_boost_tackle(self):

        move = {
            "accuracy": 100,
            "basePower": 40,
            "category": "special",
            "flags": {
                "protect": 1,
                "mirror": 1,
                "distance": 1
            },
            "id": "tackle",
            "priority": 0,
            "target": "any",
            "type": "dark",
            "pp": 15
        }
        expected_move_power = 40
        pkmn = MagicMock()
        actual_power = ability_modify_attack_being_used(self.ability_name, move, pkmn, None, False, None)[constants.BASE_POWER]

        self.assertEqual(expected_move_power, actual_power)
