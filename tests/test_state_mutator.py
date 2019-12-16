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
                defaultdict(lambda: 0)
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
                defaultdict(lambda: 0)
            ),
            None,
            None,
            False
        )
        self.mutator = StateMutator(self.state)

    def test_switch_instruction_replaces_active(self):
        instruction = (
            constants.MUTATOR_SWITCH,
            constants.SELF,
            "pikachu",
            "rattata"
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual("rattata", self.state.self.active.id)

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
            constants.SELF,
            "pikachu",
            "rattata"
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        try:
            self.state.self.reserve["pikachu"]
        except KeyError:
            self.fail("`pikachu` is not in `self.reserve`")

    def test_reverse_switch_instruction_replaces_active(self):
        instruction = (
            constants.MUTATOR_SWITCH,
            constants.SELF,
            "rattata",
            "pikachu"
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual("rattata", self.state.self.active.id)

    def test_apply_volatile_status_properly_applies_status(self):
        instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            constants.SELF,
            "leechseed"
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertIn("leechseed", self.state.self.active.volatile_status)

    def test_reverse_volatile_status_properly_removes_status(self):
        self.state.self.active.volatile_status.add("leechseed")
        instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            constants.SELF,
            "leechseed"
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertNotIn("leechseed", self.state.self.active.volatile_status)

    def test_damage_is_properly_applied(self):
        instruction = (
            constants.MUTATOR_DAMAGE,
            constants.SELF,
            50
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        damage_taken = self.state.self.active.maxhp - self.state.self.active.hp

        self.assertEqual(50, damage_taken)

    def test_damage_is_properly_reversed(self):
        self.state.self.active.hp -= 50
        instruction = (
            constants.MUTATOR_DAMAGE,
            constants.SELF,
            50
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        damage_taken = self.state.self.active.maxhp - self.state.self.active.hp

        self.assertEqual(0, damage_taken)

    def test_healing_is_properly_applied(self):
        self.state.self.active.hp -= 50
        instruction = (
            constants.MUTATOR_HEAL,
            constants.SELF,
            50
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        damage_taken = self.state.self.active.maxhp - self.state.self.active.hp

        self.assertEqual(0, damage_taken)

    def test_healing_is_properly_reversed(self):
        instruction = (
            constants.MUTATOR_HEAL,
            constants.SELF,
            50
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        damage_taken = self.state.self.active.maxhp - self.state.self.active.hp

        self.assertEqual(50, damage_taken)

    def test_boost_is_properly_applied(self):
        instruction = (
            constants.MUTATOR_BOOST,
            constants.SELF,
            constants.ATTACK,
            1
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual(1, self.state.self.active.attack_boost)

    def test_boost_is_properly_reversed(self):
        self.state.self.active.attack_boost = 1
        instruction = (
            constants.MUTATOR_BOOST,
            constants.SELF,
            constants.ATTACK,
            1
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(0, self.state.self.active.attack_boost)

    def test_boost_is_properly_reversed_when_a_boost_previously_existed(self):
        # the pokemon had attack_boost=2 before
        # it boosted to 4, and now it is being reversed
        self.state.self.active.attack_boost = 4
        instruction = (
            constants.MUTATOR_BOOST,
            constants.SELF,
            constants.ATTACK,
            2
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(2, self.state.self.active.attack_boost)

    def test_unboost_is_properly_applied(self):
        instruction = (
            constants.MUTATOR_UNBOOST,
            constants.SELF,
            constants.ATTACK,
            1
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual(-1, self.state.self.active.attack_boost)

    def test_unboost_is_properly_reversed(self):
        self.state.self.active.attack_boost = -1
        instruction = (
            constants.MUTATOR_UNBOOST,
            constants.SELF,
            constants.ATTACK,
            1
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(0, self.state.self.active.attack_boost)

    def test_apply_status_properly_applies_status(self):
        instruction = (
            constants.MUTATOR_APPLY_STATUS,
            constants.SELF,
            constants.BURN
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual(constants.BURN, self.state.self.active.status)

    def test_apply_status_is_properly_reversed(self):
        self.state.self.active.status = constants.BURN
        instruction = (
            constants.MUTATOR_APPLY_STATUS,
            constants.SELF,
            constants.BURN
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(None, self.state.self.active.status)

    def test_remove_status_properly_removes_status(self):
        self.state.self.active.status = constants.BURN
        instruction = (
            constants.MUTATOR_REMOVE_STATUS,
            constants.SELF,
            constants.BURN
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual(None, self.state.self.active.status)

    def test_remove_status_is_properly_reversed(self):
        instruction = (
            constants.MUTATOR_REMOVE_STATUS,
            constants.SELF,
            constants.BURN
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(constants.BURN, self.state.self.active.status)

    def test_side_start_is_properly_applied(self):
        instruction = (
            constants.MUTATOR_SIDE_START,
            constants.SELF,
            constants.STEALTH_ROCK,
            1
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual(1, self.state.self.side_conditions[constants.STEALTH_ROCK])

    def test_side_start_is_properly_reversed(self):
        self.state.self.side_conditions[constants.STEALTH_ROCK] = 1
        instruction = (
            constants.MUTATOR_SIDE_START,
            constants.SELF,
            constants.STEALTH_ROCK,
            1
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(0, self.state.self.side_conditions[constants.STEALTH_ROCK])

    def test_side_end_is_properly_applied(self):
        self.state.self.side_conditions[constants.STEALTH_ROCK] = 2
        instruction = (
            constants.MUTATOR_SIDE_END,
            constants.SELF,
            constants.STEALTH_ROCK,
            2
        )

        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual(0, self.state.self.side_conditions[constants.STEALTH_ROCK])

    def test_side_end_is_properly_reversed(self):
        instruction = (
            constants.MUTATOR_SIDE_END,
            constants.SELF,
            constants.STEALTH_ROCK,
            2
        )

        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(2, self.state.self.side_conditions[constants.STEALTH_ROCK])

    def test_disable_move(self):
        move = {
                'id': 'return',
                'disabled': False,
                'current_pp': 16
            }
        self.state.self.active.moves = [move]
        instruction = (
            constants.MUTATOR_DISABLE_MOVE,
            constants.SELF,
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
        self.state.self.active.moves = [move]
        instruction = (
            constants.MUTATOR_DISABLE_MOVE,
            constants.SELF,
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
        self.state.self.active.moves = [move]
        instruction = (
            constants.MUTATOR_ENABLE_MOVE,
            constants.SELF,
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
        self.state.self.active.moves = [move]
        instruction = (
            constants.MUTATOR_ENABLE_MOVE,
            constants.SELF,
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
        self.state.self.active.types = ['normal']
        instruction = (
            constants.MUTATOR_CHANGE_TYPE,
            constants.SELF,
            ['water'],
            self.state.self.active.types
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)

        self.assertEqual(['water'], self.state.self.active.types)

    def test_reverse_change_types(self):
        self.state.self.active.types = ['water']
        instruction = (
            constants.MUTATOR_CHANGE_TYPE,
            constants.SELF,
            ['water'],
            ['normal']
        )
        list_of_instructions = [instruction]
        self.mutator.reverse(list_of_instructions)

        self.assertEqual(['normal'], self.state.self.active.types)

    def test_apply_and_reverse_change_types(self):
        self.state.self.active.types = ['normal']
        instruction = (
            constants.MUTATOR_CHANGE_TYPE,
            constants.SELF,
            ['water', 'grass'],
            self.state.self.active.types
        )
        list_of_instructions = [instruction]
        self.mutator.apply(list_of_instructions)
        if self.state.self.active.types != ['water', 'grass']:
            self.fail('types were not changed')

        self.mutator.reverse(list_of_instructions)
        self.assertEqual(['normal'], self.state.self.active.types)
