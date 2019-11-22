import unittest
from unittest import mock

from showdown.engine.select_best_move import pick_safest
from showdown.battle_bots.nash_equilibrium.main import get_weighted_choices_from_multiple_score_lookups


class TestPickSafest(unittest.TestCase):
    def test_returns_only_options_from_one_item_dictionary(self):
        score_lookup = {
            ("a", "b"): 100
        }

        safest = pick_safest(score_lookup)
        expected_result = (("a", "b"), 100)

        self.assertEqual(expected_result, safest)

    def test_returns_better_option_for_two_different_moves(self):
        score_lookup = {
            ("a", "b"): 100,
            ("c", "b"): 200
        }

        safest = pick_safest(score_lookup)
        expected_result = (("c", "b"), 200)

        self.assertEqual(expected_result, safest)

    def test_returns_option_with_the_lowest_minimum_in_2_by_2(self):
        score_lookup = {
            ("a", "x"): 100,
            ("a", "y"): -100,
            ("c", "x"): 200,
            ("c", "y"): -200,
        }

        safest = pick_safest(score_lookup)
        expected_result = (("a", "y"), -100)

        self.assertEqual(expected_result, safest)

    def test_returns_option_with_the_lowest_minimum_in_3_by_3(self):
        score_lookup = {
            ("a", "x"): 100,
            ("a", "y"): -100,
            ("a", "z"): -500,
            ("c", "x"): 200,
            ("c", "y"): -200,
            ("c", "z"): -400,
        }

        safest = pick_safest(score_lookup)
        expected_result = (("c", "z"), -400)

        self.assertEqual(expected_result, safest)


class TestGetWeightedChoices(unittest.TestCase):
    def setUp(self):
        self.find_nash_equilibrium_patch = mock.patch('showdown.battle_bots.nash_equilibrium.main.find_nash_equilibrium')
        self.addCleanup(self.find_nash_equilibrium_patch.stop)
        self.find_nash_mock = self.find_nash_equilibrium_patch.start()

    def test_returns_even_distribution_between_two_pure_strategies(self):
        self.find_nash_mock.side_effect = [
            (['a', 'b'], ['c', 'd'], [1, 0], [0, 1], None),
            (['a', 'b'], ['c', 'd'], [0, 1], [0, 1], None),
        ]
        # choice is 'a' 100% of the time
        sl1 = {
            ('a', 'c'): 10,
            ('a', 'd'): 10,
            ('b', 'c'): -10,
            ('b', 'd'): -10,
        }
        # choice is 'b' 100% of the time
        sl2 = {
            ('a', 'c'): -10,
            ('a', 'd'): -10,
            ('b', 'c'): 10,
            ('b', 'd'): 10,
        }

        score_lookups = [sl1, sl2]

        choices = get_weighted_choices_from_multiple_score_lookups(score_lookups)
        expected_choices = [('a', 0.5), ('b', 0.5)]

        self.assertEqual(expected_choices, choices)

    def test_returns_correct_values_for_score_lookups_with_different_moves(self):
        self.find_nash_mock.side_effect = [
            (['a', 'b'], ['c', 'd'], [1, 0], [0, 1], None),
            (['e', 'f'], ['g', 'h'], [0, 1], [0, 1], None),
        ]
        # choice is 'a' 100% of the time
        sl1 = {
            ('a', 'c'): 10,
            ('a', 'd'): 10,
            ('b', 'c'): -10,
            ('b', 'd'): -10,
        }
        # choice is 'f' 100% of the time
        sl2 = {
            ('e', 'g'): -10,
            ('e', 'g'): -10,
            ('f', 'h'): 10,
            ('f', 'h'): 10,
        }

        score_lookups = [sl1, sl2]

        choices = get_weighted_choices_from_multiple_score_lookups(score_lookups)
        expected_choices = [('a', 0.5), ('b', 0), ('e', 0), ('f', 0.5)]

        self.assertEqual(expected_choices, choices)

    def test_returns_correct_values_for_score_lookups_with_different_moves_containing_some_overlap(self):
        self.find_nash_mock.side_effect = [
            (['a', 'b'], ['c', 'd'], [1, 0], [0, 1], None),
            (['a', 'z'], ['g', 'h'], [0.5, 0.5], [0, 1], None),
        ]
        sl1 = {
            ('a', 'c'): 10,
            ('a', 'd'): 10,
            ('b', 'c'): -10,
            ('b', 'd'): -10,
        }
        sl2 = {
            ('a', 'g'): -10,
            ('a', 'g'): -10,
            ('z', 'h'): 10,
            ('z', 'h'): 10,
        }

        score_lookups = [sl1, sl2]

        choices = get_weighted_choices_from_multiple_score_lookups(score_lookups)
        expected_choices = [('a', 0.75), ('b', 0), ('z', 0.25)]

        self.assertEqual(expected_choices, choices)

    def test_opponent_moves_overlapping(self):
        self.find_nash_mock.side_effect = [
            (['a', 'b'], ['c', 'd'], [1, 0], [0, 1], None),
            (['a', 'b'], ['c', 'e'], [0.5, 0.5], [0.5, 0.5], None),
        ]
        sl1 = {
            ('a', 'c'): 10,
            ('a', 'd'): 10,
            ('b', 'c'): -10,
            ('b', 'd'): -10,
        }
        sl2 = {
            ('a', 'c'): 1,
            ('a', 'e'): -1,
            ('b', 'c'): -1,
            ('b', 'e'): 1,
        }

        score_lookups = [sl1, sl2]

        choices = get_weighted_choices_from_multiple_score_lookups(score_lookups)
        expected_choices = [('a', 0.75), ('b', 0.25)]

        self.assertEqual(expected_choices, choices)
