import unittest
from unittest import mock

import constants

from showdown.battle import Pokemon
from showdown.battle import Move


class TestPokemonInit(unittest.TestCase):
    def test_alternate_pokemon_name_initializes(self):
        name = 'florgeswhite'
        Pokemon(name, 100)


class TestGetPossibleMoves(unittest.TestCase):
    def test_gets_four_moves_when_none_are_known(self):
        p = Pokemon('pikachu', 100)

        moves = [
            ('move1', 95),
            ('move2', 94),
            ('move3', 93),
            ('move4', 92)
        ]

        moves = p.get_possible_moves(moves)

        expected_result = (
            ['move1', 'move2', 'move3', 'move4'],
            []
        )

        self.assertEqual(expected_result, moves)

    def test_gets_only_first_3_moves_when_one_move_is_known(self):
        p = Pokemon('pikachu', 100)
        p.moves = [
            Move('tackle')
        ]

        moves = [
            ('move1', 95),
            ('move2', 94),
            ('move3', 93),
            ('move4', 92)
        ]

        moves = p.get_possible_moves(moves)

        expected_result = (
            ['move1', 'move2', 'move3'],
            []
        )

        self.assertEqual(expected_result, moves)

    def test_chance_moves_are_not_affected_by_known_moves(self):
        p = Pokemon('pikachu', 100)
        p.moves = [
            Move('tackle')
        ]

        moves = [
            ('move1', 95),
            ('move2', 40),
            ('move3', 40),
            ('move4', 40)
        ]

        moves = p.get_possible_moves(moves)

        expected_result = (
            ['move1'],
            ['move2', 'move3', 'move4']
        )

        self.assertEqual(expected_result, moves)

    def test_chance_moves_are_not_guessed_if_known_plus_expected_equals_four(self):
        p = Pokemon('pikachu', 100)

        p.moves = [
            Move('tackle'),
            Move('splash'),
            Move('stringshot'),
        ]
        moves = [
            ('move1', 95),
            ('move2', 40),
            ('move3', 40),
            ('move4', 40)
        ]

        moves = p.get_possible_moves(moves)

        expected_result = (
            ['move1'],
            []
        )

        self.assertEqual(expected_result, moves)

    def test_does_not_get_already_revealed_move(self):
        p = Pokemon('pikachu', 100)

        p.moves = [
            Move('tackle'),
            Move('splash'),
            Move('stringshot'),
        ]
        moves = [
            ('tackle', 95),
            ('splash', 40),
            ('stringshot', 40),
            ('move4', 40)
        ]

        moves = p.get_possible_moves(moves)

        expected_result = (
            [],
            ['move4']
        )

        self.assertEqual(expected_result, moves)

    def test_does_not_get_already_revealed_move_and_guesses_expected_moves(self):
        p = Pokemon('pikachu', 100)

        p.moves = [
            Move('tackle'),
            Move('stringshot'),
        ]
        moves = [
            ('tackle', 95),
            ('splash', 85),
            ('stringshot', 40),
            ('move4', 40)
        ]

        moves = p.get_possible_moves(moves)

        expected_result = (
            ['splash'],
            ['move4']
        )

        self.assertEqual(expected_result, moves)

    def test_expected_plus_known_does_not_exceed_four_with_chance_moves(self):
        p = Pokemon('pikachu', 100)

        p.moves = [
            Move('tackle'),
            Move('splash'),
            Move('stringshot'),
        ]
        moves = [
            ('move1', 95),
            ('move2', 80),
            ('move3', 40),
            ('move4', 40)
        ]

        moves = p.get_possible_moves(moves)

        expected_result = (
            ['move1'],
            []
        )

        self.assertEqual(expected_result, moves)

    def test_gets_less_likely_moves_as_chance_moves(self):
        p = Pokemon('pikachu', 100)

        moves = [
            ('move1', 95),
            ('move2', 94),
            ('move3', 50),
            ('move4', 25),
            ('move5', 25),
            ('move6', 25),
            ('move7', 25)
        ]

        moves = p.get_possible_moves(moves)

        expected_result = (
            ['move1', 'move2'],
            ['move3', 'move4', 'move5', 'move6', 'move7']
        )

        self.assertEqual(expected_result, moves)

    def test_does_not_get_moves_below_threshold(self):
        p = Pokemon('pikachu', 100)

        moves = [
            ('move1', 95),
            ('move2', 94),
            ('move3', 50),
            ('move4', 25),
            ('move5', 25),
            ('move6', 15),
            ('move7', 15)
        ]

        moves = p.get_possible_moves(moves)

        expected_result = (
            ['move1', 'move2'],
            ['move3', 'move4', 'move5']
        )

        self.assertEqual(expected_result, moves)


