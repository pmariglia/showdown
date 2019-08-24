import unittest
from unittest import mock

import constants

from showdown.battle import Pokemon
from showdown.battle import Move


class TestPokemonInit(unittest.TestCase):
    def test_alternate_pokemon_name_initializes(self):
        name = 'florgeswhite'
        Pokemon(name, 100)


class TestGetItemForRandomBattles(unittest.TestCase):
    def setUp(self):
        self.get_sets_patch = mock.patch('data.helpers._get_random_battle_set')
        self.addCleanup(self.get_sets_patch.stop)
        self.get_sets_mock = self.get_sets_patch.start()

        self.get_sets_mock.return_value = {
            constants.ITEMS: {
                "item": 33
            }
        }

    def test_gets_item_when_item_is_unknown(self):
        p = Pokemon('pikachu', 100)
        p.item = constants.UNKNOWN_ITEM
        p.update_item_for_random_battles()
        self.assertNotEqual(p.item, constants.UNKNOWN_ITEM)

    def test_does_not_guess_item_when_it_is_none(self):
        p = Pokemon('pikachu', 100)
        p.item = None
        p.update_item_for_random_battles()
        self.assertIsNone(p.item)

    def test_does_not_guess_item_when_it_exists(self):
        p = Pokemon('pikachu', 100)
        p.item = 'some_item'
        p.update_item_for_random_battles()
        self.assertEqual('some_item', p.item)

    def test_guesses_most_likely_item(self):
        self.get_sets_mock.return_value = {
            constants.ITEMS: {
                "item_one": 10,
                "item_two": 9
            }
        }
        p = Pokemon('pikachu', 100)
        p.item = constants.UNKNOWN_ITEM
        p.update_item_for_random_battles()
        self.assertEqual("item_one", p.item)


class TestGetAbilityForRandomBattles(unittest.TestCase):
    def setUp(self):
        self.get_sets_patch = mock.patch('data.helpers._get_random_battle_set')
        self.addCleanup(self.get_sets_patch.stop)
        self.get_sets_mock = self.get_sets_patch.start()

        self.get_sets_mock.return_value = {
            constants.ABILITIES: {
                "ability": 33
            }
        }

    def test_gets_item_when_item_is_unknown(self):
        p = Pokemon('pikachu', 100)
        p.ability = None
        p.update_ability_for_random_battles()
        self.assertIsNotNone(p.ability)

    def test_does_not_get_ability_when_it_exists(self):
        p = Pokemon('pikachu', 100)
        p.ability = "some_ability"
        p.update_ability_for_random_battles()
        self.assertEqual("some_ability", p.ability)

    def test_gets_most_likely_ability(self):
        self.get_sets_mock.return_value = {
            constants.ABILITIES: {
                "immunity": 10,
                "sandveil": 9
            }
        }
        p = Pokemon('gligar', 100)
        p.ability = None
        p.update_ability_for_random_battles()
        self.assertEqual("immunity", p.ability)

    def test_no_abilities_does_not_error(self):
        self.get_sets_mock.return_value = {
            constants.ABILITIES: {}
        }
        p = Pokemon('gligar', 100)
        p.ability = None
        p.update_ability_for_random_battles()
        self.assertEqual(None, p.ability)


