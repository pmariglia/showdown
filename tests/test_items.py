import unittest
from unittest.mock import MagicMock
import constants
from showdown.engine.special_effects.items.modify_attack_being_used import item_modify_attack_being_used
from showdown.engine.special_effects.items.modify_attack_against import item_modify_attack_against


class TestChoiceBand(unittest.TestCase):
    def setUp(self):
        self.state = dict()
        self.item_name = "choiceband"

    def test_choice_band_boosts_physical(self):

        move = {
            "accuracy": 100,
            "basePower": 40,
            "category": "physical",
            "flags": {
                "protect": 1,
                "pulse": 1,
                "mirror": 1,
                "distance": 1
            },
            "id": "tackle",
            "priority": 0,
            "target": "normal",
            "type": "normal",
            "pp": 15
        }
        expected_move_power = 60
        pkmn = MagicMock()
        actual_power = item_modify_attack_being_used(self.item_name, move, pkmn, None)[constants.BASE_POWER]

        self.assertEqual(expected_move_power, actual_power)

    def test_choice_band_does_not_boost_special(self):

        move = {
            "accuracy": 100,
            "basePower": 90,
            "category": "special",
            "flags": {
                "protect": 1,
                "pulse": 1,
                "mirror": 1,
                "distance": 1
            },
            "id": "flamethrower",
            "priority": 0,
            "target": "normal",
            "type": "fire",
            "pp": 15
        }
        expected_move_power = 90
        pkmn = MagicMock()
        actual_power = item_modify_attack_being_used(self.item_name, move, pkmn, None)[constants.BASE_POWER]

        self.assertEqual(expected_move_power, actual_power)


class TestChoiceSpecs(unittest.TestCase):
    def setUp(self):
        self.state = dict()
        self.item_name = "choicespecs"

    def test_choice_scarf_does_not_boost_physical(self):

        move = {
            "accuracy": 100,
            "basePower": 40,
            "category": "physical",
            "flags": {
                "protect": 1,
                "pulse": 1,
                "mirror": 1,
                "distance": 1
            },
            "id": "tackle",
            "priority": 0,
            "target": "normal",
            "type": "normal",
            "pp": 15
        }
        expected_move_power = 40
        pkmn = MagicMock()
        actual_power = item_modify_attack_being_used(self.item_name, move, pkmn, None)[constants.BASE_POWER]

        self.assertEqual(expected_move_power, actual_power)

    def test_choice_scarf_boosts_special(self):

        move = {
            "accuracy": 100,
            "basePower": 90,
            "category": "special",
            "flags": {
                "protect": 1,
                "pulse": 1,
                "mirror": 1,
                "distance": 1
            },
            "id": "flamethrower",
            "priority": 0,
            "target": "normal",
            "type": "fire",
            "pp": 15
        }
        expected_move_power = 135
        pkmn = MagicMock()
        actual_power = item_modify_attack_being_used(self.item_name, move, pkmn, None)[constants.BASE_POWER]

        self.assertEqual(expected_move_power, actual_power)


class TestEviolite(unittest.TestCase):
    def setUp(self):
        self.state = dict()
        self.item_name = "eviolite"

    def test_reduces_physical_move(self):

        move = {
            "accuracy": 100,
            "basePower": 40,
            "category": "physical",
            "flags": {
                "protect": 1,
                "pulse": 1,
                "mirror": 1,
                "distance": 1
            },
            "id": "tackle",
            "priority": 0,
            "target": "normal",
            "type": "normal",
            "pp": 15
        }
        expected_move_power = 26.666666666666668
        pkmn = MagicMock()
        actual_power = item_modify_attack_against(self.item_name, move, pkmn, None)[constants.BASE_POWER]

        self.assertEqual(expected_move_power, actual_power)

    def test_reduces_special_move(self):

        move = {
            "accuracy": 100,
            "basePower": 90,
            "category": "special",
            "flags": {
                "protect": 1,
                "pulse": 1,
                "mirror": 1,
                "distance": 1
            },
            "id": "flamethrower",
            "priority": 0,
            "target": "normal",
            "type": "fire",
            "pp": 15
        }
        expected_move_power = 60.0
        pkmn = MagicMock()
        actual_power = item_modify_attack_against(self.item_name, move, pkmn, None)[constants.BASE_POWER]

        self.assertEqual(expected_move_power, actual_power)