class TestGetPossibleAbilities(unittest.TestCase):
    def test_gets_revealed_item_when_item_is_revealed(self):
        p = Pokemon('pikachu', 100)
        p.ability = 'static'

        abilities = [
            ('static', 50),
            ('voltabsorb', 50),
        ]

        possible_items = p.get_possible_abilities(abilities)

        expected_items = ['static']

        self.assertEqual(expected_items, possible_items)

    def test_gets_multiple_abilities(self):
        p = Pokemon('pikachu', 100)
        p.ability = None

        abilities = [
            ('static', 50),
            ('voltabsorb', 50),
        ]

        possible_items = p.get_possible_abilities(abilities)

        expected_items = ['static', 'voltabsorb']

        self.assertEqual(expected_items, possible_items)

    def test_does_not_exceed_threshold(self):
        p = Pokemon('pikachu', 100)
        p.ability = None

        abilities = [
            ('static', 80),
            ('voltabsorb', 20),
        ]

        possible_items = p.get_possible_abilities(abilities)

        expected_items = ['static']

        self.assertEqual(expected_items, possible_items)

    def test_does_not_get_low_percentage_ability(self):
        p = Pokemon('pikachu', 100)
        p.ability = None

        abilities = [
            ('static', 65),
            ('other_ability1', 5),
            ('other_ability2', 5),
            ('other_ability3', 5),
            ('other_ability4', 5),
            ('other_ability5', 5),
            ('other_ability6', 5),
            ('other_ability7', 5),
        ]

        possible_items = p.get_possible_abilities(abilities)

        expected_items = ['static']

        self.assertEqual(expected_items, possible_items)

    def test_ignored_ability_in_pass_abilities(self):
        p = Pokemon('pikachu', 100)
        p.ability = None

        abilities = [
            ('static', 50),
            ('pressure', 50),  # pass-ability; it reveals itself so do not guess
        ]

        possible_items = p.get_possible_abilities(abilities)

        expected_items = ['static']

        self.assertEqual(expected_items, possible_items)


class TestGetPossibleItems(unittest.TestCase):
    def test_gets_revealed_item_when_item_is_revealed(self):
        p = Pokemon('pikachu', 100)
        p.item = 'lightball'

        items = [
            ('lightball', 50),
            ('leftovers', 50),
        ]

        possible_items = p.get_possible_items(items)

        expected_items = ['lightball']

        self.assertEqual(expected_items, possible_items)

    def test_gets_none_when_item_is_none(self):
        p = Pokemon('pikachu', 100)
        p.item = None

        items = [
            ('lightball', 50),
            ('leftovers', 50),
        ]

        possible_items = p.get_possible_items(items)

        expected_items = [None]

        self.assertEqual(expected_items, possible_items)

    def test_gets_two_items_when_they_are_equally_likely(self):
        p = Pokemon('pikachu', 100)
        p.item = constants.UNKNOWN_ITEM

        items = [
            ('lightball', 50),
            ('other_item', 50),
        ]

        possible_items = p.get_possible_items(items)

        expected_items = [
            'lightball',
            'other_item'
        ]

        self.assertEqual(expected_items, possible_items)

    def test_stops_once_cumulative_percentage_exceeds_limit(self):
        p = Pokemon('pikachu', 100)
        p.item = constants.UNKNOWN_ITEM

        items = [
            ('lightball', 50),
            ('other_item', 30),
            ('another_item', 20),
        ]

        possible_items = p.get_possible_items(items)

        expected_items = [
            'lightball',
            'other_item'
        ]

        self.assertEqual(expected_items, possible_items)

    def test_works_with_one_item(self):
        p = Pokemon('pikachu', 100)
        p.item = constants.UNKNOWN_ITEM

        items = [
            ('lightball', 100),
        ]

        possible_items = p.get_possible_items(items)

        expected_items = [
            'lightball',
        ]

        self.assertEqual(expected_items, possible_items)

    def test_ignores_item_in_pass_items(self):
        p = Pokemon('pikachu', 100)
        p.item = constants.UNKNOWN_ITEM

        items = [
            ('lightball', 50),
            ('leftovers', 50),  # leftovers is ignored because it reveals itself
        ]

        possible_items = p.get_possible_items(items)

        expected_items = [
            'lightball',
        ]

        self.assertEqual(expected_items, possible_items)


