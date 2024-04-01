import unittest

from data.pkmn_sets import TeamDatasets, SmogonSets


class TestTeamDatasets(unittest.TestCase):
    def setUp(self):
        TeamDatasets.__init__()

    def test_team_datasets_initialize_gen5(self):
        TeamDatasets.initialize(
            "gen5ou",
            {"azelf", "heatran", "rotomwash", "scizor", "tyranitar", "volcarona"},
        )
        self.assertEqual("gen5ou", TeamDatasets.pkmn_mode)
        self.assertEqual(6, len(TeamDatasets.pkmn_sets))

    def test_team_datasets_initialize_gen4(self):
        TeamDatasets.initialize(
            "gen4ou",
            {"azelf", "heatran", "rotomwash", "scizor", "tyranitar", "dragonite"},
        )
        self.assertEqual("gen4ou", TeamDatasets.pkmn_mode)
        self.assertEqual(6, len(TeamDatasets.pkmn_sets))

    def test_team_datasets_add_new_pokemon(self):
        TeamDatasets.initialize("gen4ou", {"dragonite"})
        self.assertNotIn("azelf", TeamDatasets.pkmn_sets)
        TeamDatasets.add_new_pokemon("azelf")
        self.assertIn("azelf", TeamDatasets.pkmn_sets)

    def test_pokemon_not_in_team_datasets_does_not_error(self):
        TeamDatasets.initialize("gen4ou", {"dragonite"})
        self.assertNotIn("azelf", TeamDatasets.pkmn_sets)
        TeamDatasets.add_new_pokemon("not_in_team_datasets")
        self.assertNotIn("not_in_team_datasets", TeamDatasets.pkmn_sets)

    def test_smogon_datasets_add_new_pokemon_with_cosmetic_forme(self):
        TeamDatasets.initialize("gen4ou", {"dragonite"})
        self.assertNotIn("gastrodon", TeamDatasets.pkmn_sets)
        self.assertNotIn("gastrodoneast", TeamDatasets.pkmn_sets)
        TeamDatasets.add_new_pokemon("gastrodoneast")
        self.assertIn("gastrodoneast", TeamDatasets.pkmn_sets)
        self.assertNotIn("gastrodon", TeamDatasets.pkmn_sets)

    def test_removing_initial_set_does_not_change_existing_pokemon_sets(self):
        TeamDatasets.initialize("gen4ou", {"dragonite"})
        initial_len = len(TeamDatasets.pkmn_sets["dragonite"])
        TeamDatasets.pkmn_sets["dragonite"].pop(-1)
        len_after_pop = len(TeamDatasets.pkmn_sets["dragonite"])
        self.assertNotEqual(initial_len, len_after_pop)
        TeamDatasets.add_new_pokemon("azelf")
        self.assertEqual(len_after_pop, len(TeamDatasets.pkmn_sets["dragonite"]))


class TestSmogonDatasets(unittest.TestCase):
    def setUp(self):
        SmogonSets.__init__()

    def test_smogon_datasets_initialize_gen5(self):
        SmogonSets.initialize(
            "gen5ou",
            {"azelf", "heatran", "scizor", "tyranitar", "volcarona"},
        )
        self.assertEqual("gen5ou", SmogonSets.pkmn_mode)
        self.assertEqual(5, len(SmogonSets.pkmn_sets))

    def test_smogon_datasets_initialize_gen4(self):
        SmogonSets.initialize(
            "gen4ou",
            {"azelf", "heatran", "scizor", "tyranitar", "dragonite"},
        )
        self.assertEqual("gen4ou", SmogonSets.pkmn_mode)
        self.assertEqual(5, len(SmogonSets.pkmn_sets))

    def test_smogon_datasets_add_new_pokemon(self):
        SmogonSets.initialize("gen4ou", {"dragonite"})
        self.assertNotIn("azelf", SmogonSets.pkmn_sets)
        SmogonSets.add_new_pokemon("azelf")
        self.assertIn("azelf", SmogonSets.pkmn_sets)

    def test_smogon_datasets_add_new_pokemon_with_cosmetic_forme(self):
        SmogonSets.initialize("gen4ou", {"dragonite"})
        self.assertNotIn("gastrodon", SmogonSets.pkmn_sets)
        self.assertNotIn("gastrodoneast", SmogonSets.pkmn_sets)
        SmogonSets.add_new_pokemon("gastrodoneast")
        self.assertNotIn("gastrodoneast", SmogonSets.pkmn_sets)
        self.assertIn("gastrodon", SmogonSets.pkmn_sets)

    def test_removing_initial_set_does_not_change_existing_pokemon_sets(self):
        SmogonSets.initialize("gen4ou", {"dragonite"})
        initial_len = len(SmogonSets.pkmn_sets["dragonite"])
        SmogonSets.pkmn_sets["dragonite"].pop(-1)
        len_after_pop = len(SmogonSets.pkmn_sets["dragonite"])
        self.assertNotEqual(initial_len, len_after_pop)
        SmogonSets.add_new_pokemon("azelf")
        self.assertEqual(len_after_pop, len(SmogonSets.pkmn_sets["dragonite"]))