class TestGetMovesForRandomBattles(unittest.TestCase):
    def setUp(self):
        self.get_sets_patch = mock.patch('data.helpers._get_random_battle_set')
        self.addCleanup(self.get_sets_patch.stop)
        self.get_sets_mock = self.get_sets_patch.start()

    def test_gets_all_possible_moves_when_none_have_yet_been_revealed(self):
        self.get_sets_mock.return_value = {
            constants.SETS: {
                "grassknot|hiddenpowerice60|voltswitch|volttackle": 16,
                "grassknot|hiddenpowerice60|irontail|volttackle": 33
            }
        }
        expected_moves = [
            Move("grassknot"),
            Move("hiddenpowerice60"),
            Move("voltswitch"),
            Move("volttackle"),
            Move("irontail")
        ]
        p = Pokemon('pikachu', 100)
        p.moves = list()
        p.update_moves_for_random_battles()
        self.assertEqual(expected_moves, p.moves)

    def test_gets_all_moves_when_an_unknown_set_is_there(self):
        self.get_sets_mock.return_value = {
            constants.SETS: {
                "grassknot|hiddenpowerice60|voltswitch|volttackle": 16,
                "grassknot|hiddenpowerice60|irontail|poisonjab": 33
            },
            constants.MOVES: {
                "grassknot": 1,
                "hiddenpowerice60": 1,
                "voltswitch": 1,
                "volttackle": 1,
                "irontail": 1,
                "poisonjab": 1,
            }
        }
        expected_moves = [
            Move("tackle"),
            Move("grassknot"),
            Move("hiddenpowerice60"),
            Move("voltswitch"),
            Move("volttackle"),
            Move("irontail"),
            Move("poisonjab")
        ]
        p = Pokemon('pikachu', 100)
        p.moves = [Move("tackle")]
        p.update_moves_for_random_battles()
        self.assertEqual(expected_moves, p.moves)

    def test_gets_only_set_available(self):
        self.get_sets_mock.return_value = {
            constants.SETS: {
                "grassknot|hiddenpowerice60|voltswitch|volttackle": 16,
                "grassknot|hiddenpowerice60|irontail|volttackle": 33
            }
        }
        expected_moves = [
            Move("irontail"),
            Move("grassknot"),
            Move("hiddenpowerice60"),
            Move("volttackle"),
        ]
        p = Pokemon('pikachu', 100)
        p.moves = [Move('irontail')]
        p.update_moves_for_random_battles()
        self.assertEqual(expected_moves, p.moves)

    def test_gets_combination_of_two_sets_available(self):
        self.get_sets_mock.return_value = {
            constants.SETS: {
                "grassknot|hiddenpowerice60|voltswitch|volttackle": 16,
                "grassknot|hiddenpowerice60|irontail|volttackle": 33
            }
        }
        expected_moves = [
            Move("grassknot"),
            Move("hiddenpowerice60"),
            Move("voltswitch"),
            Move("volttackle"),
            Move("irontail")
        ]
        p = Pokemon('pikachu', 100)
        p.moves = [Move('grassknot')]
        p.update_moves_for_random_battles()
        self.assertEqual(expected_moves, p.moves)

    def test_gets_combination_of_two_sets_available_but_not_the_third(self):
        self.get_sets_mock.return_value = {
            constants.SETS: {
                "grassknot|hiddenpowerice60|voltswitch|volttackle": 16,
                "grassknot|hiddenpowerice60|irontail|volttackle": 33,
                "tackle|hiddenpowerice60|irontail|volttackle": 33
            }
        }
        expected_moves = [
            Move("grassknot"),
            Move("hiddenpowerice60"),
            Move("voltswitch"),
            Move("volttackle"),
            Move("irontail")
        ]
        p = Pokemon('pikachu', 100)
        p.moves = [Move('grassknot')]
        p.update_moves_for_random_battles()
        self.assertEqual(expected_moves, p.moves)

    def test_three_revealed_moves_gets_only_the_possible_sets(self):
        self.get_sets_mock.return_value = {
            constants.SETS: {
                "grassknot|hiddenpowerice60|voltswitch|volttackle": 16,
                "grassknot|hiddenpowerice60|irontail|volttackle": 33,
                "tackle|hiddenpowerice60|irontail|volttackle": 33
            }
        }
        expected_moves = [
            Move('grassknot'),
            Move('hiddenpowerice60'),
            Move('volttackle'),
            Move('voltswitch'),
            Move('irontail'),
        ]
        p = Pokemon('pikachu', 100)
        p.moves = [
            Move('grassknot'),
            Move('hiddenpowerice60'),
            Move('volttackle'),
        ]
        p.update_moves_for_random_battles()
        self.assertEqual(expected_moves, p.moves)

    def test_no_new_moves_are_added_when_4_have_been_revealed(self):
        self.get_sets_mock.return_value = {
            constants.SETS: {
                "grassknot|hiddenpowerice60|voltswitch|volttackle": 16,
                "grassknot|hiddenpowerice60|irontail|volttackle": 33,
                "tackle|hiddenpowerice60|irontail|volttackle": 33
            }
        }
        expected_moves = [
            Move("grassknot"),
            Move("hiddenpowerice60"),
            Move("voltswitch"),
            Move("volttackle"),
        ]
        p = Pokemon('pikachu', 100)
        p.moves = [
            Move("grassknot"),
            Move("hiddenpowerice60"),
            Move("voltswitch"),
            Move("volttackle"),
        ]
        p.update_moves_for_random_battles()
        self.assertEqual(expected_moves, p.moves)
