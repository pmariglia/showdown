import unittest
from data import all_move_json
import constants
from showdown.engine.special_effects.moves.modify_move import modify_attack_being_used


class TestSuckerPunch(unittest.TestCase):
    def setUp(self):
        self.state = dict()
        self.move = all_move_json["suckerpunch"]
        self.attacking_pokemon = None
        self.defending_pokemon = None

    def test_suckerpunch_misses_when_opponent_selects_non_damaging_move(self):
        opponent_move = all_move_json['substitute']
        expected_accuracy = 0
        new_move = modify_attack_being_used(self.move, opponent_move, self.attacking_pokemon, self.defending_pokemon, True, None, None)
        self.assertEqual(expected_accuracy, new_move[constants.ACCURACY])

    def test_suckerpunch_misses_verus_a_switch(self):
        opponent_move = {
            constants.SWITCH_STRING: "pokemon"
        }
        expected_accuracy = 0
        new_move = modify_attack_being_used(self.move, opponent_move, self.attacking_pokemon, self.defending_pokemon, False, None, None)
        self.assertEqual(expected_accuracy, new_move[constants.ACCURACY])

    def test_suckerpunch_misses_when_it_is_the_second_move(self):
        opponent_move = all_move_json['extremespeed']
        expected_accuracy = 0
        new_move = modify_attack_being_used(self.move, opponent_move, self.attacking_pokemon, self.defending_pokemon, False, None, None)
        self.assertEqual(expected_accuracy, new_move[constants.ACCURACY])

    def test_suckerpunch_hits_when_opponent_tries_to_attack(self):
        opponent_move = all_move_json['tackle']
        expected_accuracy = 100
        new_move = modify_attack_being_used(self.move, opponent_move, self.attacking_pokemon, self.defending_pokemon, True, None, None)
        self.assertEqual(expected_accuracy, new_move[constants.ACCURACY])
