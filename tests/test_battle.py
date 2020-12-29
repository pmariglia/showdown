import unittest
from unittest import mock

import constants

from showdown.battle import LastUsedMove
from showdown.battle import Battle
from showdown.battle import Battler
from showdown.battle import Pokemon
from showdown.battle import Move


# so we can instantiate a Battle object for testing
Battle.__abstractmethods__ = set()


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

    def test_does_not_guess_choice_item_when_can_have_choice_item_flag_is_false(self):
        p = Pokemon('pikachu', 100)
        p.item = constants.UNKNOWN_ITEM
        p.can_have_choice_item = False

        items = [
            ('lightball', 50),
            ('choiceband', 50),  # should be ignored because flag is set to False
        ]

        possible_items = p.get_possible_items(items)

        expected_items = [
            'lightball',
        ]

        self.assertEqual(expected_items, possible_items)

    def test_can_not_have_choice_specs_flag_does_not_affect_choice_band_guess(self):
        p = Pokemon('pikachu', 100)
        p.item = constants.UNKNOWN_ITEM
        p.can_not_have_specs = True
        p.can_not_have_band = False

        items = [
            ('lightball', 50),
            ('choiceband', 50),  # should NOT be ignored because flag is set to False
                                 # choice_specs flag doesn't matter
        ]

        possible_items = p.get_possible_items(items)

        expected_items = [
            'lightball',
            'choiceband'
        ]

        self.assertEqual(expected_items, possible_items)

    def test_does_not_guess_choice_band_when_can_not_have_band_or_specs_is_true(self):
        p = Pokemon('pikachu', 100)
        p.item = constants.UNKNOWN_ITEM
        p.can_not_have_band = True

        items = [
            ('lightball', 50),
            ('choiceband', 50),  # should be ignored because flag is set to True
        ]

        possible_items = p.get_possible_items(items)

        expected_items = [
            'lightball',
        ]

        self.assertEqual(expected_items, possible_items)

    def test_guesses_choiceband_when_can_not_have_band_is_false(self):
        p = Pokemon('pikachu', 100)
        p.item = constants.UNKNOWN_ITEM
        p.can_not_have_band = False

        items = [
            ('lightball', 50),
            ('choiceband', 50),  # should NOT be ignored because flag is set to False
        ]

        possible_items = p.get_possible_items(items)

        expected_items = [
            'lightball',
            'choiceband'
        ]

        self.assertEqual(expected_items, possible_items)

    def test_does_not_guess_assultvest_when_can_have_assultvest_flag_is_false(self):
        p = Pokemon('pikachu', 100)
        p.item = constants.UNKNOWN_ITEM
        p.can_have_assaultvest = False

        items = [
            ('lightball', 50),
            ('assaultvest', 50),  # should be ignored because flag is set to False
        ]

        possible_items = p.get_possible_items(items)

        expected_items = [
            'lightball',
        ]

        self.assertEqual(expected_items, possible_items)

    def test_guesses_assultvest_when_can_have_assultvest_flag_is_true(self):
        p = Pokemon('pikachu', 100)
        p.item = constants.UNKNOWN_ITEM
        p.can_have_assaultvest = True

        items = [
            ('lightball', 50),
            ('assaultvest', 50),
        ]

        possible_items = p.get_possible_items(items)

        expected_items = [
            'lightball',
            'assaultvest'
        ]

        self.assertEqual(expected_items, possible_items)

    def test_guesses_choice_item_when_can_have_choice_item_flag_is_true(self):
        p = Pokemon('pikachu', 100)
        p.item = constants.UNKNOWN_ITEM
        p.can_have_choice_item = True

        items = [
            ('lightball', 50),
            ('choiceband', 50),  # should be guessed because flag is set to True
        ]

        possible_items = p.get_possible_items(items)

        expected_items = [
            'lightball',
            'choiceband'
        ]

        self.assertEqual(expected_items, possible_items)

    def test_guesses_life_orb(self):
        p = Pokemon('pikachu', 100)
        p.item = constants.UNKNOWN_ITEM
        p.can_have_life_orb = True

        items = [
            ('lifeorb', 50),
            ('lightball', 50),  # should be guessed because flag is set to True
        ]

        possible_items = p.get_possible_items(items)

        expected_items = [
            'lifeorb',
            'lightball'
        ]

        self.assertEqual(expected_items, possible_items)

    def test_does_not_guess_lifeorb_when_can_have_lifeorb_is_false(self):
        p = Pokemon('pikachu', 100)
        p.item = constants.UNKNOWN_ITEM
        p.can_have_life_orb = False

        items = [
            ('lifeorb', 50),
            ('lightball', 50),  # should be guessed because flag is set to True
        ]

        possible_items = p.get_possible_items(items)

        expected_items = [
            'lightball'
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


class TestBattlerActiveLockedIntoMove(unittest.TestCase):
    def setUp(self):
        self.battler = Battler()
        self.battler.active = Pokemon('pikachu', 100)
        self.battler.active.moves = [
            Move('thunderbolt'),
            Move('volttackle'),
            Move('agility'),
            Move('doubleteam'),
        ]

    def test_choice_item_with_previous_move_used_by_this_pokemon_returns_true(self):
        self.battler.active.item = 'choicescarf'
        self.battler.last_used_move = LastUsedMove(
            pokemon_name='pikachu',
            move='volttackle',
            turn=0
        )

        self.battler.lock_moves()

        self.assertFalse(self.battler.active.get_move('volttackle').disabled)

        self.assertTrue(self.battler.active.get_move('thunderbolt').disabled)
        self.assertTrue(self.battler.active.get_move('agility').disabled)
        self.assertTrue(self.battler.active.get_move('doubleteam').disabled)

    def test_firstimpression_gets_locked_when_last_used_move_was_by_the_active_pokemon(self):
        self.battler.active.moves.append(Move('firstimpression'))
        self.battler.last_used_move = LastUsedMove(
            pokemon_name='pikachu',  # the current active pokemon
            move='volttackle',
            turn=0
        )

        self.battler.lock_moves()

        self.assertTrue(self.battler.active.get_move('firstimpression').disabled)

    def test_calmmind_gets_locked_when_user_has_assaultvest(self):
        self.battler.active.moves.append(Move('calmmind'))
        self.battler.active.item = 'assaultvest'

        self.battler.lock_moves()

        self.assertTrue(self.battler.active.get_move('calmmind').disabled)

    def test_tackle_is_not_disabled_when_user_has_assaultvest(self):
        self.battler.active.moves.append(Move('tackle'))
        self.battler.active.item = 'assaultvest'

        self.battler.lock_moves()

        self.assertFalse(self.battler.active.get_move('tackle').disabled)

    def test_fakeout_gets_locked_when_last_used_move_was_by_the_active_pokemon(self):
        self.battler.active.moves.append(Move('fakeout'))
        self.battler.last_used_move = LastUsedMove(
            pokemon_name='pikachu',  # the current active pokemon
            move='volttackle',
            turn=0
        )

        self.battler.lock_moves()

        self.assertTrue(self.battler.active.get_move('fakeout').disabled)

    def test_firstimpression_is_not_disabled_when_the_last_used_move_was_a_switch(self):
        self.battler.active.moves.append(Move('firstimpression'))
        self.battler.last_used_move = LastUsedMove(
            pokemon_name='caterpie',
            move='switch',
            turn=0
        )

        self.battler.lock_moves()

        self.assertFalse(self.battler.active.get_move('firstimpression').disabled)

    def test_fakeout_is_not_disabled_when_the_last_used_move_was_a_switch(self):
        self.battler.active.moves.append(Move('fakeout'))
        self.battler.last_used_move = LastUsedMove(
            pokemon_name='caterpie',
            move='switch',
            turn=0
        )

        self.battler.lock_moves()

        self.assertFalse(self.battler.active.get_move('fakeout').disabled)

    def test_choice_item_with_previous_move_being_a_switch_returns_false(self):
        self.battler.active.item = 'choicescarf'
        self.battler.last_used_move = LastUsedMove(
            pokemon_name='caterpie',
            move='switch',
            turn=0
        )
        self.battler.lock_moves()

        self.assertFalse(self.battler.active.get_move('volttackle').disabled)
        self.assertFalse(self.battler.active.get_move('thunderbolt').disabled)
        self.assertFalse(self.battler.active.get_move('agility').disabled)
        self.assertFalse(self.battler.active.get_move('doubleteam').disabled)

    def test_non_choice_item_possession_returns_false(self):
        self.battler.active.item = ''
        self.battler.last_used_move = LastUsedMove(
            pokemon_name='pikachu',
            move='tackle',
            turn=0
        )
        self.battler.lock_moves()

        self.assertFalse(self.battler.active.get_move('volttackle').disabled)
        self.assertFalse(self.battler.active.get_move('thunderbolt').disabled)
        self.assertFalse(self.battler.active.get_move('agility').disabled)
        self.assertFalse(self.battler.active.get_move('doubleteam').disabled)


class TestBattle(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.active = Pokemon('Pikachu', 100)
        self.battle.opponent.active = Pokemon('Pikachu', 100)

    def test_gets_only_move_for_both_sides(self):
        self.battle.user.active.moves = [
            Move('thunderbolt')
        ]
        self.battle.opponent.active.moves = [
            Move('thunderbolt')
        ]

        expected_options = ['thunderbolt'], ['thunderbolt']

        self.assertEqual(expected_options, self.battle.get_all_options())

    def test_gets_multiple_moves_for_both_sides(self):
        self.battle.user.active.moves = [
            Move('thunderbolt'),
            Move('agility'),
            Move('tackle'),
            Move('charm'),
        ]
        self.battle.opponent.active.moves = [
            Move('thunderbolt'),
            Move('swift'),
            Move('dragondance'),
            Move('stealthrock'),
        ]

        expected_options = (
            [
                'thunderbolt',
                'agility',
                'tackle',
                'charm'
            ],
            [
                'thunderbolt',
                'swift',
                'dragondance',
                'stealthrock'
            ]
        )

        self.assertEqual(expected_options, self.battle.get_all_options())

    def test_gets_one_switch_and_splash(self):
        self.battle.user.active.moves = []
        self.battle.opponent.active.moves = []

        self.battle.user.reserve = [Pokemon('caterpie', 100)]
        self.battle.opponent.reserve = [Pokemon('caterpie', 100)]

        expected_options = (
            [
                'switch caterpie'
            ],
            [
                'splash',
                'switch caterpie'
            ]
        )

        self.assertEqual(expected_options, self.battle.get_all_options())

    def test_gets_multiple_switches_and_splash(self):
        self.battle.user.active.moves = []
        self.battle.opponent.active.moves = []

        self.battle.user.reserve = [Pokemon('caterpie', 100), Pokemon('spinarak', 100)]
        self.battle.opponent.reserve = [Pokemon('caterpie', 100), Pokemon('houndour', 100)]

        expected_options = (
            [
                'switch caterpie',
                'switch spinarak'
            ],
            [
                'splash',
                'switch caterpie',
                'switch houndour'
            ]
        )

        self.assertEqual(expected_options, self.battle.get_all_options())

    def test_gets_multiple_switches_and_multiple_moves(self):
        self.battle.user.active.moves = [
            Move('tackle'),
            Move('charm'),
        ]
        self.battle.opponent.active.moves = [
            Move('tackle'),
            Move('thunderbolt'),
        ]

        self.battle.user.reserve = [Pokemon('caterpie', 100), Pokemon('spinarak', 100)]
        self.battle.opponent.reserve = [Pokemon('caterpie', 100), Pokemon('houndour', 100)]

        expected_options = (
            [
                'tackle',
                'charm',
                'switch caterpie',
                'switch spinarak'
            ],
            [
                'tackle',
                'thunderbolt',
                'switch caterpie',
                'switch houndour'
            ]
        )

        self.assertEqual(expected_options, self.battle.get_all_options())

    def test_ignores_moves_and_gives_opponent_no_option_when_user_active_is_dead(self):
        self.battle.user.active.hp = 0
        self.battle.user.active.moves = [
            Move('tackle'),
            Move('charm'),
        ]
        self.battle.opponent.active.moves = [
            Move('tackle'),
            Move('thunderbolt'),
        ]

        self.battle.user.reserve = [Pokemon('caterpie', 100), Pokemon('spinarak', 100)]
        self.battle.opponent.reserve = [Pokemon('caterpie', 100), Pokemon('houndour', 100)]

        expected_options = (
            [
                'switch caterpie',
                'switch spinarak'
            ],
            [
                'splash'
            ]
        )

        self.assertEqual(expected_options, self.battle.get_all_options())

    def test_ignores_moves_and_gives_opponent_no_option_when_force_switch_is_true(self):
        self.battle.force_switch = True
        self.battle.user.active.moves = [
            Move('tackle'),
            Move('charm'),
        ]
        self.battle.opponent.active.moves = [
            Move('tackle'),
            Move('thunderbolt'),
        ]

        self.battle.user.reserve = [Pokemon('caterpie', 100), Pokemon('spinarak', 100)]
        self.battle.opponent.reserve = [Pokemon('caterpie', 100), Pokemon('houndour', 100)]

        expected_options = (
            [
                'switch caterpie',
                'switch spinarak'
            ],
            [
                'splash'
            ]
        )

        self.assertEqual(expected_options, self.battle.get_all_options())

    def test_gives_no_options_for_user_and_only_switches_for_opponent_when_wait_is_true(self):
        self.battle.wait = True
        self.battle.user.active.moves = [
            Move('tackle'),
            Move('charm'),
        ]
        self.battle.opponent.active.moves = [
            Move('tackle'),
            Move('thunderbolt'),
        ]

        self.battle.user.reserve = [Pokemon('caterpie', 100), Pokemon('spinarak', 100)]
        self.battle.opponent.reserve = [Pokemon('caterpie', 100), Pokemon('houndour', 100)]

        expected_options = (
            [
                'splash'
            ],
            [
                'switch caterpie',
                'switch houndour'
            ]
        )

        self.assertEqual(expected_options, self.battle.get_all_options())

    def test_gives_no_options_for_user_and_only_switches_for_opponent_when_opponent_active_is_dead(self):
        self.battle.opponent.active.hp = 0
        self.battle.user.active.moves = [
            Move('tackle'),
            Move('charm'),
        ]
        self.battle.opponent.active.moves = [
            Move('tackle'),
            Move('thunderbolt'),
        ]

        self.battle.user.reserve = [Pokemon('caterpie', 100), Pokemon('spinarak', 100)]
        self.battle.opponent.reserve = [Pokemon('caterpie', 100), Pokemon('houndour', 100)]

        expected_options = (
            [
                'splash'
            ],
            [
                'switch caterpie',
                'switch houndour'
            ]
        )

        self.assertEqual(expected_options, self.battle.get_all_options())

    def test_double_fainted_active_pokemon(self):
        self.battle.user.active.hp = 0
        self.battle.opponent.active.hp = 0
        self.battle.user.active.moves = [
            Move('tackle'),
            Move('charm'),
        ]
        self.battle.opponent.active.moves = [
            Move('tackle'),
            Move('thunderbolt'),
        ]

        self.battle.user.reserve = [Pokemon('caterpie', 100), Pokemon('spinarak', 100)]
        self.battle.opponent.reserve = [Pokemon('caterpie', 100), Pokemon('houndour', 100)]

        expected_options = (
            [
                'switch caterpie',
                'switch spinarak'
            ],
            [
                'switch caterpie',
                'switch houndour'
            ]
        )

        self.assertEqual(expected_options, self.battle.get_all_options())

    def test_opponent_has_no_moves_results_in_splash_or_switches(self):
        self.battle.user.active.moves = [
            Move('tackle'),
            Move('charm'),
        ]
        self.battle.opponent.active.moves = [
        ]

        self.battle.user.reserve = [Pokemon('caterpie', 100), Pokemon('spinarak', 100)]
        self.battle.opponent.reserve = [Pokemon('caterpie', 100)]

        expected_options = (
            [
                'tackle',
                'charm',
                'switch caterpie',
                'switch spinarak'
            ],
            [
                'splash',
                'switch caterpie',
            ]
        )

        self.assertEqual(expected_options, self.battle.get_all_options())

    def test_opponent_has_moves_when_uturn_moves_first(self):
        self.battle.user.active.moves = [
            Move('tackle'),
            Move('charm'),
            Move('uturn'),
        ]
        self.battle.opponent.active.moves = [
            Move('tackle'),
            Move('charm'),
        ]

        self.battle.user.reserve = [Pokemon('caterpie', 100), Pokemon('spinarak', 100)]
        self.battle.opponent.reserve = [Pokemon('caterpie', 100)]

        # using uturn on the previous turn would cause force_switch to be True
        self.battle.force_switch = True

        self.battle.turn = 5

        self.battle.user.last_used_move = LastUsedMove(
            move='uturn',
            pokemon_name='pikachu',
            turn=5,
        )

        # the opponent's last move would have been from the turn before (turn 4), meaning it hasn't moved yet
        self.battle.opponent.last_used_move = LastUsedMove(
            move='tackle',
            pokemon_name='pikachu',
            turn=4
        )

        expected_options = (
            [
                'switch caterpie',
                'switch spinarak'
            ],
            [
                'tackle',
                'charm',
            ]
        )

        self.assertEqual(expected_options, self.battle.get_all_options())

    def test_opponent_has_no_moves_when_uturn_moves_second(self):
        self.battle.user.active.moves = [
            Move('tackle'),
            Move('charm'),
            Move('uturn'),
        ]
        self.battle.opponent.active.moves = [
            Move('tackle'),
            Move('charm'),
        ]

        self.battle.user.reserve = [Pokemon('caterpie', 100), Pokemon('spinarak', 100)]
        self.battle.opponent.reserve = [Pokemon('caterpie', 100)]

        # using uturn on the previous turn would cause force_switch to be True
        self.battle.force_switch = True

        self.battle.turn = 5

        self.battle.user.last_used_move = LastUsedMove(
            move='uturn',
            pokemon_name='pikachu',
            turn=5,
        )

        self.battle.opponent.last_used_move = LastUsedMove(
            move='tackle',
            pokemon_name='pikachu',
            turn=5
        )

        expected_options = (
            [
                'switch caterpie',
                'switch spinarak'
            ],
            [
                'splash'
            ]
        )

        self.assertEqual(expected_options, self.battle.get_all_options())

    def test_opponent_has_no_moves_when_uturn_happens_after_switch(self):
        self.battle.user.active.moves = [
            Move('tackle'),
            Move('charm'),
            Move('uturn'),
        ]
        self.battle.opponent.active.moves = [
            Move('tackle'),
            Move('charm'),
        ]

        self.battle.user.reserve = [Pokemon('caterpie', 100), Pokemon('spinarak', 100)]
        self.battle.opponent.reserve = [Pokemon('caterpie', 100)]

        # using uturn on the previous turn would cause force_switch to be True
        self.battle.force_switch = True

        self.battle.turn = 5

        self.battle.user.last_used_move = LastUsedMove(
            move='uturn',
            pokemon_name='pikachu',
            turn=5,
        )

        self.battle.opponent.last_used_move = LastUsedMove(
            move='switch pikachu',
            pokemon_name=None,
            turn=5
        )

        expected_options = (
            [
                'switch caterpie',
                'switch spinarak'
            ],
            [
                'splash'
            ]
        )

        self.assertEqual(expected_options, self.battle.get_all_options())

    def test_opponent_has_no_moves_when_uturn_kills_and_opponent_has_not_moved_yet(self):
        self.battle.user.active.moves = [
            Move('tackle'),
            Move('charm'),
            Move('uturn'),
        ]
        self.battle.opponent.active.moves = [
            Move('tackle'),
            Move('charm'),
        ]

        self.battle.user.reserve = [Pokemon('caterpie', 100), Pokemon('spinarak', 100)]
        self.battle.opponent.reserve = [Pokemon('caterpie', 100)]

        # using uturn on the previous turn would cause force_switch to be True
        self.battle.force_switch = True

        # opponent has died from uturn
        self.battle.opponent.active.hp = 0

        self.battle.turn = 5

        self.battle.user.last_used_move = LastUsedMove(
            move='uturn',
            pokemon_name='pikachu',
            turn=5,
        )

        # the opponent's last move would have been from the turn before (turn 4), meaning it hasn't moved yet
        self.battle.opponent.last_used_move = LastUsedMove(
            move='tackle',
            pokemon_name='pikachu',
            turn=4
        )

        expected_options = (
            [
                'switch caterpie',
                'switch spinarak'
            ],
            [
                'splash'
            ]
        )

        self.assertEqual(expected_options, self.battle.get_all_options())

    def test_opponent_has_no_moves_when_uturn_kills_and_opponent_has_already_moved(self):
        self.battle.user.active.moves = [
            Move('tackle'),
            Move('charm'),
            Move('uturn'),
        ]
        self.battle.opponent.active.moves = [
            Move('tackle'),
            Move('charm'),
        ]

        self.battle.user.reserve = [Pokemon('caterpie', 100), Pokemon('spinarak', 100)]
        self.battle.opponent.reserve = [Pokemon('caterpie', 100)]

        # using uturn on the previous turn would cause force_switch to be True
        self.battle.force_switch = True

        # opponent has died from uturn
        self.battle.opponent.active.hp = 0

        self.battle.turn = 5

        self.battle.user.last_used_move = LastUsedMove(
            move='uturn',
            pokemon_name='pikachu',
            turn=5,
        )

        # the opponent's last move would have been from the turn before (turn 4), meaning it hasn't moved yet
        self.battle.opponent.last_used_move = LastUsedMove(
            move='tackle',
            pokemon_name='pikachu',
            turn=5
        )

        expected_options = (
            [
                'switch caterpie',
                'switch spinarak'
            ],
            [
                'splash'
            ]
        )

        self.assertEqual(expected_options, self.battle.get_all_options())

    def test_opponent_has_no_moves_when_uturn_kills_and_opponent_has_already_switched_in(self):
        self.battle.user.active.moves = [
            Move('tackle'),
            Move('charm'),
            Move('uturn'),
        ]
        self.battle.opponent.active.moves = [
            Move('tackle'),
            Move('charm'),
        ]

        self.battle.user.reserve = [Pokemon('caterpie', 100), Pokemon('spinarak', 100)]
        self.battle.opponent.reserve = [Pokemon('caterpie', 100)]

        # using uturn on the previous turn would cause force_switch to be True
        self.battle.force_switch = True

        # opponent has died from uturn
        self.battle.opponent.active.hp = 0

        self.battle.turn = 5

        self.battle.user.last_used_move = LastUsedMove(
            move='uturn',
            pokemon_name='pikachu',
            turn=5,
        )

        # the opponent's last move would have been from the turn before (turn 4), meaning it hasn't moved yet
        self.battle.opponent.last_used_move = LastUsedMove(
            move='switch pikachu',
            pokemon_name=None,
            turn=5
        )

        expected_options = (
            [
                'switch caterpie',
                'switch spinarak'
            ],
            [
                'splash'
            ]
        )

        self.assertEqual(expected_options, self.battle.get_all_options())
