from unittest import TestCase

import constants
from data.team_datasets import _TeamDatasets, PokemonSet, PokemonMoveset
from showdown.battle import Pokemon, Move, StatRange


class TestTeamDatasets(TestCase):
    def setUp(self):
        self.team_datasets = _TeamDatasets()

    def test_populating_datasets_from_file_with_empty_list(self):
        self.team_datasets.set_pokemon_sets([])

    def test_populating_datasets_using_known_pokemon(self):
        self.team_datasets.set_pokemon_sets(["garchomp"])
        self.assertIn("garchomp", self.team_datasets.pokemon_sets)

    def test_predict_set_returns_pokemonset(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|jolly|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 1
            }
        }
        garchomp = Pokemon("garchomp", 100)
        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)

        expected_set = PokemonSet(
            "water",
            "roughskin",
            "rockyhelmet",
            "jolly",
            (0, 0, 252, 0, 4, 252),
            PokemonMoveset(("dragontail", "earthquake", "spikes", "stealthrock"))
        )

        self.assertEqual(expected_set, predicted_garchomp_set)

    def test_predict_set_returns_more_common_set(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|jolly|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 1,
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
                "water|roughskin|rockyhelmet|timid|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 3,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)

        expected_set = PokemonSet(
            "water",
            "roughskin",
            "rockyhelmet",
            "adamant",  # adamant is more common
            (0, 0, 252, 0, 4, 252),
            PokemonMoveset(("dragontail", "earthquake", "spikes", "stealthrock"))
        )

        self.assertEqual(expected_set, predicted_garchomp_set)

    def test_predict_set_returns_none_when_no_set_matches(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|jolly|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 1,
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.moves = [
            Move("watergun")  # none of the above sets have this
        ]

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        self.assertIsNone(predicted_garchomp_set)

    def test_predict_set_returns_set_if_moves_are_a_subset(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|jolly|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 1,
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.moves = [
            Move("earthquake")
        ]

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)

        expected_set = PokemonSet(
            "water",
            "roughskin",
            "rockyhelmet",
            "adamant",
            (0, 0, 252, 0, 4, 252),
            PokemonMoveset(("dragontail", "earthquake", "spikes", "stealthrock"))
        )

        self.assertEqual(expected_set, predicted_garchomp_set)

    def test_matching_ability_returns_valid_set(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.ability = "roughskin"

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        expected_set = PokemonSet(
            "water",
            "roughskin",
            "rockyhelmet",
            "adamant",
            (0, 0, 252, 0, 4, 252),
            PokemonMoveset(("dragontail", "earthquake", "spikes", "stealthrock"))
        )
        self.assertEqual(expected_set, predicted_garchomp_set)

    def test_mismatching_ability_means_set_is_not_returned(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.ability = "sandforce"

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        self.assertIsNone(predicted_garchomp_set)

    def test_item_being_none_allows_set_to_match(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.item = None

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        expected_set = PokemonSet(
            "water",
            "roughskin",
            "rockyhelmet",
            "adamant",
            (0, 0, 252, 0, 4, 252),
            PokemonMoveset(("dragontail", "earthquake", "spikes", "stealthrock"))
        )
        self.assertEqual(expected_set, predicted_garchomp_set)

    def test_item_being_unknown_allows_set_to_match(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.item = constants.UNKNOWN_ITEM

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        expected_set = PokemonSet(
            "water",
            "roughskin",
            "rockyhelmet",
            "adamant",
            (0, 0, 252, 0, 4, 252),
            PokemonMoveset(("dragontail", "earthquake", "spikes", "stealthrock"))
        )
        self.assertEqual(expected_set, predicted_garchomp_set)

    def test_item_mismatching_does_not_match_set(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.item = "leftovers"

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        self.assertIsNone(predicted_garchomp_set)

    def test_item_matching_matches_set(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.item = "rockyhelmet"

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        expected_set = PokemonSet(
            "water",
            "roughskin",
            "rockyhelmet",
            "adamant",
            (0, 0, 252, 0, 4, 252),
            PokemonMoveset(("dragontail", "earthquake", "spikes", "stealthrock"))
        )
        self.assertEqual(expected_set, predicted_garchomp_set)

    def test_omits_ability_mismatch_when_flag_is_unset(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.ability = "some_mismatch"

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp, match_ability=False)
        expected_set = PokemonSet(
            "water",
            "roughskin",
            "rockyhelmet",
            "adamant",
            (0, 0, 252, 0, 4, 252),
            PokemonMoveset(("dragontail", "earthquake", "spikes", "stealthrock"))
        )
        self.assertEqual(expected_set, predicted_garchomp_set)

    def test_omits_item_mismatch_when_flag_is_unset(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.item = "some_mismatch"

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp, match_item=False)
        expected_set = PokemonSet(
            "water",
            "roughskin",
            "rockyhelmet",
            "adamant",
            (0, 0, 252, 0, 4, 252),
            PokemonMoveset(("dragontail", "earthquake", "spikes", "stealthrock"))
        )
        self.assertEqual(expected_set, predicted_garchomp_set)

    def test_omits_item_and_ability_mismatch_when_both_flags_are_unset(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.ability = "some_mismatch"
        garchomp.item = "some_mismatch"

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp, match_item=False, match_ability=False)
        expected_set = PokemonSet(
            "water",
            "roughskin",
            "rockyhelmet",
            "adamant",
            (0, 0, 252, 0, 4, 252),
            PokemonMoveset(("dragontail", "earthquake", "spikes", "stealthrock"))
        )
        self.assertEqual(expected_set, predicted_garchomp_set)

    def test_does_not_set_lifeorb_if_can_have_lifeorb_is_false(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|lifeorb|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 2,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.can_have_life_orb = False

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        self.assertEqual("rockyhelmet", predicted_garchomp_set.item)

    def test_does_not_set_heavydutyboots_if_can_have_heavydutyboots_is_false(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|heavydutyboots|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 2,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.can_have_heavydutyboots = False

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        self.assertEqual("rockyhelmet", predicted_garchomp_set.item)

    def test_does_not_set_choice_item_if_can_have_can_have_choice_item_is_false(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|choiceband|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 2,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.can_have_choice_item = False

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        self.assertEqual("rockyhelmet", predicted_garchomp_set.item)

    def test_does_not_set_choice_band_if_can_not_have_band_is_true(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|choiceband|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 2,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.can_not_have_band = True

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        self.assertEqual("rockyhelmet", predicted_garchomp_set.item)

    def test_min_speed_check_invalidates_a_set(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|choiceband|adamant|0,252,252,0,4,0|dragontail|earthquake|spikes|stealthrock": 5,
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 2,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.speed_range = StatRange(min=300, max=float("inf"))  # should invalidate the first set

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        self.assertEqual("rockyhelmet", predicted_garchomp_set.item)

    def test_max_speed_check_invalidates_a_set(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|choiceband|adamant|0,252,252,0,4,0|dragontail|earthquake|spikes|stealthrock": 2,
                "water|roughskin|rockyhelmet|adamant|0,0,252,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.speed_range = StatRange(min=0, max=300)  # should invalidate the second set

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        self.assertEqual("choiceband", predicted_garchomp_set.item)

    def test_choicescarf_set_properly_fails_when_speed_range_is_present(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|choiceband|adamant|252,252,0,0,4,0|dragontail|earthquake|spikes|stealthrock": 2,
                "water|roughskin|choicescarf|adamant|0,252,0,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.speed_range = StatRange(min=0, max=400)  # should invalidate the choicescarf set

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        self.assertEqual("choiceband", predicted_garchomp_set.item)

    def test_boosting_ability_with_speed_range(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|choiceband|adamant|252,252,0,0,4,0|dragontail|earthquake|spikes|stealthrock": 2,
                "water|roughskin|choicescarf|adamant|0,252,0,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)
        garchomp.speed_range = StatRange(min=0, max=400)  # should invalidate the choicescarf set

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        self.assertEqual("choiceband", predicted_garchomp_set.item)

    def test_pkmn_not_existing_in_datasets_returns_none(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|choiceband|adamant|252,252,0,0,4,0|dragontail|earthquake|spikes|stealthrock": 2,
                "water|roughskin|choicescarf|adamant|0,252,0,0,4,252|dragontail|earthquake|spikes|stealthrock": 5,
            }
        }
        cinderace = Pokemon("cinderace", 100)

        predicted_cinderace_set = self.team_datasets.predict_set(cinderace)
        self.assertIsNone(predicted_cinderace_set)

    def test_pokemon_with_less_than_four_moves_works(self):
        self.team_datasets.pokemon_sets = {
            "garchomp": {
                "water|roughskin|choicescarf|adamant|0,252,0,0,4,252|dragontail|earthquake": 5,
            }
        }
        garchomp = Pokemon("garchomp", 100)

        expected_set = PokemonSet(
            "water",
            "roughskin",
            "choicescarf",
            "adamant",
            (0, 252, 0, 0, 4, 252),
            PokemonMoveset(("dragontail", "earthquake"))
        )

        predicted_garchomp_set = self.team_datasets.predict_set(garchomp)
        self.assertEqual(expected_set, predicted_garchomp_set)
