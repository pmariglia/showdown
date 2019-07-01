import unittest

from showdown.decide.decide import pick_safest


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
