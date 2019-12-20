import unittest
import json

import constants
from showdown.battle import Battle
from showdown.battle import Pokemon
from showdown.battle import Move
from showdown.battle import LastUsedMove

from showdown.battle_modifier import request
from showdown.battle_modifier import switch_or_drag
from showdown.battle_modifier import heal_or_damage
from showdown.battle_modifier import move
from showdown.battle_modifier import boost
from showdown.battle_modifier import unboost
from showdown.battle_modifier import status
from showdown.battle_modifier import weather
from showdown.battle_modifier import curestatus
from showdown.battle_modifier import start_volatile_status
from showdown.battle_modifier import end_volatile_status
from showdown.battle_modifier import set_opponent_ability
from showdown.battle_modifier import set_opponent_ability_from_ability_tag
from showdown.battle_modifier import form_change
from showdown.battle_modifier import inactive
from showdown.battle_modifier import zpower
from showdown.battle_modifier import clearnegativeboost
from showdown.battle_modifier import check_choicescarf
from showdown.battle_modifier import singleturn


# so we can instantiate a Battle object for testing
Battle.__abstractmethods__ = set()


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

    def test_switching_sets_last_move_to_none(self):
        split_msg = ['', 'switch', 'p2a: weedle', 'Weedle, L100, M', '100/100']
        switch_or_drag(self.battle, split_msg)

        expected_last_move = LastUsedMove(None, 'switch')

        self.assertEqual(expected_last_move, self.battle.opponent.last_used_move)

    def test_opponent_switching_with_dynamax_volatile_status_halves_their_hp(self):
        self.battle.opponent.active.volatile_statuses = ['dynamax']
        split_msg = ['', 'switch', 'p2a: weedle', 'Weedle, L100, M', '100/100']

        pkmn = self.battle.opponent.active
        hp, maxhp = pkmn.hp, pkmn.max_hp

        switch_or_drag(self.battle, split_msg)

        self.assertEqual(hp/2, pkmn.hp)
        self.assertEqual(maxhp/2, pkmn.max_hp)

    def test_opponent_switching_without_dynamax_volatile_status_does_not_halve_their_hp(self):
        self.battle.opponent.active.volatile_statuses = []
        split_msg = ['', 'switch', 'p2a: weedle', 'Weedle, L100, M', '100/100']

        pkmn = self.battle.opponent.active
        hp, maxhp = pkmn.hp, pkmn.max_hp

        switch_or_drag(self.battle, split_msg)

        self.assertEqual(hp, pkmn.hp)
        self.assertEqual(maxhp, pkmn.max_hp)


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

    def test_sets_ability_when_the_bot_is_damaged_from_opponents_ability(self):
        split_msg = ['', '-damage', 'p1a: Lamdorus', '167/319', '[from] ability: Iron Barbs', '[of] p2a: Ferrothorn']
        heal_or_damage(self.battle, split_msg)
        self.assertEqual('ironbarbs', self.battle.opponent.active.ability)

    def test_sets_item_when_it_causes_the_bot_damage(self):
        split_msg = ['', '-damage', 'p1a: Kartana', '167/319', '[from] item: Rocky Helmet', '[of] p2a: Ferrothorn']
        heal_or_damage(self.battle, split_msg)
        self.assertEqual('rockyhelmet', self.battle.opponent.active.item)

    def test_does_not_set_item_when_item_is_none(self):
        # |-heal|p2a: Drifblim|37/100|[from] item: Sitrus Berry
        split_msg = ['', '-heal', 'p2a: Drifblim', '37/100', '[from] item: Sitrus Berry']
        self.battle.opponent.active.item = None
        heal_or_damage(self.battle, split_msg)
        self.assertEqual(None, self.battle.opponent.active.item)

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

    def test_new_move_has_one_pp_less_than_max(self):
        split_msg = ['', 'move', 'p2a: Caterpie', 'String Shot']

        move(self.battle, split_msg)
        m = self.battle.opponent.active.get_move("String Shot")
        expected_pp = m.max_pp - 1

        self.assertEqual(expected_pp, m.current_pp)

    def test_unknown_move_does_not_try_to_decrement(self):
        split_msg = ['', 'move', 'p2a: Caterpie', 'some-random-unknown-move']

        move(self.battle, split_msg)

    def test_add_revealed_move_does_not_add_move_twice(self):
        split_msg = ['', 'move', 'p2a: Caterpie', 'String Shot']

        self.battle.opponent.active.moves.append(Move("String Shot"))
        move(self.battle, split_msg)

        self.assertEqual(1, len(self.battle.opponent.active.moves))

    def test_decrements_seen_move_pp_if_seen_again(self):
        split_msg = ['', 'move', 'p2a: Caterpie', 'String Shot']
        m = Move("String Shot")
        m.current_pp = 5
        self.battle.opponent.active.moves.append(m)
        move(self.battle, split_msg)

        self.assertEqual(4, m.current_pp)

    def test_properly_sets_last_used_move(self):
        split_msg = ['', 'move', 'p2a: Caterpie', 'String Shot']

        move(self.battle, split_msg)

        expected_last_used_move = LastUsedMove(pokemon_name='caterpie', move='stringshot')

        self.assertEqual(expected_last_used_move, self.battle.opponent.last_used_move)

    def test_sets_can_have_choice_item_to_false_if_two_different_moves_are_used_when_the_pkmn_has_an_unknown_item(self):
        self.battle.opponent.active.can_have_choice_item = True
        split_msg = ['', 'move', 'p2a: Caterpie', 'String Shot']
        self.battle.opponent.last_used_move = LastUsedMove('caterpie', 'tackle')

        move(self.battle, split_msg)

        self.assertFalse(self.battle.opponent.active.can_have_choice_item)

    def test_does_not_set_can_have_choice_item_to_false_if_the_same_move_is_used_when_the_pkmn_has_an_unknown_item(self):
        self.battle.opponent.active.can_have_choice_item = True
        split_msg = ['', 'move', 'p2a: Caterpie', 'String Shot']
        self.battle.opponent.last_used_move = LastUsedMove('caterpie', 'stringshot')

        move(self.battle, split_msg)

        self.assertTrue(self.battle.opponent.active.can_have_choice_item)

    def test_sets_can_have_choice_item_to_false_even_if_item_is_known(self):
        # if the item is known - this flag doesn't matter anyways
        self.battle.opponent.active.can_have_choice_item = True
        self.battle.opponent.active.item = 'leftovers'
        split_msg = ['', 'move', 'p2a: Caterpie', 'String Shot']
        self.battle.opponent.last_used_move = LastUsedMove('caterpie', 'tackle')

        move(self.battle, split_msg)

        self.assertFalse(self.battle.opponent.active.can_have_choice_item)

    def test_sets_can_have_life_orb_to_false_if_damaging_move_is_used(self):
        # if a damaging move is used, we no longer want to guess lifeorb as an item
        self.battle.opponent.active.can_have_life_orb = True
        split_msg = ['', 'move', 'p2a: Caterpie', 'Tackle']

        move(self.battle, split_msg)

        self.assertFalse(self.battle.opponent.active.can_have_life_orb)

    def test_does_not_set_can_have_life_orb_to_false_if_pokemon_could_have_sheerforce(self):
        # mawile could have sheerforce
        # we shouldn't set the lifeorb flag to False because sheerforce doesn't reveal lifeorb when a damaging move is used
        self.battle.opponent.active.name = 'mawile'
        self.battle.opponent.active.can_have_life_orb = True
        split_msg = ['', 'move', 'p2a: Mawile', 'Tackle']

        move(self.battle, split_msg)

        self.assertTrue(self.battle.opponent.active.can_have_life_orb)

    def test_does_not_set_can_have_life_orb_to_false_if_pokemon_could_have_magic_guard(self):
        # clefable could have magic guard
        # we shouldn't set the lifeorb flag to False because magic guard doesn't reveal lifeorb when a damaging move is used
        self.battle.opponent.active.name = 'clefable'
        self.battle.opponent.active.can_have_life_orb = True
        split_msg = ['', 'move', 'p2a: Clefable', 'Tackle']

        move(self.battle, split_msg)

        self.assertTrue(self.battle.opponent.active.can_have_life_orb)


