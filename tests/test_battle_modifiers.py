import unittest
import json

import constants
from showdown.state.battle import Battle
from showdown.state.pokemon import Pokemon
from showdown.state.move import Move

from showdown.state.battle_modifiers import request
from showdown.state.battle_modifiers import switch_or_drag
from showdown.state.battle_modifiers import heal_or_damage
from showdown.state.battle_modifiers import move
from showdown.state.battle_modifiers import boost
from showdown.state.battle_modifiers import unboost
from showdown.state.battle_modifiers import status
from showdown.state.battle_modifiers import curestatus
from showdown.state.battle_modifiers import start_volatile_status
from showdown.state.battle_modifiers import end_volatile_status
from showdown.state.battle_modifiers import set_opponent_ability
from showdown.state.battle_modifiers import set_opponent_ability_from_ability_tag
from showdown.state.battle_modifiers import form_change


class TestRequestMessage(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.active = Pokemon("pikachu", 100)
        self.request_json = {
            "active": [
                {
                    "moves": [
                        {
                            "move": "Storm Throw",
                            "id": "stormthrow",
                            "pp": 16,
                            "maxpp": 16,
                            "target": "normal",
                            "disabled": False
                        },
                        {
                            "move": "Ice Punch",
                            "id": "icepunch",
                            "pp": 24,
                            "maxpp": 24,
                            "target": "normal",
                            "disabled": False
                        },
                        {
                            "move": "Bulk Up",
                            "id": "bulkup",
                            "pp": 32,
                            "maxpp": 32,
                            "target": "self",
                            "disabled": False
                        },
                        {
                            "move": "Knock Off",
                            "id": "knockoff",
                            "pp": 32,
                            "maxpp": 32,
                            "target": "normal",
                            "disabled": False
                        }
                    ]
                }
            ],
            "side": {
                "name": "NiceNameNerd",
                "id": "p1",
                "pokemon": [
                    {
                        "ident": "p1: Throh",
                        "details": "Throh, L83, M",
                        "condition": "335/335",
                        "active": True,
                        "stats": {
                            "atk": 214,
                            "def": 189,
                            "spa": 97,
                            "spd": 189,
                            "spe": 122
                        },
                        "moves": [
                            "stormthrow",
                            "icepunch",
                            "bulkup",
                            "knockoff"
                        ],
                        "baseAbility": "moldbreaker",
                        "item": "leftovers",
                        "pokeball": "pokeball",
                        "ability": "moldbreaker"
                    },
                    {
                        "ident": "p1: Empoleon",
                        "details": "Empoleon, L77, F",
                        "condition": "256/256",
                        "active": False,
                        "stats": {
                            "atk": 137,
                            "def": 180,
                            "spa": 215,
                            "spd": 200,
                            "spe": 137
                        },
                        "moves": [
                            "icebeam",
                            "grassknot",
                            "scald",
                            "flashcannon"
                        ],
                        "baseAbility": "torrent",
                        "item": "choicespecs",
                        "pokeball": "pokeball",
                        "ability": "torrent"
                    },
                    {
                        "ident": "p1: Emboar",
                        "details": "Emboar, L79, M",
                        "condition": "303/303",
                        "active": False,
                        "stats": {
                            "atk": 240,
                            "def": 148,
                            "spa": 204,
                            "spd": 148,
                            "spe": 148
                        },
                        "moves": [
                            "headsmash",
                            "superpower",
                            "flareblitz",
                            "grassknot"
                        ],
                        "baseAbility": "reckless",
                        "item": "assaultvest",
                        "pokeball": "pokeball",
                        "ability": "reckless"
                    },
                    {
                        "ident": "p1: Zoroark",
                        "details": "Zoroark, L77, M",
                        "condition": "219/219",
                        "active": False,
                        "stats": {
                            "atk": 166,
                            "def": 137,
                            "spa": 229,
                            "spd": 137,
                            "spe": 206
                        },
                        "moves": [
                            "sludgebomb",
                            "darkpulse",
                            "flamethrower",
                            "focusblast"
                        ],
                        "baseAbility": "illusion",
                        "item": "choicespecs",
                        "pokeball": "pokeball",
                        "ability": "illusion"
                    },
                    {
                        "ident": "p1: Reuniclus",
                        "details": "Reuniclus, L78, M",
                        "condition": "300/300",
                        "active": False,
                        "stats": {
                            "atk": 106,
                            "def": 162,
                            "spa": 240,
                            "spd": 178,
                            "spe": 92
                        },
                        "moves": [
                            "calmmind",
                            "shadowball",
                            "psyshock",
                            "recover"
                        ],
                        "baseAbility": "magicguard",
                        "item": "lifeorb",
                        "pokeball": "pokeball",
                        "ability": "magicguard"
                    },
                    {
                        "ident": "p1: Moltres",
                        "details": "Moltres, L77",
                        "condition": "265/265",
                        "active": False,
                        "stats": {
                            "atk": 159,
                            "def": 183,
                            "spa": 237,
                            "spd": 175,
                            "spe": 183
                        },
                        "moves": [
                            "fireblast",
                            "toxic",
                            "hurricane",
                            "roost"
                        ],
                        "baseAbility": "flamebody",
                        "item": "leftovers",
                        "pokeball": "pokeball",
                        "ability": "flamebody"
                    }
                ]
            },
            "rqid": 2
        }

    def test_request_json_initializes_user_name(self):
        split_request_message = ['', 'request', json.dumps(self.request_json)]
        request(self.battle, split_request_message)
        self.assertEqual("p1", self.battle.user.name)

    def test_request_json_initializes_user_active_pkmn(self):
        split_request_message = ['', 'request', json.dumps(self.request_json)]
        request(self.battle, split_request_message)
        self.assertEqual("throh", self.battle.user.active.name)

    def test_request_json_initializes_5_reserve_pokemon(self):
        split_request_message = ['', 'request', json.dumps(self.request_json)]
        request(self.battle, split_request_message)
        self.assertEqual(5, len(self.battle.user.reserve))

    def test_request_sets_force_switch_to_false(self):
        split_request_message = ['', 'request', json.dumps(self.request_json)]
        request(self.battle, split_request_message)
        self.assertEqual(False, self.battle.force_switch)

    def test_force_switch_properly_sets_the_force_switch_flag(self):
        self.request_json.pop('active')
        self.request_json[constants.FORCE_SWITCH] = [True]
        split_request_message = ['', 'request', json.dumps(self.request_json)]
        request(self.battle, split_request_message)
        self.assertEqual(True, self.battle.force_switch)

    def test_force_switch_initializes_5_reserve_pokemon(self):
        self.request_json.pop('active')
        self.request_json[constants.FORCE_SWITCH] = [True]
        split_request_message = ['', 'request', json.dumps(self.request_json)]
        request(self.battle, split_request_message)
        self.assertEqual(5, len(self.battle.user.reserve))

    def test_wait_properly_sets_wait_flag(self):
        self.request_json.pop('active')
        self.request_json[constants.WAIT] = [True]
        split_request_message = ['', 'request', json.dumps(self.request_json)]
        request(self.battle, split_request_message)
        self.assertEqual(True, self.battle.wait)

    def test_wait_does_not_initialize_pokemon(self):
        self.request_json.pop('active')
        self.request_json[constants.WAIT] = [True]
        split_request_message = ['', 'request', json.dumps(self.request_json)]
        request(self.battle, split_request_message)
        self.assertEqual(0, len(self.battle.user.reserve))


class TestSwitchOrDrag(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.name = 'p1'
        self.battle.opponent.name = 'p2'
        self.battle.user.active = Pokemon('pikachu', 100)

        self.opponent_active = Pokemon('caterpie', 100)
        self.battle.opponent.active = self.opponent_active
        self.battle.opponent.reserve = [
        ]

    def test_switch_opponents_pokemon_successfully_creates_new_pokemon_for_active(self):
        new_pkmn = Pokemon('weedle', 100)
        split_msg = ['', 'switch', 'p2a: weedle', 'Weedle, L100, M', '100/100']
        switch_or_drag(self.battle, split_msg)

        self.assertEqual(new_pkmn, self.battle.opponent.active)

    def test_switch_resets_toxic_count_for_opponent(self):
        self.battle.opponent.side_conditions[constants.TOXIC_COUNT] = 1
        split_msg = ['', 'switch', 'p2a: weedle', 'Weedle, L100, M', '100/100']
        switch_or_drag(self.battle, split_msg)

        self.assertEqual(0, self.battle.opponent.side_conditions[constants.TOXIC_COUNT])

    def test_switch_resets_toxic_count_for_opponent_when_there_is_no_toxic_count(self):
        split_msg = ['', 'switch', 'p2a: weedle', 'Weedle, L100, M', '100/100']
        switch_or_drag(self.battle, split_msg)

        self.assertEqual(0, self.battle.opponent.side_conditions[constants.TOXIC_COUNT])

    def test_switch_resets_toxic_count_for_user(self):
        self.battle.user.side_conditions[constants.TOXIC_COUNT] = 1
        split_msg = ['', 'switch', 'p1a: weedle', 'Weedle, L100, M', '100/100']
        switch_or_drag(self.battle, split_msg)

        self.assertEqual(0, self.battle.user.side_conditions[constants.TOXIC_COUNT])

    def test_switch_opponents_pokemon_successfully_places_previous_active_pokemon_in_reserve(self):
        split_msg = ['', 'switch', 'p2a: weedle', 'Weedle, L100, M', '100/100']
        switch_or_drag(self.battle, split_msg)

        self.assertIn(self.opponent_active, self.battle.opponent.reserve)

    def test_switch_opponents_pokemon_creates_reserve_of_length_1_when_reserve_was_previously_empty(self):
        split_msg = ['', 'switch', 'p2a: weedle', 'Weedle, L100, M', '100/100']
        switch_or_drag(self.battle, split_msg)

        self.assertEqual(1, len(self.battle.opponent.reserve))

    def test_switch_into_already_seen_pokemon_does_not_create_a_new_pokemon(self):
        already_seen_pokemon = Pokemon('weedle', 100)
        self.battle.opponent.reserve.append(already_seen_pokemon)
        split_msg = ['', 'switch', 'p2a: weedle', 'Weedle, L100, M', '100/100']
        switch_or_drag(self.battle, split_msg)

        self.assertEqual(1, len(self.battle.opponent.reserve))

    def test_already_seen_pokemon_is_the_same_object_as_the_one_in_the_reserve(self):
        already_seen_pokemon = Pokemon('weedle', 100)
        self.battle.opponent.reserve.append(already_seen_pokemon)
        split_msg = ['', 'switch', 'p2a: weedle', 'Weedle, L100, M', '100/100']
        switch_or_drag(self.battle, split_msg)

        self.assertIs(already_seen_pokemon, self.battle.opponent.active)

    def test_silvally_steel_replaces_silvally(self):
        already_seen_pokemon = Pokemon('silvally', 100)
        self.battle.opponent.reserve.append(already_seen_pokemon)
        split_msg = ['', 'switch', 'p2a: silvally', 'Silvally-Steel, L100, M', '100/100']
        switch_or_drag(self.battle, split_msg)

        expected_pokemon = Pokemon('silvallysteel', 100)

        self.assertEqual(expected_pokemon, self.battle.opponent.active)

    def test_arceus_ghost_switching_in(self):
        already_seen_pokemon = Pokemon('arceus', 100)
        self.battle.opponent.reserve.append(already_seen_pokemon)
        split_msg = ['', 'switch', 'p2a: Arceus', 'Arceus-Ghost', '100/100']
        switch_or_drag(self.battle, split_msg)

        expected_pokemon = Pokemon('arceus-ghost', 100)

        self.assertEqual(expected_pokemon, self.battle.opponent.active)

    def test_existing_boosts_on_opponents_active_pokemon_are_cleared_when_switching(self):
        self.opponent_active.boosts[constants.ATTACK] = 1
        self.opponent_active.boosts[constants.SPEED] = 1
        split_msg = ['', 'switch', 'p2a: weedle', 'Weedle, L100, M', '100/100']
        switch_or_drag(self.battle, split_msg)

        self.assertEqual({}, self.opponent_active.boosts)

    def test_existing_boosts_on_bots_active_pokemon_are_cleared_when_switching(self):
        pkmn = self.battle.user.active
        pkmn.boosts[constants.ATTACK] = 1
        pkmn.boosts[constants.SPEED] = 1
        split_msg = ['', 'switch', 'p1a: pidgey', 'Pidgey, L100, M', '100/100']
        switch_or_drag(self.battle, split_msg)

        self.assertEqual({}, pkmn.boosts)

    def test_switching_into_the_same_pokemon_does_not_put_that_pokemon_in_the_reserves(self):
        # this is specifically for Zororak
        split_msg = ['', 'switch', 'p2a: caterpie', 'Caterpie, L100, M', '100/100']
        switch_or_drag(self.battle, split_msg)

        self.assertFalse(self.battle.opponent.reserve)


class TestHealOrDamage(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.name = 'p1'
        self.battle.opponent.name = 'p2'

        self.user_active = Pokemon('caterpie', 100)
        self.opponent_active = Pokemon('caterpie', 100)

        # manually set hp to 200 for testing purposes
        self.opponent_active.max_hp = 200
        self.opponent_active.hp = 200

        self.battle.opponent.active = self.opponent_active
        self.battle.user.active = self.user_active

    def test_sets_ability_when_the_information_is_present(self):
        split_msg = ['', '-heal', 'p2a: Quagsire', '68/100', '[from] ability: Water Absorb', '[of] p2a: Genesect']
        heal_or_damage(self.battle, split_msg)
        self.assertEqual('waterabsorb', self.battle.opponent.active.ability)

    def test_damage_sets_opponents_active_pokemon_to_correct_hp(self):
        split_msg = ['', '-damage', 'p2a: Caterpie', '80/100']
        heal_or_damage(self.battle, split_msg)
        self.assertEqual(160, self.battle.opponent.active.hp)

    def test_fainted_message_properly_faints_opponents_pokemon(self):
        split_msg = ['', '-damage', 'p2a: Caterpie', '0 fnt']
        heal_or_damage(self.battle, split_msg)
        self.assertEqual(0, self.battle.opponent.active.hp)

    def test_damage_caused_by_an_item_properly_sets_opponents_item(self):
        split_msg = ['', '-damage', 'p2a: Caterpie', '100/100', '[from] item: Life Orb']
        heal_or_damage(self.battle, split_msg)
        self.assertEqual("lifeorb", self.battle.opponent.active.item)

    def test_damage_caused_by_toxic_increases_side_condition_toxic_counter_for_opponent(self):
        split_msg = ['', '-damage', 'p2a: Caterpie', '94/100 tox', '[from] psn']
        heal_or_damage(self.battle, split_msg)
        self.assertEqual(1, self.battle.opponent.side_conditions[constants.TOXIC_COUNT])

    def test_damage_caused_by_toxic_increases_side_condition_toxic_counter_for_user(self):
        split_msg = ['', '-damage', 'p1a: Caterpie', '94/100 tox', '[from] psn']
        heal_or_damage(self.battle, split_msg)
        self.assertEqual(1, self.battle.user.side_conditions[constants.TOXIC_COUNT])

    def test_toxic_count_increases_to_2(self):
        self.battle.opponent.side_conditions[constants.TOXIC_COUNT] = 1
        split_msg = ['', '-damage', 'p2a: Caterpie', '94/100 tox', '[from] psn']
        heal_or_damage(self.battle, split_msg)
        self.assertEqual(2, self.battle.opponent.side_conditions[constants.TOXIC_COUNT])

    def test_damage_caused_by_non_toxic_damage_does_not_increase_toxic_count(self):
        split_msg = ['', '-damage', 'p2a: Caterpie', '50/100 tox', '[from] item: Life Orb']
        heal_or_damage(self.battle, split_msg)
        self.assertEqual(0, self.battle.opponent.side_conditions[constants.TOXIC_COUNT])


class TestMove(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.name = 'p1'
        self.battle.opponent.name = 'p2'

        self.opponent_active = Pokemon('caterpie', 100)
        self.battle.opponent.active = self.opponent_active

    def test_adds_move_to_opponent(self):
        split_msg = ['', 'move', 'p2a: Caterpie', 'String Shot']

        move(self.battle, split_msg)
        m = Move("String Shot")

        self.assertIn(m, self.battle.opponent.active.moves)

    def test_add_revealed_move_does_not_add_move_twice(self):
        split_msg = ['', 'move', 'p2a: Caterpie', 'String Shot']

        self.battle.opponent.active.moves.append(Move("String Shot"))
        move(self.battle, split_msg)

        self.assertEqual(1, len(self.battle.opponent.active.moves))


class TestBoostAndUnboost(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.name = 'p1'
        self.battle.opponent.name = 'p2'

        self.user_active = Pokemon('weedle', 100)
        self.battle.user.active = self.user_active

        self.opponent_active = Pokemon('caterpie', 100)
        self.battle.opponent.active = self.opponent_active

    def test_opponent_boost_properly_updates_opponent_pokemons_boosts(self):
        split_msg = ['', 'boost', 'p2a: Weedle', 'atk', '1']
        boost(self.battle, split_msg)

        expected_boosts = {
            constants.ATTACK: 1
        }

        self.assertEqual(expected_boosts, self.battle.opponent.active.boosts)

    def test_unboost_works_properly_on_opponent(self):
        split_msg = ['', 'boost', 'p2a: Weedle', 'atk', '1']
        unboost(self.battle, split_msg)

        expected_boosts = {
            constants.ATTACK: -1
        }

        self.assertEqual(expected_boosts, self.battle.opponent.active.boosts)

    def test_unboost_does_not_lower_below_negative_6(self):
        self.battle.opponent.active.boosts[constants.ATTACK] = -6
        split_msg = ['', 'unboost', 'p2a: Weedle', 'atk', '2']
        unboost(self.battle, split_msg)

        expected_boosts = {
            constants.ATTACK: -6
        }

        self.assertEqual(expected_boosts, dict(self.battle.opponent.active.boosts))

    def test_unboost_lowers_one_when_it_hits_the_limit(self):
        self.battle.opponent.active.boosts[constants.ATTACK] = -5
        split_msg = ['', 'unboost', 'p2a: Weedle', 'atk', '2']
        unboost(self.battle, split_msg)

        expected_boosts = {
            constants.ATTACK: -6
        }

        self.assertEqual(expected_boosts, dict(self.battle.opponent.active.boosts))

    def test_boost_does_not_lower_below_negative_6(self):
        self.battle.opponent.active.boosts[constants.ATTACK] = 6
        split_msg = ['', 'boost', 'p2a: Weedle', 'atk', '2']
        boost(self.battle, split_msg)

        expected_boosts = {
            constants.ATTACK: 6
        }

        self.assertEqual(expected_boosts, dict(self.battle.opponent.active.boosts))

    def test_boost_lowers_one_when_it_hits_the_limit(self):
        self.battle.opponent.active.boosts[constants.ATTACK] = 5
        split_msg = ['', 'boost', 'p2a: Weedle', 'atk', '2']
        boost(self.battle, split_msg)

        expected_boosts = {
            constants.ATTACK: 6
        }

        self.assertEqual(expected_boosts, dict(self.battle.opponent.active.boosts))

    def test_unboost_works_properly_on_user(self):
        split_msg = ['', 'boost', 'p1a: Caterpie', 'atk', '1']
        unboost(self.battle, split_msg)

        expected_boosts = {
            constants.ATTACK: -1
        }

        self.assertEqual(expected_boosts, self.battle.user.active.boosts)

    def test_user_boosts_updates_properly(self):
        split_msg = ['', 'boost', 'p1a: Caterpie', 'atk', '1']
        boost(self.battle, split_msg)

        expected_boosts = {
            constants.ATTACK: 1
        }

        self.assertEqual(expected_boosts, self.battle.user.active.boosts)

    def test_multiple_boost_properly_updates(self):
        split_msg = ['', 'boost', 'p2a: Weedle', 'atk', '1']
        boost(self.battle, split_msg)
        boost(self.battle, split_msg)

        expected_boosts = {
            constants.ATTACK: 2
        }

        self.assertEqual(expected_boosts, self.battle.opponent.active.boosts)


class TestStatus(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.name = 'p1'
        self.battle.opponent.name = 'p2'

        self.opponent_active = Pokemon('caterpie', 100)
        self.battle.opponent.active = self.opponent_active

    def test_opponents_active_pokemon_has_status_properly_set(self):
        split_msg = ['', '-status', 'p2a: Caterpie', 'brn']
        status(self.battle, split_msg)

        self.assertEqual(self.battle.opponent.active.status, constants.BURN)


class TestCureStatus(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.name = 'p1'
        self.battle.opponent.name = 'p2'

        self.opponent_active = Pokemon('caterpie', 100)
        self.battle.opponent.active = self.opponent_active

        self.opponent_reserve = Pokemon('pikachu', 100)
        self.battle.opponent.reserve = [self.opponent_active, self.opponent_reserve]

    def test_curestatus_works_on_active_pokemon(self):
        self.opponent_active.status = constants.BURN
        split_msg = ['', '-curestatus', 'p2: Caterpie', 'brn', '[msg]']
        curestatus(self.battle, split_msg)

        self.assertEqual(None, self.opponent_active.status)

    def test_curestatus_works_on_reserve_pokemon(self):
        self.opponent_reserve.status = constants.BURN
        split_msg = ['', '-curestatus', 'p2: Pikachu', 'brn', '[msg]']
        curestatus(self.battle, split_msg)

        self.assertEqual(None, self.opponent_reserve.status)


class TestStartVolatileStatus(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.name = 'p1'
        self.battle.opponent.name = 'p2'

        self.opponent_active = Pokemon('caterpie', 100)
        self.battle.opponent.active = self.opponent_active

        self.user_active = Pokemon('weedle', 100)
        self.battle.user.active = self.user_active

    def test_volatile_status_is_set_on_opponent_pokemon(self):
        split_msg = ['', '-start', 'p2a: Caterpie', 'Encore']
        start_volatile_status(self.battle, split_msg)

        expected_volatile_statuese = ['encore']

        self.assertEqual(expected_volatile_statuese, self.battle.opponent.active.volatile_statuses)

    def test_volatile_status_is_set_on_user_pokemon(self):
        split_msg = ['', '-start', 'p1a: Weedle', 'Encore']
        start_volatile_status(self.battle, split_msg)

        expected_volatile_statuese = ['encore']

        self.assertEqual(expected_volatile_statuese, self.battle.user.active.volatile_statuses)

    def test_adds_volatile_status_from_move_string(self):
        split_msg = ['', '-start', 'p1a: Weedle', 'move: Taunt']
        start_volatile_status(self.battle, split_msg)

        expected_volatile_statuese = ['taunt']

        self.assertEqual(expected_volatile_statuese, self.battle.user.active.volatile_statuses)

    def test_does_not_add_the_same_volatile_status_twice(self):
        self.battle.opponent.active.volatile_statuses = ['encore']
        split_msg = ['', '-start', 'p2a: Caterpie', 'Encore']
        start_volatile_status(self.battle, split_msg)

        expected_volatile_statuese = ['encore']

        self.assertEqual(expected_volatile_statuese, self.battle.opponent.active.volatile_statuses)


class TestEndVolatileStatus(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.name = 'p1'
        self.battle.opponent.name = 'p2'

        self.opponent_active = Pokemon('caterpie', 100)
        self.battle.opponent.active = self.opponent_active

        self.user_active = Pokemon('weedle', 100)
        self.battle.user.active = self.user_active

    def test_removes_volatile_status_from_opponent(self):
        self.battle.opponent.active.volatile_statuses = ['encore']
        split_msg = ['', '-start', 'p2a: Caterpie', 'Encore']
        end_volatile_status(self.battle, split_msg)

        expected_volatile_statuses = []

        self.assertEqual(expected_volatile_statuses, self.battle.opponent.active.volatile_statuses)

    def test_removes_volatile_status_from_user(self):
        self.battle.user.active.volatile_statuses = ['encore']
        split_msg = ['', '-start', 'p1a: Weedle', 'Encore']
        end_volatile_status(self.battle, split_msg)

        expected_volatile_statuses = []

        self.assertEqual(expected_volatile_statuses, self.battle.user.active.volatile_statuses)


class TestUpdateAbility(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.name = 'p1'
        self.battle.opponent.name = 'p2'

        self.opponent_active = Pokemon('caterpie', 100)
        self.battle.opponent.active = self.opponent_active
        self.battle.opponent.active.ability = None

        self.user_active = Pokemon('weedle', 100)
        self.battle.user.active = self.user_active

    def test_removes_volatile_status_from_opponent(self):
        self.battle.opponent.active.volatile_statuses = ['encore']
        split_msg = ['', '-immune', 'p2a: Caterpie', '[from] ability: Volt Absorb']
        set_opponent_ability(self.battle, split_msg)

        expected_ability = 'voltabsorb'

        self.assertEqual(expected_ability, self.battle.opponent.active.ability)

    def test_update_ability_from_ability_string_properly_updates_ability(self):
        # |-ability|p1a: Seaking|Lightning Rod|boost
        split_msg = ['', '-ability', 'p2a: Caterpie', 'Lightning Rod', 'boost']
        set_opponent_ability_from_ability_tag(self.battle, split_msg)

        expected_ability = 'lightningrod'

        self.assertEqual(expected_ability, self.battle.opponent.active.ability)


class TestFormChange(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.name = 'p1'
        self.battle.opponent.name = 'p2'

        self.opponent_active = Pokemon('caterpie', 100)
        self.battle.opponent.active = self.opponent_active
        self.battle.opponent.active.ability = None

        self.user_active = Pokemon('weedle', 100)
        self.battle.user.active = self.user_active

    def test_changes_with_formechange_message(self):
        self.battle.opponent.active = Pokemon('meloetta', 100)
        split_msg = ['', '-formechange', 'p2a: Meloetta', 'Meloetta - Pirouette', '[msg]']
        form_change(self.battle, split_msg)

        self.assertEqual('meloettapirouette', self.battle.opponent.active.name)

    def test_preserves_base_name_when_form_changes(self):
        self.battle.opponent.active = Pokemon('meloetta', 100)
        split_msg = ['', '-formechange', 'p2a: Meloetta', 'Meloetta - Pirouette', '[msg]']
        form_change(self.battle, split_msg)

        self.assertEqual('meloetta', self.battle.opponent.active.base_name)

    def test_removes_pokemon_from_reserve_if_it_is_in_there(self):
        zoroark = Pokemon('zoroark', 82)
        self.battle.opponent.active = Pokemon('meloetta', 100)
        self.battle.opponent.reserve = [zoroark]
        split_msg = ['', '-replace', 'p2a: Zoroark', 'Zoroark, L82, M']
        form_change(self.battle, split_msg)

        self.assertNotIn(zoroark, self.battle.opponent.reserve)

    def test_does_not_set_base_name_for_illusion_ending(self):
        self.battle.opponent.active = Pokemon('meloetta', 100)
        split_msg = ['', 'replace', 'p2a: Zoroark', 'Zoroark, L84, F']
        form_change(self.battle, split_msg)

        self.assertEqual('zoroark', self.battle.opponent.active.base_name)

    def test_multiple_forme_changes_does_not_ruin_base_name(self):
        self.battle.user.active = Pokemon('pikachu', 100)
        self.battle.opponent.active = Pokemon('pikachu', 100)
        self.battle.opponent.reserve = []
        self.battle.opponent.reserve.append(Pokemon('wishiwashi', 100))

        m1 = ['', 'switch', 'p2a: Wishiwashi', 'Wishiwashi, L100, M', '100/100']
        m2 = ['', '-formechange', 'p2a: Wishiwashi', 'Wishiwashi-School', '', '[from] ability: Schooling']
        m3 = ['', 'switch', 'p2a: Pikachu', 'Pikachu, L100, M', '100/100']
        m4 = ['', 'switch', 'p2a: Wishiwashi', 'Wishiwashi, L100, M', '100/100']
        m5 = ['', '-formechange', 'p2a: Wishiwashi', 'Wishiwashi-School', '', '[from] ability: Schooling']
        m6 = ['', 'switch', 'p2a: Pikachu', 'Pikachu, L100, M', '100/100']
        m7 = ['', 'switch', 'p2a: Wishiwashi', 'Wishiwashi, L100, M', '100/100']
        m8 = ['', '-formechange', 'p2a: Wishiwashi', 'Wishiwashi-School', '', '[from] ability: Schooling']

        switch_or_drag(self.battle, m1)
        form_change(self.battle, m2)
        switch_or_drag(self.battle, m3)
        switch_or_drag(self.battle, m4)
        form_change(self.battle, m5)
        switch_or_drag(self.battle, m6)
        switch_or_drag(self.battle, m7)
        form_change(self.battle, m8)

        pkmn = Pokemon("wishiwashischool", 100)
        self.assertNotIn(pkmn, self.battle.opponent.reserve)