class TestConvertToMega(unittest.TestCase):
    def setUp(self):
        self.get_mega_name_patch = mock.patch('showdown.battle.get_mega_pkmn_name')
        self.addCleanup(self.get_mega_name_patch.stop)
        self.get_mega_name_mock = self.get_mega_name_patch.start()

        self.pkmn_sets_patch = mock.patch('showdown.battle.data')
        self.addCleanup(self.pkmn_sets_patch.stop)
        self.pkmn_sets_mock = self.pkmn_sets_patch.start()

    def test_changes_venusaur_to_its_mega_form(self):
        self.get_mega_name_mock.return_value = 'venusaurmega'

        pkmn = Pokemon('venusaur', 100)
        pkmn.try_convert_to_mega()
        self.assertEqual('venusaurmega', pkmn.name)

    def test_preserves_previous_hitpoints(self):
        self.get_mega_name_mock.return_value = 'venusaurmega'

        pkmn = Pokemon('venusaur', 100)
        pkmn.hp = 1
        pkmn.try_convert_to_mega()
        self.assertEqual(1, pkmn.hp)

    def test_preserves_previous_status_condition(self):
        self.get_mega_name_mock.return_value = 'venusaurmega'

        pkmn = Pokemon('venusaur', 100)
        pkmn.status = constants.BURN
        pkmn.try_convert_to_mega()
        self.assertEqual(constants.BURN, pkmn.status)

    def test_preserves_previous_boosts(self):
        self.get_mega_name_mock.return_value = 'venusaurmega'

        pkmn = Pokemon('venusaur', 100)
        pkmn.boosts[constants.ATTACK] = 1
        pkmn.try_convert_to_mega()
        self.assertEqual(1, pkmn.boosts[constants.ATTACK])

    def test_preserves_previous_moves(self):
        self.get_mega_name_mock.return_value = 'venusaurmega'

        pkmn = Pokemon('venusaur', 100)
        pkmn.moves = [
            {'1': '2'},
            {'3': '4'},
            {'5': '6'},
            {'7': '8'},
        ]
        pkmn.try_convert_to_mega()
        expected_moves = [
            {'1': '2'},
            {'3': '4'},
            {'5': '6'},
            {'7': '8'},
        ]
        self.assertEqual(expected_moves, pkmn.moves)

    def test_converts_when_it_is_in_sets_lookup_and_check_sets_is_true(self):
        self.pkmn_sets_mock.pokemon_sets = {
            "venusaurmega": {}
        }
        self.get_mega_name_mock.return_value = 'venusaurmega'

        pkmn = Pokemon('venusaur', 100)
        pkmn.try_convert_to_mega(check_in_sets=True)
        self.assertEqual("venusaurmega", pkmn.name)

    def test_converts_when_it_is_not_in_sets_lookup_and_check_sets_is_false(self):
        self.pkmn_sets_mock.pokemon_sets = {}
        self.get_mega_name_mock.return_value = 'venusaurmega'

        pkmn = Pokemon('venusaur', 100)
        pkmn.try_convert_to_mega(check_in_sets=False)
        self.assertEqual("venusaurmega", pkmn.name)

    def test_does_not_convert_when_it_is_not_in_sets_lookup_and_check_sets_is_true(self):
        self.pkmn_sets_mock.pokemon_sets = {}
        self.get_mega_name_mock.return_value = 'venusaurmega'

        pkmn = Pokemon('venusaur', 100)
        pkmn.try_convert_to_mega(check_in_sets=True)
        self.assertEqual("venusaur", pkmn.name)

    def test_does_not_convert_if_item_is_revealed(self):
        self.pkmn_sets_mock.pokemon_sets = {}
        self.get_mega_name_mock.return_value = 'venusaurmega'

        pkmn = Pokemon('venusaur', 100)
        pkmn.item = 'leftovers'
        pkmn.try_convert_to_mega()
        self.assertEqual("venusaur", pkmn.name)

    def test_does_not_convert_if_item_is_none(self):
        self.pkmn_sets_mock.pokemon_sets = {}
        self.get_mega_name_mock.return_value = 'venusaurmega'

        pkmn = Pokemon('venusaur', 100)
        pkmn.item = None
        pkmn.try_convert_to_mega()
        self.assertEqual("venusaur", pkmn.name)
