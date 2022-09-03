import unittest

from collections import defaultdict
import constants

from showdown.battle import Pokemon as StatePokemon
from showdown.engine.objects import State
from showdown.engine.objects import Side
from showdown.engine.objects import Pokemon
from showdown.engine.objects import StateMutator


class TestStatemutator(unittest.TestCase):
    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                {
                    "rattata": Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    "charmander": Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    "squirtle": Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    "bulbasaur": Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    "pidgey": Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                },
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                {
                    "rattata": Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    "charmander": Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    "squirtle": Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    "bulbasaur": Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    "pidgey": Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                },
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            None,
            None,
            False
        )
        self.mutator = StateMutator(self.state)

    def test_switch_instruction_replaces_active(self):
        instruction = (
            constants.MUTATOR_SWITCH,
            constants.USER,
            "pikachu",
            "rattata"
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual("rattata", self.state.user.active.id)

    def test_switch_instruction_replaces_active_for_opponent(self):
        instruction = (
            constants.MUTATOR_SWITCH,
            constants.OPPONENT,
            "pikachu",
            "rattata"
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual("rattata", self.state.opponent.active.id)

    def test_switch_instruction_places_active_into_reserve(self):
        instruction = (
            constants.MUTATOR_SWITCH,
            constants.USER,
            "pikachu",
            "rattata"
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        try:
            self.state.user.reserve["pikachu"]
        except KeyError:
            self.fail("`pikachu` is not in `self.reserve`")

    def test_reverse_switch_instruction_replaces_active(self):
        instruction = (
            constants.MUTATOR_SWITCH,
            constants.USER,
            "rattata",
            "pikachu"
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual("rattata", self.state.user.active.id)

    def test_apply_volatile_status_properly_applies_status(self):
        instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            constants.USER,
            "leechseed"
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertIn("leechseed", self.state.user.active.volatile_status)

    def test_reverse_volatile_status_properly_removes_status(self):
        self.state.user.active.volatile_status.add("leechseed")
        instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            constants.USER,
            "leechseed"
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertNotIn("leechseed", self.state.user.active.volatile_status)

    def test_damage_is_properly_applied(self):
        instruction = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            50
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        damage_taken = self.state.user.active.maxhp - self.state.user.active.hp

        self.assertEqual(50, damage_taken)

    def test_damage_is_properly_reversed(self):
        self.state.user.active.hp -= 50
        instruction = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            50
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        damage_taken = self.state.user.active.maxhp - self.state.user.active.hp

        self.assertEqual(0, damage_taken)

    def test_healing_is_properly_applied(self):
        self.state.user.active.hp -= 50
        instruction = (
            constants.MUTATOR_HEAL,
            constants.USER,
            50
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        damage_taken = self.state.user.active.maxhp - self.state.user.active.hp

        self.assertEqual(0, damage_taken)

    def test_healing_is_properly_reversed(self):
        instruction = (
            constants.MUTATOR_HEAL,
            constants.USER,
            50
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        damage_taken = self.state.user.active.maxhp - self.state.user.active.hp

        self.assertEqual(50, damage_taken)

    def test_boost_is_properly_applied(self):
        instruction = (
            constants.MUTATOR_BOOST,
            constants.USER,
            constants.ATTACK,
            1
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual(1, self.state.user.active.attack_boost)

    def test_boost_is_properly_reversed(self):
        self.state.user.active.attack_boost = 1
        instruction = (
            constants.MUTATOR_BOOST,
            constants.USER,
            constants.ATTACK,
            1
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(0, self.state.user.active.attack_boost)

    def test_boost_is_properly_reversed_when_a_boost_previously_existed(self):
        # the pokemon had attack_boost=2 before
        # it boosted to 4, and now it is being reversed
        self.state.user.active.attack_boost = 4
        instruction = (
            constants.MUTATOR_BOOST,
            constants.USER,
            constants.ATTACK,
            2
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(2, self.state.user.active.attack_boost)

    def test_unboost_is_properly_applied(self):
        instruction = (
            constants.MUTATOR_UNBOOST,
            constants.USER,
            constants.ATTACK,
            1
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual(-1, self.state.user.active.attack_boost)

    def test_unboost_is_properly_reversed(self):
        self.state.user.active.attack_boost = -1
        instruction = (
            constants.MUTATOR_UNBOOST,
            constants.USER,
            constants.ATTACK,
            1
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(0, self.state.user.active.attack_boost)

    def test_apply_status_properly_applies_status(self):
        instruction = (
            constants.MUTATOR_APPLY_STATUS,
            constants.USER,
            constants.BURN
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual(constants.BURN, self.state.user.active.status)

    def test_apply_status_is_properly_reversed(self):
        self.state.user.active.status = constants.BURN
        instruction = (
            constants.MUTATOR_APPLY_STATUS,
            constants.USER,
            constants.BURN
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(None, self.state.user.active.status)

    def test_remove_status_properly_removes_status(self):
        self.state.user.active.status = constants.BURN
        instruction = (
            constants.MUTATOR_REMOVE_STATUS,
            constants.USER,
            constants.BURN
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual(None, self.state.user.active.status)

    def test_remove_status_is_properly_reversed(self):
        instruction = (
            constants.MUTATOR_REMOVE_STATUS,
            constants.USER,
            constants.BURN
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(constants.BURN, self.state.user.active.status)

    def test_side_start_is_properly_applied(self):
        instruction = (
            constants.MUTATOR_SIDE_START,
            constants.USER,
            constants.STEALTH_ROCK,
            1
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual(1, self.state.user.side_conditions[constants.STEALTH_ROCK])

    def test_side_start_is_properly_reversed(self):
        self.state.user.side_conditions[constants.STEALTH_ROCK] = 1
        instruction = (
            constants.MUTATOR_SIDE_START,
            constants.USER,
            constants.STEALTH_ROCK,
            1
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(0, self.state.user.side_conditions[constants.STEALTH_ROCK])

    def test_side_end_is_properly_applied(self):
        self.state.user.side_conditions[constants.STEALTH_ROCK] = 2
        instruction = (
            constants.MUTATOR_SIDE_END,
            constants.USER,
            constants.STEALTH_ROCK,
            2
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual(0, self.state.user.side_conditions[constants.STEALTH_ROCK])

    def test_side_end_is_properly_reversed(self):
        instruction = (
            constants.MUTATOR_SIDE_END,
            constants.USER,
            constants.STEALTH_ROCK,
            2
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(2, self.state.user.side_conditions[constants.STEALTH_ROCK])

    def test_disable_move(self):
        move = {
                'id': 'return',
                'disabled': False,
                'current_pp': 16
            }
        self.state.user.active.moves = [move]
        instruction = (
            constants.MUTATOR_DISABLE_MOVE,
            constants.USER,
            "return",
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertTrue(move[constants.DISABLED])

    def test_reverse_disable_move(self):
        move = {
                'id': 'return',
                'disabled': True,
                'current_pp': 16
            }
        self.state.user.active.moves = [move]
        instruction = (
            constants.MUTATOR_DISABLE_MOVE,
            constants.USER,
            "return",
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertFalse(move[constants.DISABLED])

    def test_enable_move(self):
        move = {
            'id': 'return',
            'disabled': True,
            'current_pp': 16
        }
        self.state.user.active.moves = [move]
        instruction = (
            constants.MUTATOR_ENABLE_MOVE,
            constants.USER,
            "return",
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertFalse(move[constants.DISABLED])

    def test_reverse_enable_move(self):
        move = {
            'id': 'return',
            'disabled': False,
            'current_pp': 16
        }
        self.state.user.active.moves = [move]
        instruction = (
            constants.MUTATOR_ENABLE_MOVE,
            constants.USER,
            "return",
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertTrue(move[constants.DISABLED])

    def test_setting_weather(self):
        self.state.weather = None
        instruction = (
            constants.MUTATOR_WEATHER_START,
            constants.SUN,
            None
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual(constants.SUN, self.state.weather)

    def test_setting_weather_when_previous_weather_exists(self):
        self.state.weather = constants.RAIN
        instruction = (
            constants.MUTATOR_WEATHER_START,
            constants.SUN,
            constants.RAIN
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual(constants.SUN, self.state.weather)

    def test_reversing_weather_when_previous_weather_exists(self):
        self.state.weather = constants.SUN
        instruction = (
            constants.MUTATOR_WEATHER_START,
            constants.SUN,
            constants.RAIN
        )
        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(constants.RAIN, self.state.weather)

    def test_reverse_setting_weather(self):
        self.state.weather = constants.SUN
        instruction = (
            constants.MUTATOR_WEATHER_START,
            constants.SUN,
            None
        )
        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(None, self.state.weather)

    def test_apply_and_reverse_setting_weather_works(self):
        self.state.weather = None
        instruction = (
            constants.MUTATOR_WEATHER_START,
            constants.SUN,
            None
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)
        if not self.state.weather == constants.SUN:
            self.fail("Sun was not set")

        self.mutator.reverse(list_of_instructions)

        self.assertEqual(None, self.state.weather)

    def test_apply_and_reverse_setting_weather_works_with_weather_previously_existing(self):
        self.state.weather = constants.RAIN
        instruction = (
            constants.MUTATOR_WEATHER_START,
            constants.SUN,
            constants.RAIN
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)
        if not self.state.weather == constants.SUN:
            self.fail("Sun was not set")

        self.mutator.reverse(list_of_instructions)

        self.assertEqual(constants.RAIN, self.state.weather)

    def test_setting_field(self):
        self.state.field = None
        instruction = (
            constants.MUTATOR_FIELD_START,
            constants.PSYCHIC_TERRAIN,
            None
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual(constants.PSYCHIC_TERRAIN, self.state.field)

    def test_reverse_setting_field(self):
        self.state.field = constants.PSYCHIC_TERRAIN
        instruction = (
            constants.MUTATOR_FIELD_START,
            constants.PSYCHIC_TERRAIN,
            None
        )
        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(None, self.state.field)

    def test_apply_and_reverse_field(self):
        self.state.field = None
        instruction = (
            constants.MUTATOR_FIELD_START,
            constants.PSYCHIC_TERRAIN,
            None
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)
        if self.state.field != constants.PSYCHIC_TERRAIN:
            self.fail("Terrain was not set")
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(None, self.state.field)

    def test_apply_and_reverse_field_when_previous_field_exists(self):
        self.state.field = constants.GRASSY_TERRAIN
        instruction = (
            constants.MUTATOR_FIELD_START,
            constants.PSYCHIC_TERRAIN,
            constants.GRASSY_TERRAIN
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)
        if self.state.field != constants.PSYCHIC_TERRAIN:
            self.fail("Terrain was not set")
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(constants.GRASSY_TERRAIN, self.state.field)

    def test_end_active_field(self):
        self.state.field = constants.GRASSY_TERRAIN
        instruction = (
            constants.MUTATOR_FIELD_END,
            constants.GRASSY_TERRAIN
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)
        if self.state.field is not None:
            self.fail("Terrain was not removed")
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(constants.GRASSY_TERRAIN, self.state.field)

    def test_reversing_end_active_field(self):
        self.state.field = None
        instruction = (
            constants.MUTATOR_FIELD_END,
            constants.GRASSY_TERRAIN
        )
        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)
        if self.state.field != constants.GRASSY_TERRAIN:
            self.fail("Terrain was not reset")
        self.mutator.apply(list_of_instructions)

        self.assertEqual(None, self.state.field)

    def test_toggle_trickroom_sets_trickroom(self):
        self.state.trick_room = False
        instruction = (
            constants.MUTATOR_TOGGLE_TRICKROOM,
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertTrue(self.state.trick_room)

    def test_reverse_instruction_unsets_trickroom(self):
        self.state.trick_room = True
        instruction = (
            constants.MUTATOR_TOGGLE_TRICKROOM,
        )
        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertFalse(self.state.trick_room)

    def test_reverse_instruction_sets_trickroom(self):
        self.state.trick_room = False
        instruction = (
            constants.MUTATOR_TOGGLE_TRICKROOM,
        )
        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertTrue(self.state.trick_room)

    def test_toggle_trickroom_unsets_trickroom(self):
        self.state.trick_room = True
        instruction = (
            constants.MUTATOR_TOGGLE_TRICKROOM,
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertFalse(self.state.trick_room)

    def test_apply_and_reverse_trickroom(self):
        self.state.trick_room = False
        instruction = (
            constants.MUTATOR_TOGGLE_TRICKROOM,
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)
        if not self.state.trick_room:
            self.fail("Trickroom was not set")
        self.mutator.reverse(list_of_instructions)

        self.assertFalse(self.state.trick_room)

    def test_change_types_properly_changes_types(self):
        self.state.user.active.types = ['normal']
        instruction = (
            constants.MUTATOR_CHANGE_TYPE,
            constants.USER,
            ['water'],
            self.state.user.active.types
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual(['water'], self.state.user.active.types)

    def test_reverse_change_types(self):
        self.state.user.active.types = ['water']
        instruction = (
            constants.MUTATOR_CHANGE_TYPE,
            constants.USER,
            ['water'],
            ['normal']
        )
        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(['normal'], self.state.user.active.types)

    def test_apply_and_reverse_change_types(self):
        self.state.user.active.types = ['normal']
        instruction = (
            constants.MUTATOR_CHANGE_TYPE,
            constants.USER,
            ['water', 'grass'],
            self.state.user.active.types
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)
        if self.state.user.active.types != ['water', 'grass']:
            self.fail('types were not changed')

        self.mutator.reverse(list_of_instructions)
        self.assertEqual(['normal'], self.state.user.active.types)

    def test_changing_item(self):
        self.state.user.active.item = 'some_item'
        instruction = (
            constants.MUTATOR_CHANGE_ITEM,
            constants.USER,
            'some_new_item',
            self.state.user.active.item
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)
        self.assertEqual('some_new_item', self.state.user.active.item)

    def test_reversing_changE_item(self):
        self.state.user.active.item = 'some_new_item'
        instruction = (
            constants.MUTATOR_CHANGE_ITEM,
            constants.USER,
            'some_new_item',
            'some_item'
        )
        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)
        self.assertEqual('some_item', self.state.user.active.item)

    def test_changing_item_and_reversing_item(self):
        self.state.user.active.item = 'some_item'
        instruction = (
            constants.MUTATOR_CHANGE_ITEM,
            constants.USER,
            'some_new_item',
            self.state.user.active.item
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        if self.state.user.active.item != 'some_new_item':
            self.fail('item was not changed')

        self.mutator.reverse(list_of_instructions)
        self.assertEqual('some_item', self.state.user.active.item)

    def test_wish_starting(self):
        self.state.user.wish = (0, 0)
        instruction = (
            constants.MUTATOR_WISH_START,
            constants.USER,
            100,
            0
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual((2, 100), self.state.user.wish)

    def test_wish_starting_and_reversing(self):
        self.state.user.wish = (0, 0)
        instruction = (
            constants.MUTATOR_WISH_START,
            constants.USER,
            100,
            0
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        if self.state.user.wish != (2, 100):
            self.fail("wish was not started")

        self.mutator.reverse(list_of_instructions)

        self.assertEqual((0, 0), self.state.user.wish)

    def test_previous_wish_reverses_to_exactly_the_same(self):
        self.state.user.wish = (0, 200)
        instruction = (
            constants.MUTATOR_WISH_START,
            constants.USER,
            100,
            200
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        if self.state.user.wish != (2, 100):
            self.fail("wish was not started")

        self.mutator.reverse(list_of_instructions)

        self.assertEqual((0, 200), self.state.user.wish)

    def test_decrement_wish(self):
        self.state.user.wish = (2, 100)
        instruction = (
            constants.MUTATOR_WISH_DECREMENT,
            constants.USER,
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual((1, 100), self.state.user.wish)

    def test_decrement_wish_and_reverse_decrement_wish(self):
        self.state.user.wish = (2, 100)
        instruction = (
            constants.MUTATOR_WISH_DECREMENT,
            constants.USER,
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        if self.state.user.wish != (1, 100):
            self.fail("wish was not decremented")

        self.mutator.reverse(list_of_instructions)

        self.assertEqual((2, 100), self.state.user.wish)

    def test_change_stats_basic_case(self):
        self.state.user.active.attack = 1
        self.state.user.active.defense = 2
        self.state.user.active.special_attack = 3
        self.state.user.active.special_defense = 4
        self.state.user.active.speed = 5
        instruction = (
            constants.MUTATOR_CHANGE_STATS,
            constants.USER,
            (9, 10, 11, 12, 13, 14),
            (
                self.state.user.active.maxhp,
                self.state.user.active.attack,
                self.state.user.active.defense,
                self.state.user.active.special_attack,
                self.state.user.active.special_defense,
                self.state.user.active.speed,
            ),
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual(9, self.state.user.active.maxhp)
        self.assertEqual(10, self.state.user.active.attack)
        self.assertEqual(11, self.state.user.active.defense)
        self.assertEqual(12, self.state.user.active.special_attack)
        self.assertEqual(13, self.state.user.active.special_defense)
        self.assertEqual(14, self.state.user.active.speed)

    def test_reverse_change_stats_basic_case(self):
        self.state.user.active.maxhp = 10
        self.state.user.active.attack = 1
        self.state.user.active.defense = 2
        self.state.user.active.special_attack = 3
        self.state.user.active.special_defense = 4
        self.state.user.active.speed = 5
        instruction = (
            constants.MUTATOR_CHANGE_STATS,
            constants.USER,
            (9, 10, 11, 12, 13, 14),
            (
                self.state.user.active.maxhp,
                self.state.user.active.attack,
                self.state.user.active.defense,
                self.state.user.active.special_attack,
                self.state.user.active.special_defense,
                self.state.user.active.speed,
            ),
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(10, self.state.user.active.maxhp)
        self.assertEqual(1, self.state.user.active.attack)
        self.assertEqual(2, self.state.user.active.defense)
        self.assertEqual(3, self.state.user.active.special_attack)
        self.assertEqual(4, self.state.user.active.special_defense)
        self.assertEqual(5, self.state.user.active.speed)