class TestWeather(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.name = 'p1'
        self.battle.opponent.name = 'p2'

        self.opponent_active = Pokemon('caterpie', 100)
        self.battle.opponent.active = self.opponent_active

    def test_starts_weather_properly(self):
        split_msg = ['', '-weather', 'RainDance', '[from] ability: Drizzle', '[of] p2a: Pelipper']

        weather(self.battle, split_msg)

        self.assertEqual('raindance', self.battle.weather)

    def test_sets_weather_ability_when_it_is_present(self):
        split_msg = ['', '-weather', 'RainDance', '[from] ability: Drizzle', '[of] p2a: Pelipper']

        weather(self.battle, split_msg)

        self.assertEqual('drizzle', self.battle.opponent.active.ability)


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

    def test_status_from_item_properly_sets_that_item(self):
        split_msg = ['', '-status', 'p2a: Caterpie', 'brn', '[from] item: Flame Orb']
        status(self.battle, split_msg)

        self.assertEqual(self.battle.opponent.active.item, 'flameorb')


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

    def test_flashfire_sets_ability(self):
        split_msg = ['', '-start', 'p2a: Caterpie', 'ability: Flash Fire']
        start_volatile_status(self.battle, split_msg)

        self.assertEqual('flashfire', self.battle.opponent.active.ability)

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

    def test_doubles_hp_when_dynamax_starts_for_opponent(self):
        split_msg = ['', '-start', 'p2a: Caterpie', 'Dynamax']
        hp, maxhp = self.battle.opponent.active.hp, self.battle.opponent.active.max_hp
        start_volatile_status(self.battle, split_msg)

        self.assertEqual(hp * 2, self.battle.opponent.active.hp)
        self.assertEqual(maxhp * 2, self.battle.opponent.active.max_hp)

    def test_does_not_touch_bots_hp_and_maxhp(self):
        split_msg = ['', '-start', 'p1a: Caterpie', 'Dynamax']
        hp, maxhp = self.battle.opponent.active.hp, self.battle.opponent.active.max_hp
        start_volatile_status(self.battle, split_msg)

        self.assertEqual(hp, self.battle.opponent.active.hp)
        self.assertEqual(maxhp, self.battle.opponent.active.max_hp)


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
        split_msg = ['', '-end', 'p2a: Caterpie', 'Encore']
        end_volatile_status(self.battle, split_msg)

        expected_volatile_statuses = []

        self.assertEqual(expected_volatile_statuses, self.battle.opponent.active.volatile_statuses)

    def test_removes_volatile_status_from_user(self):
        self.battle.user.active.volatile_statuses = ['encore']
        split_msg = ['', '-end', 'p1a: Weedle', 'Encore']
        end_volatile_status(self.battle, split_msg)

        expected_volatile_statuses = []

        self.assertEqual(expected_volatile_statuses, self.battle.user.active.volatile_statuses)

    def test_halves_opponent_hp_when_dynamax_ends(self):
        self.battle.opponent.active.volatile_statuses = ['dynamax']
        hp, maxhp = self.battle.opponent.active.hp, self.battle.opponent.active.max_hp
        split_msg = ['', '-end', 'p2a: Weedle', 'Dynamax']
        end_volatile_status(self.battle, split_msg)

        self.assertEqual(hp/2, self.battle.opponent.active.hp)
        self.assertEqual(maxhp/2, self.battle.opponent.active.max_hp)

    def test_does_not_halve_bots_hp_when_dynamax_ends(self):
        self.battle.user.active.volatile_statuses = ['dynamax']
        hp, maxhp = self.battle.opponent.active.hp, self.battle.opponent.active.max_hp
        split_msg = ['', '-end', 'p1a: Weedle', 'Dynamax']
        end_volatile_status(self.battle, split_msg)

        self.assertEqual(hp, self.battle.opponent.active.hp)
        self.assertEqual(maxhp, self.battle.opponent.active.max_hp)


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

    def test_preserves_boosts(self):
        self.battle.opponent.active = Pokemon('meloetta', 100)
        self.battle.opponent.active.boosts = {
            constants.ATTACK: 2
        }
        split_msg = ['', '-formechange', 'p2a: Meloetta', 'Meloetta - Pirouette', '[msg]']
        form_change(self.battle, split_msg)

        self.assertEqual(2, self.battle.opponent.active.boosts[constants.ATTACK])

    def test_preserves_status(self):
        self.battle.opponent.active = Pokemon('meloetta', 100)
        self.battle.opponent.active.status = constants.BURN
        split_msg = ['', '-formechange', 'p2a: Meloetta', 'Meloetta - Pirouette', '[msg]']
        form_change(self.battle, split_msg)

        self.assertEqual(constants.BURN, self.battle.opponent.active.status)

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


class TestInactive(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.name = 'p1'
        self.battle.opponent.name = 'p2'

        self.opponent_active = Pokemon('caterpie', 100)
        self.battle.opponent.active = self.opponent_active
        self.battle.opponent.active.ability = None

        self.user_active = Pokemon('weedle', 100)
        self.battle.user.active = self.user_active

        self.username = "CoolUsername"

        self.battle.username = self.username

    def test_sets_time_to_15_seconds(self):
        split_msg = ['', 'inactive', 'Time left: 135 sec this turn', '135 sec total']
        inactive(self.battle, split_msg)

        self.assertEqual(135, self.battle.time_remaining)

    def test_sets_to_60_seconds(self):
        split_msg = ['', 'inactive', 'Time left: 60 sec this turn', '60 sec total']
        inactive(self.battle, split_msg)

        self.assertEqual(60, self.battle.time_remaining)

    def test_capture_group_failing(self):
        self.battle.time_remaining = 1
        split_msg = ['', 'inactive', 'some random message']
        inactive(self.battle, split_msg)

        self.assertEqual(1, self.battle.time_remaining)

    def test_capture_group_failing_but_message_starts_with_username(self):
        self.battle.time_remaining = 1
        split_msg = ['', 'inactive', 'Time left: some random message']
        inactive(self.battle, split_msg)

        self.assertEqual(1, self.battle.time_remaining)

    def test_different_inactive_message_does_not_change_time(self):
        self.battle.time_remaining = 1
        split_msg = ['', 'inactive', 'Some Other Person has 10 seconds left']
        inactive(self.battle, split_msg)

        self.assertEqual(1, self.battle.time_remaining)


class TestClearNegativeBoost(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.name = 'p1'
        self.battle.opponent.name = 'p2'

        self.user_active = Pokemon('weedle', 100)
        self.battle.user.active = self.user_active

        self.opponent_active = Pokemon('caterpie', 100)
        self.battle.opponent.active = self.opponent_active

    def test_clears_negative_boosts(self):
        self.battle.opponent.active.boosts = {
            constants.ATTACK: -1
        }
        split_msg = ['-clearnegativeboost', 'p2a: caterpie', '[silent]']
        clearnegativeboost(self.battle, split_msg)

        self.assertEqual(0, self.battle.opponent.active.boosts[constants.ATTACK])

    def test_clears_multiple_negative_boosts(self):
        self.battle.opponent.active.boosts = {
            constants.ATTACK: -1,
            constants.SPEED: -1
        }
        split_msg = ['-clearnegativeboost', 'p2a: caterpie', '[silent]']
        clearnegativeboost(self.battle, split_msg)

        self.assertEqual(0, self.battle.opponent.active.boosts[constants.ATTACK])
        self.assertEqual(0, self.battle.opponent.active.boosts[constants.SPEED])

    def test_does_not_clear_positive_boost(self):
        self.battle.opponent.active.boosts = {
            constants.ATTACK: 1
        }
        split_msg = ['-clearnegativeboost', 'p2a: caterpie', '[silent]']
        clearnegativeboost(self.battle, split_msg)

        self.assertEqual(1, self.battle.opponent.active.boosts[constants.ATTACK])

    def test_clears_only_negative_boosts(self):
        self.battle.opponent.active.boosts = {
            constants.ATTACK: 1,
            constants.SPECIAL_ATTACK: 1,
            constants.SPEED: 1,
            constants.DEFENSE: -1,
            constants.SPECIAL_DEFENSE: -1
        }
        split_msg = ['-clearnegativeboost', 'p2a: caterpie', '[silent]']
        clearnegativeboost(self.battle, split_msg)

        expected_boosts = {
            constants.ATTACK: 1,
            constants.SPECIAL_ATTACK: 1,
            constants.SPEED: 1,
            constants.DEFENSE: 0,
            constants.SPECIAL_DEFENSE: 0
        }

        self.assertEqual(expected_boosts, self.battle.opponent.active.boosts)


class TestZPower(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.name = 'p1'
        self.battle.opponent.name = 'p2'

        self.opponent_active = Pokemon('caterpie', 100)
        self.battle.opponent.active = self.opponent_active
        self.battle.opponent.active.ability = None

        self.user_active = Pokemon('weedle', 100)
        self.battle.user.active = self.user_active

        self.username = "CoolUsername"

        self.battle.username = self.username

    def test_sets_item_to_none(self):
        split_msg = ['', '-zpower', 'p2a: Pkmn']
        self.battle.opponent.active.item = "some_item"
        zpower(self.battle, split_msg)

        self.assertEqual(None, self.battle.opponent.active.item)

    def test_does_not_set_item_when_the_bot_moves(self):
        split_msg = ['', '-zpower', 'p1a: Pkmn']
        self.battle.opponent.active.item = "some_item"
        zpower(self.battle, split_msg)

        self.assertEqual("some_item", self.battle.opponent.active.item)


class TestSingleTurn(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.name = 'p1'
        self.battle.opponent.name = 'p2'

        self.opponent_active = Pokemon('caterpie', 100)
        self.battle.opponent.active = self.opponent_active
        self.battle.opponent.active.ability = None

        self.user_active = Pokemon('weedle', 100)
        self.battle.user.active = self.user_active

        self.username = "CoolUsername"

        self.battle.username = self.username

    def test_sets_protect_side_condition_for_opponent_when_used(self):
        split_msg = ['', '-singleturn', 'p2a: Caterpie', 'Protect']
        singleturn(self.battle, split_msg)

        self.assertEqual(2, self.battle.opponent.side_conditions[constants.PROTECT])

    def test_does_not_set_for_non_protect_move(self):
        split_msg = ['', '-singleturn', 'p2a: Caterpie', 'Roost']
        singleturn(self.battle, split_msg)

        self.assertEqual(0, self.battle.opponent.side_conditions[constants.PROTECT])

    def test_sets_protect_side_condition_for_bot_when_used(self):
        split_msg = ['', '-singleturn', 'p1a: Weedle', 'Protect']
        singleturn(self.battle, split_msg)

        self.assertEqual(2, self.battle.user.side_conditions[constants.PROTECT])

    def test_sets_protect_side_condition_when_prefixed_by_move(self):
        split_msg = ['', '-singleturn', 'p2a: Caterpie', 'move: Protect']
        singleturn(self.battle, split_msg)

        self.assertEqual(2, self.battle.opponent.side_conditions[constants.PROTECT])


class TestGuessChoiceScarf(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(None)
        self.battle.user.name = 'p1'
        self.battle.opponent.name = 'p2'

        self.opponent_active = Pokemon('caterpie', 100)
        self.battle.opponent.active = self.opponent_active
        self.battle.opponent.active.ability = None

        self.user_active = Pokemon('caterpie', 100)
        self.battle.user.active = self.user_active

        self.username = "CoolUsername"

        self.battle.username = self.username

    def test_guesses_choicescarf_when_opponent_should_always_be_slower(self):
        self.battle.user.active.stats[constants.SPEED] = 210  # opponent's speed should not be greater than 207 (max speed caterpie)

        messages = [
            '|move|p2a: Caterpie|Stealth Rock|',
            '|move|p1a: Caterpie|Stealth Rock|'
        ]

        check_choicescarf(self.battle, messages)

        self.assertEqual('choicescarf', self.battle.opponent.active.item)

    def test_does_not_guess_choicescarf_when_opponent_could_have_prankster(self):
        self.battle.opponent.active.name = 'grimmsnarl'  # grimmsnarl could have prankster - it's non-damaging moves get +1 priority
        self.battle.user.active.stats[constants.SPEED] = 245  # opponent's speed should not be greater than 240 (max speed grimmsnarl)

        messages = [
            '|move|p2a: Grimmsnarl|Stealth Rock|',
            '|move|p1a: Caterpie|Stealth Rock|'
        ]

        check_choicescarf(self.battle, messages)

        self.assertEqual(constants.UNKNOWN_ITEM, self.battle.opponent.active.item)

    def test_does_not_guess_choicescarf_when_opponent_is_speed_boosted(self):
        self.battle.user.active.stats[constants.SPEED] = 210  # opponent's speed should not be greater than 207 (max speed caterpie)
        self.battle.opponent.active.boosts[constants.SPEED] = 1

        messages = [
            '|move|p2a: Caterpie|Stealth Rock|',
            '|move|p1a: Caterpie|Stealth Rock|'
        ]

        check_choicescarf(self.battle, messages)

        self.assertEqual(constants.UNKNOWN_ITEM, self.battle.opponent.active.item)

    def test_does_not_guess_choicescarf_when_bot_is_speed_unboosted(self):
        self.battle.user.active.stats[constants.SPEED] = 210  # opponent's speed should not be greater than 207 (max speed caterpie)
        self.battle.user.active.boosts[constants.SPEED] = -1

        messages = [
            '|move|p2a: Caterpie|Stealth Rock|',
            '|move|p1a: Caterpie|Stealth Rock|'
        ]

        check_choicescarf(self.battle, messages)

        self.assertEqual(constants.UNKNOWN_ITEM, self.battle.opponent.active.item)

    def test_does_not_guess_scarf_in_trickroom(self):
        self.battle.trick_room = True
        self.battle.user.active.stats[constants.SPEED] = 210  # opponent's speed should not be greater than 207 (max speed caterpie)

        messages = [
            '|move|p2a: Caterpie|Stealth Rock|',
            '|move|p1a: Caterpie|Stealth Rock|'
        ]

        check_choicescarf(self.battle, messages)

        self.assertEqual(constants.UNKNOWN_ITEM, self.battle.opponent.active.item)

    def test_does_not_guess_scarf_under_trickroom_when_opponent_could_be_slower(self):
        self.battle.trick_room = True
        self.battle.user.active.stats[constants.SPEED] = 205  # opponent caterpie speed is 113 - 207

        messages = [
            '|move|p2a: Caterpie|Stealth Rock|',
            '|move|p1a: Caterpie|Stealth Rock|'
        ]

        check_choicescarf(self.battle, messages)

        self.assertEqual(constants.UNKNOWN_ITEM, self.battle.opponent.active.item)

    def test_guesses_scarf_in_trickroom_when_opponent_cannot_be_slower(self):
        self.battle.trick_room = True
        self.battle.user.active.stats[constants.SPEED] = 110  # opponent caterpie speed is 113 - 207

        messages = [
            '|move|p2a: Caterpie|Stealth Rock|',
            '|move|p1a: Caterpie|Stealth Rock|'
        ]

        check_choicescarf(self.battle, messages)

        self.assertEqual('choicescarf', self.battle.opponent.active.item)

    def test_unknown_moves_defaults_to_0_priority(self):
        self.battle.user.active.stats[constants.SPEED] = 210  # opponent's speed should not be greater than 207 (max speed caterpie)

        messages = [
            '|move|p2a: Caterpie|unknown-move|',
            '|move|p1a: Caterpie|unknown-move|'
        ]

        check_choicescarf(self.battle, messages)

        self.assertEqual('choicescarf', self.battle.opponent.active.item)

    def test_priority_move_with_unknown_move_does_not_cause_guess(self):
        self.battle.user.active.stats[constants.SPEED] = 210  # opponent's speed should not be greater than 207 (max speed caterpie)

        messages = [
            '|move|p2a: Caterpie|Quick Attack|',
            '|move|p1a: Caterpie|unknown-move|'
        ]

        check_choicescarf(self.battle, messages)

        self.assertEqual(constants.UNKNOWN_ITEM, self.battle.opponent.active.item)

    def test_does_not_guess_item_when_bot_moves_first(self):
        self.battle.user.active.stats[constants.SPEED] = 210  # opponent's speed should not be greater than 207 (max speed caterpie)

        messages = [
            '|move|p1a: Caterpie|Stealth Rock|',
            '|move|p2a: Caterpie|Stealth Rock|'
        ]

        check_choicescarf(self.battle, messages)

        self.assertEqual(constants.UNKNOWN_ITEM, self.battle.opponent.active.item)

    def test_does_not_guess_item_when_moves_are_different_priority(self):
        self.battle.user.active.stats[constants.SPEED] = 210  # opponent's speed should not be greater than 207 (max speed caterpie)

        messages = [
            '|move|p2a: Caterpie|Quick Attack|',
            '|move|p1a: Caterpie|Stealth Rock|'
        ]

        check_choicescarf(self.battle, messages)

        self.assertEqual(constants.UNKNOWN_ITEM, self.battle.opponent.active.item)

    def test_does_not_guess_item_when_opponent_can_be_faster(self):
        self.battle.user.active.stats[constants.SPEED] = 200  # opponent's speed can be 207 (max speed caterpie)

        messages = [
            '|move|p2a: Caterpie|Stealth Rock|',
            '|move|p1a: Caterpie|Stealth Rock|'
        ]

        check_choicescarf(self.battle, messages)

        self.assertEqual(constants.UNKNOWN_ITEM, self.battle.opponent.active.item)

    def test_swiftswim_causing_opponent_to_be_faster_results_in_not_guessing_choicescarf(self):
        self.battle.opponent.active.ability = 'swiftswim'
        self.battle.weather = constants.RAIN
        self.battle.user.active.stats[constants.SPEED] = 300  # opponent's speed can be 414 (max speed caterpie plus swiftswim)

        messages = [
            '|move|p2a: Caterpie|Stealth Rock|',
            '|move|p1a: Caterpie|Stealth Rock|'
        ]

        check_choicescarf(self.battle, messages)

        self.assertEqual(constants.UNKNOWN_ITEM, self.battle.opponent.active.item)

    def test_only_one_move_causes_no_item_to_be_guessed(self):
        self.battle.user.active.stats[constants.SPEED] = 210

        messages = [
            '|move|p2a: Caterpie|Stealth Rock|',
        ]

        check_choicescarf(self.battle, messages)

        self.assertEqual(constants.UNKNOWN_ITEM, self.battle.opponent.active.item)

    def test_does_not_guess_choicescarf_when_item_is_none(self):
        self.battle.opponent.active.item = None
        self.battle.user.active.stats[constants.SPEED] = 210  # opponent's speed should not be greater than 207 (max speed caterpie)

        messages = [
            '|move|p2a: Caterpie|Stealth Rock|',
            '|move|p1a: Caterpie|Stealth Rock|'
        ]

        check_choicescarf(self.battle, messages)

        self.assertEqual(None, self.battle.opponent.active.item)

    def test_does_not_guess_choicescarf_when_item_is_known(self):
        self.battle.opponent.active.item = 'leftovers'
        self.battle.user.active.stats[constants.SPEED] = 210  # opponent's speed should not be greater than 207 (max speed caterpie)

        messages = [
            '|move|p2a: Caterpie|Stealth Rock|',
            '|move|p1a: Caterpie|Stealth Rock|'
        ]

        check_choicescarf(self.battle, messages)

        self.assertEqual('leftovers', self.battle.opponent.active.item)

    def test_uses_randombattle_spread_when_guessing_for_randombattle(self):
        self.battle.battle_type = constants.RANDOM_BATTLE

        # opponent's speed should be 193 WITHOUT a choicescarf
        # HOWEVER, max-speed should still outspeed this value
        self.battle.user.active.stats[constants.SPEED] = 195

        self.opponent_active = Pokemon('floetteeternal', 80)  # randombattle level for Floette-E
        self.battle.opponent.active = self.opponent_active

        messages = [
            '|move|p2a: Floette-Eternal|Stealth Rock|',
            '|move|p1a: Caterpie|Stealth Rock|'
        ]

        check_choicescarf(self.battle, messages)

        self.assertEqual('choicescarf', self.battle.opponent.active.item)
