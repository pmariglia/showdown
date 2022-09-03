import unittest
import constants
from showdown.engine import instruction_generator
from showdown.battle import Pokemon as StatePokemon
from showdown.engine.objects import StateMutator
from showdown.engine.objects import State
from showdown.engine.objects import Side
from showdown.engine.objects import Pokemon
from showdown.engine.objects import TransposeInstruction
from collections import defaultdict


class TestGetInstructionsFromFlinched(unittest.TestCase):
    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            None,
            None,
            False
        )
        self.previous_instructions = TransposeInstruction(1, [], False)

    def test_flinch_sets_state_to_frozen_and_returns_one_state(self):
        defender = constants.USER

        self.state.user.active.volatile_status.add(constants.FLINCH)
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_flinched(mutator, defender, self.previous_instructions)

        flinch_instruction = (
            constants.MUTATOR_REMOVE_VOLATILE_STATUS,
            defender,
            constants.FLINCH
        )

        expected_instruction = TransposeInstruction(1.0, [flinch_instruction], True)

        self.assertEqual(expected_instruction, instructions)

    def test_flinch_being_false_does_not_freeze_the_state(self):
        defender = constants.USER

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_flinched(mutator, defender, self.previous_instructions)

        expected_instruction = TransposeInstruction(1.0, [], False)

        self.assertEqual(expected_instruction, instructions)


class TestGetInstructionsFromConditionsThatFreezeState(unittest.TestCase):

    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            None,
            None,
            False
        )
        self.move = {constants.FLAGS: dict(), constants.ID: constants.DO_NOTHING_MOVE, constants.TYPE: 'normal'}

    def test_paralyzed_attacker_results_in_two_instructions(self):
        attacker = constants.OPPONENT
        defender = constants.USER
        self.state.opponent.active.status = constants.PARALYZED
        previous_instruction = TransposeInstruction(1.0, [], False)

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, self.move, self.move, previous_instruction)

        expected_instructions = [
            TransposeInstruction(1 - constants.FULLY_PARALYZED_PERCENT, [], False),
            TransposeInstruction(constants.FULLY_PARALYZED_PERCENT, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_frozen_attacker_results_in_two_instructions(self):
        attacker = constants.OPPONENT
        defender = constants.USER
        self.state.opponent.active.status = constants.FROZEN
        previous_instruction = TransposeInstruction(1.0, [], False)

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, self.move, self.move, previous_instruction)

        expected_instructions = [
            TransposeInstruction(constants.THAW_PERCENT, [('remove_status', 'opponent', 'frz')], False),
            TransposeInstruction(1 - constants.THAW_PERCENT, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_asleep_attacker_results_in_two_instructions(self):
        attacker = constants.OPPONENT
        defender = constants.USER
        self.state.opponent.active.status = constants.SLEEP
        previous_instruction = TransposeInstruction(1.0, [], False)

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, self.move, self.move, previous_instruction)

        expected_instructions = [
            TransposeInstruction(constants.WAKE_UP_PERCENT, [('remove_status', 'opponent', 'slp')], False),
            TransposeInstruction(1 - constants.WAKE_UP_PERCENT, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_powder_move_on_grass_type_does_nothing_and_freezes_the_state(self):
        attacker = constants.OPPONENT
        defender = constants.USER
        self.state.user.active.types = ['grass']
        previous_instruction = TransposeInstruction(1.0, [], False)
        move = {
            constants.FLAGS: {
                constants.POWDER: 1
            },
            constants.TYPE: ''
        }

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, move, self.move, previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_powder_move_used_by_asleep_pokemon_produces_correct_states(self):
        attacker = constants.OPPONENT
        defender = constants.USER
        self.state.opponent.active.status = constants.SLEEP
        self.state.user.active.types = ['grass']
        previous_instruction = TransposeInstruction(1.0, [], False)
        move = {
            constants.FLAGS: {
                constants.POWDER: 1
            },
            constants.TYPE: ''
        }

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, move, self.move, previous_instruction)

        expected_instructions = [
            TransposeInstruction(constants.WAKE_UP_PERCENT, [('remove_status', 'opponent', 'slp')], True),
            TransposeInstruction(1-constants.WAKE_UP_PERCENT, [], True),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_powder_against_fire_has_no_effect(self):
        attacker = constants.OPPONENT
        defender = constants.USER
        self.state.user.active.types = ['fire']
        previous_instruction = TransposeInstruction(1.0, [], False)
        move = {
            constants.FLAGS: {
                constants.POWDER: 1
            },
            constants.TYPE: ''
        }

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, move, self.move, previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False)
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetInstructionsFromDamage(unittest.TestCase):

    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            None,
            None,
            False
        )
        self.previous_instruction = TransposeInstruction(1.0, [], False)
        self.attacking_move = {
            constants.ID: constants.DO_NOTHING_MOVE
        }

    def test_100_percent_move_returns_one_state(self):
        defender = constants.USER
        damage = 50
        accuracy = 100

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_damage(mutator, defender, damage, accuracy, self.attacking_move, self.previous_instruction)

        mutator_instructions = (
            constants.MUTATOR_DAMAGE,
            defender,
            50
        )

        expected_instructions = [
            TransposeInstruction(1.0, [mutator_instructions], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_100_percent_move_with_drain_heals_the_attacker(self):
        defender = constants.USER
        damage = 50
        accuracy = 100

        # start the attacker with 10 HP
        self.state.opponent.active.hp = 10

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_damage(mutator, defender, damage, accuracy, {constants.ID: constants.DO_NOTHING_MOVE, constants.DRAIN: [1, 2]}, self.previous_instruction)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            defender,
            50
        )

        drain_instruction = (
            constants.MUTATOR_HEAL,
            constants.OPPONENT,
            25
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction, drain_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_100_percent_move_with_recoil_hurts_the_attacker(self):
        defender = constants.USER
        damage = 50
        accuracy = 100

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_damage(mutator, defender, damage, accuracy, {constants.ID: constants.DO_NOTHING_MOVE, constants.RECOIL: [1, 2]}, self.previous_instruction)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            defender,
            50
        )

        drain_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.OPPONENT,
            25
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction, drain_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_95_percent_move_with_crash_hurts_the_attacker(self):
        defender = constants.USER
        damage = 50
        accuracy = 95

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_damage(mutator, defender, damage, accuracy, {constants.ID: constants.DO_NOTHING_MOVE, constants.CRASH: [1, 2]}, self.previous_instruction)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            defender,
            50
        )

        crash_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.OPPONENT,
            self.state.opponent.active.maxhp / 2
        )

        expected_instructions = [
            TransposeInstruction(0.95, [damage_instruction], False),
            TransposeInstruction(0.050000000000000044, [crash_instruction], True),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_100_percent_move_that_does_no_damage_hurts_the_attacker(self):
        defender = constants.USER
        damage = 0
        accuracy = 100

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_damage(mutator, defender, damage, accuracy, {constants.CRASH: [1, 2]}, self.previous_instruction)

        crash_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.OPPONENT,
            self.state.opponent.active.maxhp / 2
        )

        expected_instructions = [
            TransposeInstruction(1, [crash_instruction], True),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_95_percent_move_with_no_damage_causes_crash(self):
        defender = constants.USER
        damage = 0
        accuracy = 95

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_damage(mutator, defender, damage, accuracy, {constants.CRASH: [1, 2]}, self.previous_instruction)

        crash_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.OPPONENT,
            self.state.opponent.active.maxhp / 2
        )

        expected_instructions = [
            TransposeInstruction(1, [crash_instruction], True),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_0_damage_move_with_50_accuracy_returns_one_state_that_is_frozen(self):
        defender = constants.USER
        damage = 0
        accuracy = 50

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_damage(mutator, defender, damage, accuracy, self.attacking_move, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_100_percent_killing_move_doesnt_drop_health_below_zero(self):
        defender = constants.USER
        damage = 1000
        accuracy = 100

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_damage(mutator, defender, damage, accuracy, self.attacking_move, self.previous_instruction)

        mutator_instructions = (
            constants.MUTATOR_DAMAGE,
            defender,
            self.state.user.active.maxhp
        )

        expected_instructions = [
            TransposeInstruction(1.0, [mutator_instructions], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_50_percent_move_returns_two_states_with_proper_percentages(self):
        defender = constants.USER
        damage = 50
        accuracy = 50

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_damage(mutator, defender, damage, accuracy, self.attacking_move, self.previous_instruction)

        mutator_instructions = (
            constants.MUTATOR_DAMAGE,
            defender,
            damage
        )

        expected_instructions = [
            TransposeInstruction(0.5, [mutator_instructions], False),
            TransposeInstruction(0.5, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_75_percent_move_returns_two_states_with_proper_percentages(self):
        defender = constants.USER
        damage = 50
        accuracy = 75

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_damage(mutator, defender, damage, accuracy, self.attacking_move, self.previous_instruction)

        mutator_instructions = (
            constants.MUTATOR_DAMAGE,
            defender,
            damage
        )

        expected_instructions = [
            TransposeInstruction(0.75, [mutator_instructions], False),
            TransposeInstruction(0.25, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_0_percent_move_returns_one_state_with_no_changes(self):
        defender = constants.USER
        damage = 50
        accuracy = 0

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_damage(mutator, defender, damage, accuracy, self.attacking_move, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], True),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_100_percent_move_returns_one_state_when_state_percentage_already_existed(self):
        defender = constants.USER
        damage = 50
        accuracy = 100

        # pre-set the previous percentage to ensure it is updated properly
        self.previous_instruction.percentage = 0.5

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_damage(mutator, defender, damage, accuracy, self.attacking_move, self.previous_instruction)

        mutator_instructions = (
            constants.MUTATOR_DAMAGE,
            defender,
            damage
        )

        expected_instructions = [
            TransposeInstruction(0.5, [mutator_instructions], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_frozen_state_does_not_change(self):
        defender = constants.USER
        damage = 50
        accuracy = 100

        # a frozen state usually has a percentage, though for testing it doesn't matter
        self.previous_instruction.percentage = 0.1
        self.previous_instruction.frozen = True

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_damage(mutator, defender, damage, accuracy, self.attacking_move, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(0.1, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetInstructionsFromSideConditions(unittest.TestCase):
    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            None,
            None,
            False
        )
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_using_stealthrock_sets_side_condition(self):
        side_string = constants.OPPONENT
        condition = constants.STEALTH_ROCK

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_side_conditions(mutator, constants.USER, side_string, condition, self.previous_instruction)

        expected_mutator_instructions = (
            constants.MUTATOR_SIDE_START,
            side_string,
            condition,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [expected_mutator_instructions], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_using_spikes_sets_side_condition(self):
        side_string = constants.OPPONENT
        condition = constants.SPIKES

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_side_conditions(mutator, constants.USER, side_string, condition, self.previous_instruction)

        expected_mutator_instructions = (
            constants.MUTATOR_SIDE_START,
            side_string,
            condition,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [expected_mutator_instructions], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_spikes_can_have_more_than_one(self):
        side_string = constants.OPPONENT
        condition = constants.SPIKES

        self.state.opponent.side_conditions[constants.SPIKES] = 1

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_side_conditions(mutator, constants.USER, side_string, condition, self.previous_instruction)

        expected_mutator_instructions = (
            constants.MUTATOR_SIDE_START,
            side_string,
            condition,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [expected_mutator_instructions], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_spikes_stops_at_3(self):
        side_string = constants.OPPONENT
        condition = constants.SPIKES

        self.state.opponent.side_conditions[constants.SPIKES] = 3

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_side_conditions(mutator, constants.USER, side_string, condition, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_using_stealthrock_into_side_already_containing_stealthrock_does_nothing(self):
        side_string = constants.OPPONENT
        condition = constants.STEALTH_ROCK

        self.state.opponent.side_conditions[constants.STEALTH_ROCK] = 1

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_side_conditions(mutator, constants.USER, side_string, condition, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False)
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetInstructionsFromHazardClearingMoves(unittest.TestCase):
    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            None,
            None,
            False
        )
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_rapidspin_clears_stealthrocks(self):
        attacker_string = constants.USER
        self.state.user.side_conditions[constants.STEALTH_ROCK] = 1

        move = {
            constants.ID: 'rapidspin'
        }

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_hazard_clearing_moves(mutator, attacker_string, move, self.previous_instruction)

        expected_mutator_instructions = [(
            constants.MUTATOR_SIDE_END,
            attacker_string,
            constants.STEALTH_ROCK,
            1
        )]

        expected_instructions = [
            TransposeInstruction(1.0, expected_mutator_instructions, False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_rapidspin_clears_stealthrocks_and_spikes(self):
        attacker_string = constants.USER
        self.state.user.side_conditions[constants.STEALTH_ROCK] = 1
        self.state.user.side_conditions[constants.SPIKES] = 3

        move = {
            constants.ID: 'rapidspin'
        }

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_hazard_clearing_moves(mutator, attacker_string, move, self.previous_instruction)

        expected_mutator_instructions = [
            (
                constants.MUTATOR_SIDE_END,
                attacker_string,
                constants.STEALTH_ROCK,
                1
            ),
            (
                constants.MUTATOR_SIDE_END,
                attacker_string,
                constants.SPIKES,
                3
            ),
        ]

        expected_instructions = [
            TransposeInstruction(1.0, expected_mutator_instructions, False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_defog_clears_both_sides_side_conditions(self):
        attacker_string = constants.USER
        defender_string = constants.OPPONENT
        self.state.user.side_conditions[constants.STEALTH_ROCK] = 1
        self.state.user.side_conditions[constants.SPIKES] = 3
        self.state.opponent.side_conditions[constants.STEALTH_ROCK] = 1
        self.state.opponent.side_conditions[constants.SPIKES] = 1
        self.state.opponent.side_conditions[constants.REFLECT] = 1

        move = {
            constants.ID: 'defog'
        }

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_hazard_clearing_moves(mutator, attacker_string, move, self.previous_instruction)

        expected_mutator_instructions = [
            (
                constants.MUTATOR_SIDE_END,
                attacker_string,
                constants.STEALTH_ROCK,
                1
            ),
            (
                constants.MUTATOR_SIDE_END,
                attacker_string,
                constants.SPIKES,
                3
            ),
            (
                constants.MUTATOR_SIDE_END,
                defender_string,
                constants.STEALTH_ROCK,
                1
            ),
            (
                constants.MUTATOR_SIDE_END,
                defender_string,
                constants.SPIKES,
                1
            ),
            (
                constants.MUTATOR_SIDE_END,
                defender_string,
                constants.REFLECT,
                1
            )
        ]

        expected_instructions = [
            TransposeInstruction(1.0, expected_mutator_instructions, False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_rapidspin_does_not_clear_reflect(self):
        attacker_string = constants.USER
        defender_string = constants.OPPONENT
        self.state.user.side_conditions[constants.REFLECT] = 1

        move = {
            constants.ID: 'rapidspin'
        }

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_hazard_clearing_moves(mutator, attacker_string, move, self.previous_instruction)

        expected_mutator_instructions = []

        expected_instructions = [
            TransposeInstruction(1.0, expected_mutator_instructions, False)
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetInstructionsFromDirectStatusEffects(unittest.TestCase):

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
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            None,
            None,
            False
        )
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_100_percent_status_returns_one_state(self):
        status = constants.BURN
        accuracy = 100
        defender = constants.USER

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_status_effects(mutator, defender, status, accuracy, self.previous_instruction)

        mutator_instructions = (
            constants.MUTATOR_APPLY_STATUS,
            defender,
            status
        )

        expected_instructions = [
            TransposeInstruction(1.0, [mutator_instructions], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_status_cannot_be_inflicted_on_pkmn_in_substitute(self):
        self.state.user.active.volatile_status.add(constants.SUBSTITUTE)
        status = constants.BURN
        accuracy = 100
        defender = constants.USER

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_status_effects(mutator, defender, status, accuracy, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_75_percent_status_returns_two_states(self):
        status = constants.BURN
        accuracy = 75
        defender = constants.USER

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_status_effects(mutator, defender, status, accuracy, self.previous_instruction)

        mutator_instructions = (
            constants.MUTATOR_APPLY_STATUS,
            defender,
            status
        )

        expected_instructions = [
            TransposeInstruction(0.75, [mutator_instructions], False),
            TransposeInstruction(0.25, [], True)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_frozen_pokemon_cannot_be_burned(self):
        status = constants.BURN
        accuracy = 100
        defender = constants.USER

        # set 'frozen' in the defender's active statuses
        self.state.user.active.status = constants.FROZEN

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_status_effects(mutator, defender, status, accuracy, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_sleep_clause_activates(self):
        status = constants.SLEEP
        accuracy = 100
        defender = constants.USER

        self.state.user.reserve['rattata'].status = constants.SLEEP

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_status_effects(mutator, defender, status, accuracy, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_poison_type_cannot_be_poisoned(self):
        status = constants.POISON
        accuracy = 100
        defender = constants.USER

        self.state.user.active.types = ['poison']

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_status_effects(mutator, defender, status, accuracy, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_switching_in_pokemon_cannot_be_statused_if_it_is_already_statused(self):
        status = constants.POISON
        accuracy = 100
        defender = constants.USER

        self.state.user.reserve['rattata'].status = constants.PARALYZED

        switch_instruction = (
            constants.MUTATOR_SWITCH,
            constants.USER,
            'pikachu',
            'rattata'
        )
        self.previous_instruction.instructions = [
            switch_instruction
        ]

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_status_effects(mutator, defender, status, accuracy, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(
                1.0,
                [switch_instruction],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_steel_type_cannot_be_poisoned(self):
        status = constants.POISON
        accuracy = 100
        defender = constants.USER

        self.state.user.active.types = ['steel']

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_status_effects(mutator, defender, status, accuracy, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_frozen_state_cannot_be_changed(self):
        status = constants.BURN
        accuracy = 100
        defender = constants.USER

        # freeze the state
        self.previous_instruction.frozen = True

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_status_effects(mutator, defender, status, accuracy, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], True),
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetInstructionsFromBoosts(unittest.TestCase):

    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            None,
            None,
            False
        )
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_no_boosts_results_in_one_unchanged_state(self):
        boosts = {}
        accuracy = True
        side = constants.USER

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_boosts(mutator, side, boosts, accuracy, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_boosts_cannot_exceed_max_boosts(self):
        self.state.user.active.attack_boost = 6
        boosts = {
            constants.ATTACK: 1
        }
        accuracy = True
        side = constants.USER

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_boosts(mutator, side, boosts, accuracy, self.previous_instruction)

        boost_instruction = (
            constants.MUTATOR_BOOST,
            side,
            constants.ATTACK,
            0
        )

        expected_instructions = [
            TransposeInstruction(1.0, [boost_instruction], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_boosts_cannot_go_below_min_boosts(self):
        self.state.user.active.attack_boost = -1 * constants.MAX_BOOSTS
        boosts = {
            constants.ATTACK: -1
        }
        accuracy = True
        side = constants.USER

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_boosts(mutator, side, boosts, accuracy, self.previous_instruction)

        boost_instruction = (
            constants.MUTATOR_BOOST,
            side,
            constants.ATTACK,
            0
        )

        expected_instructions = [
            TransposeInstruction(1.0, [boost_instruction], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_boosts_cannot_go_below_min_boosts_with_previous_instruction_lowering_boost(self):

        self.previous_instruction = TransposeInstruction(
            1,
            [
                (constants.MUTATOR_UNBOOST, constants.USER, constants.ATTACK, 5)
            ],
            False
        )

        boosts = {
            constants.ATTACK: -2
        }
        accuracy = True
        side = constants.USER

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_boosts(mutator, side, boosts, accuracy, self.previous_instruction)

        boost_instruction = (
            constants.MUTATOR_BOOST,
            side,
            constants.ATTACK,
            -1
        )

        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    self.previous_instruction.instructions[0],
                    boost_instruction,

                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_boosts_cannot_go_below_min_boosts_with_previous_instruction_lowering_boost_with_percentage_hit_not_1(self):

        self.previous_instruction = TransposeInstruction(
            1,
            [
                (constants.MUTATOR_UNBOOST, constants.USER, constants.ATTACK, 5)
            ],
            False
        )

        boosts = {
            constants.ATTACK: -2
        }
        accuracy = 60
        side = constants.USER

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_boosts(mutator, side, boosts, accuracy, self.previous_instruction)

        boost_instruction = (
            constants.MUTATOR_BOOST,
            side,
            constants.ATTACK,
            -1
        )

        expected_instructions = [
            TransposeInstruction(
                0.6,
                [
                    self.previous_instruction.instructions[0],
                    boost_instruction,

                ],
                False
            ),
            TransposeInstruction(
                0.4,
                [
                    self.previous_instruction.instructions[0],

                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_guaranteed_atk_boost_returns_one_state(self):
        boosts = {
            constants.ATTACK: 1
        }
        accuracy = True
        side = constants.USER

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_boosts(mutator, side, boosts, accuracy, self.previous_instruction)

        boost_instruction = (
            constants.MUTATOR_BOOST,
            side,
            constants.ATTACK,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [boost_instruction], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_50_percent_boost_returns_two_states(self):
        boosts = {
            constants.ATTACK: 1
        }
        accuracy = 50
        side = constants.USER

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_boosts(mutator, side, boosts, accuracy, self.previous_instruction)

        boost_instruction = (
            constants.MUTATOR_BOOST,
            side,
            constants.ATTACK,
            1
        )

        expected_instructions = [
            TransposeInstruction(0.5, [boost_instruction], False),
            TransposeInstruction(0.5, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_guaranteed_atk_boost_returns_one_state_when_attack_boost_already_existed(self):
        self.state.user.active.attack_boost = 1
        boosts = {
            constants.ATTACK: 1
        }
        accuracy = True
        side = constants.USER

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_boosts(mutator, side, boosts, accuracy, self.previous_instruction)

        boost_instruction = (
            constants.MUTATOR_BOOST,
            side,
            constants.ATTACK,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [boost_instruction], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_pre_existing_boost_does_not_affect_new_boost(self):
        boosts = {
            constants.ATTACK: 1
        }
        accuracy = True
        side = constants.USER

        self.state.user.active.defense_boost = 1
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_boosts(mutator, side, boosts, accuracy, self.previous_instruction)

        boost_instruction = (
            constants.MUTATOR_BOOST,
            side,
            constants.ATTACK,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [boost_instruction], False)
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_multiple_new_boosts_with_multiple_pre_existing_boosts(self):
        boosts = {
            constants.ATTACK: 1,
            constants.DEFENSE: 1
        }
        accuracy = True
        side = constants.USER

        self.state.user.active.defense_boost = 1
        self.state.user.active.speed_boost = 1
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_boosts(mutator, side, boosts, accuracy, self.previous_instruction)

        attack_boost_instruction = (
            constants.MUTATOR_BOOST,
            side,
            constants.ATTACK,
            1
        )
        defense_boost_instruction = (
            constants.MUTATOR_BOOST,
            side,
            constants.DEFENSE,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [attack_boost_instruction, defense_boost_instruction], False)
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetInstructionsFromSpecialLogicMoves(unittest.TestCase):
    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            None,
            None,
            False
        )
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_works_with_previous_instructions(self):
        self.previous_instruction = TransposeInstruction(
            1,
            [
                (constants.MUTATOR_WEATHER_START, constants.SUN, None)
            ],
            False
        )

        move_name = constants.RAIN
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_move_special_effect(mutator, constants.USER, mutator.state.user.active, mutator.state.opponent.active, move_name, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    (constants.MUTATOR_WEATHER_START, constants.SUN, None),
                    (constants.MUTATOR_WEATHER_START, constants.RAIN, constants.SUN),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetInstructionsFromFlinchingMoves(unittest.TestCase):

    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            None,
            None,
            False
        )
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_30_percent_flinching_move_returns_two_states(self):
        accuracy = 30
        defender = constants.USER

        instructions = instruction_generator.get_instructions_from_flinching_moves(defender, accuracy, True, self.previous_instruction)

        flinched_instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            defender,
            constants.FLINCH
        )

        expected_instructions = [
            TransposeInstruction(0.3, [flinched_instruction], False),
            TransposeInstruction(0.7, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_100_percent_flinching_move_returns_one_state(self):
        accuracy = 100
        defender = constants.USER

        instructions = instruction_generator.get_instructions_from_flinching_moves(defender, accuracy, True, self.previous_instruction)

        flinched_instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            defender,
            constants.FLINCH
        )

        expected_instructions = [
            TransposeInstruction(1.0, [flinched_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_0_percent_flinching_move_returns_one_state(self):
        accuracy = 0
        defender = constants.USER

        instructions = instruction_generator.get_instructions_from_flinching_moves(defender, accuracy, True, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_pre_exising_percentage_propagates_downward(self):
        accuracy = 30
        defender = constants.USER

        self.previous_instruction.percentage = 0.5
        instructions = instruction_generator.get_instructions_from_flinching_moves(defender, accuracy, True, self.previous_instruction)

        flinched_instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            defender,
            constants.FLINCH
        )

        expected_instructions = [
            TransposeInstruction(0.15, [flinched_instruction], False),
            TransposeInstruction(0.35, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetStateFromSwitch(unittest.TestCase):
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
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_basic_switch_with_no_side_effects(self):
        attacker = constants.USER
        switch_pokemon_name = "rattata"

        expected_instructions = TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_SWITCH,
                    attacker,
                    self.state.user.active.id,
                    switch_pokemon_name
                ),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switching_into_pokemon_with_grassyseed_causes_that_seed_boost_to_occur_if_terrain_is_up(self):
        attacker = constants.USER
        switch_pokemon_name = "rattata"
        self.state.user.reserve["rattata"].item = "grassyseed"
        self.state.field = "grassyterrain"

        expected_instructions = TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_SWITCH,
                    attacker,
                    self.state.user.active.id,
                    switch_pokemon_name
                ),
                (
                    constants.MUTATOR_BOOST,
                    attacker,
                    constants.DEFENSE,
                    1
                ),
                (
                    constants.MUTATOR_CHANGE_ITEM,
                    attacker,
                    None,
                    "grassyseed"
                ),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_seed_boost_doesnt_occur_if_stat_is_maxed(self):
        attacker = constants.USER
        switch_pokemon_name = "rattata"
        self.state.user.reserve["rattata"].item = "grassyseed"
        self.state.field = constants.GRASSY_TERRAIN

        # this literally cant happen for a pkmn switching in but worth a check I guess?
        self.state.user.reserve["rattata"].defense_boost = 6

        expected_instructions = TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_SWITCH,
                    attacker,
                    self.state.user.active.id,
                    switch_pokemon_name
                )
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switching_into_pokemon_with_psychicseed_causes_that_seed_boost_to_occur_if_terrain_is_up(self):
        attacker = constants.USER
        switch_pokemon_name = "rattata"
        self.state.user.reserve["rattata"].item = "psychicseed"
        self.state.field = constants.PSYCHIC_TERRAIN

        expected_instructions =  TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_SWITCH,
                    attacker,
                    self.state.user.active.id,
                    switch_pokemon_name
                ),
                (
                    constants.MUTATOR_BOOST,
                    attacker,
                    constants.SPECIAL_DEFENSE,
                    1
                ),
                (
                    constants.MUTATOR_CHANGE_ITEM,
                    attacker,
                    None,
                    "psychicseed"
                ),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_unboosts_active_pokemon(self):
        self.state.user.active.attack_boost = 3
        self.state.user.active.defense_boost = 2
        attacker = constants.USER
        switch_pokemon_name = "rattata"

        expected_instructions = TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_UNBOOST,
                    attacker,
                    constants.ATTACK,
                    3
                ),
                (
                    constants.MUTATOR_UNBOOST,
                    attacker,
                    constants.DEFENSE,
                    2
                ),
                (
                    constants.MUTATOR_SWITCH,
                    attacker,
                    self.state.user.active.id,
                    switch_pokemon_name
                ),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_stealth_rock_gives_damage_instruction(self):
        self.state.user.side_conditions[constants.STEALTH_ROCK] = 1
        attacker = constants.USER
        switch_pokemon_name = "rattata"

        expected_instructions = TransposeInstruction(
            1,
            [
                ('switch', 'user', 'pikachu', 'rattata'),
                (
                    constants.MUTATOR_DAMAGE,
                    attacker,
                    27.75  # 1/8th of rattata's 222 maxhp is 27.75 damage
                ),
            ]
            ,
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_regenerator_heals_one_third_hp(self):
        attacker = constants.USER
        switch_pokemon_name = "rattata"
        self.state.user.active.hp = 1
        self.state.user.active.ability = 'regenerator'

        expected_instructions = TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_HEAL,
                    attacker,
                    77  # 1/3rd of pikachu's maxhp is 77
                ),
                ('switch', 'user', 'pikachu', 'rattata'),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_regenerator_does_not_overheal(self):
        attacker = constants.USER
        switch_pokemon_name = "rattata"
        self.state.user.active.hp -= 1
        self.state.user.active.ability = 'regenerator'

        expected_instructions = TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_HEAL,
                    attacker,
                    1
                ),
                ('switch', 'user', 'pikachu', 'rattata'),

            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_toxicspikes_causes_poison(self):
        self.state.user.side_conditions[constants.TOXIC_SPIKES] = 1
        attacker = constants.USER
        switch_pokemon_name = "rattata"

        expected_instructions = TransposeInstruction(
            1,
            [
                ('switch', 'user', 'pikachu', 'rattata'),
                (
                    constants.MUTATOR_APPLY_STATUS,
                    attacker,
                    constants.POISON,
                ),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_poison_switch_into_toxicspikes_clears_the_spikes(self):
        self.state.user.side_conditions[constants.TOXIC_SPIKES] = 1
        attacker = constants.USER
        switch_pokemon_name = "rattata"

        self.state.user.reserve[switch_pokemon_name].types = ['poison']

        expected_instructions = TransposeInstruction(
            1,
            [
                ('switch', 'user', 'pikachu', 'rattata'),
                (
                    constants.MUTATOR_SIDE_END,
                    attacker,
                    constants.TOXIC_SPIKES,
                    1
                ),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_poison_switch_into_two_toxicspikes_clears_the_spikes(self):
        self.state.user.side_conditions[constants.TOXIC_SPIKES] = 2
        attacker = constants.USER
        switch_pokemon_name = "rattata"

        self.state.user.reserve[switch_pokemon_name].types = ['poison']

        expected_instructions = TransposeInstruction(
            1,
            [
                ('switch', 'user', 'pikachu', 'rattata'),
                (
                    constants.MUTATOR_SIDE_END,
                    attacker,
                    constants.TOXIC_SPIKES,
                    2
                ),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_flying_poison_doesnt_clear_toxic_spikes(self):
        self.state.user.side_conditions[constants.TOXIC_SPIKES] = 2
        attacker = constants.USER
        switch_pokemon_name = "rattata"

        self.state.user.reserve[switch_pokemon_name].types = ['poison', 'flying']

        expected_instructions = TransposeInstruction(
            1,
            [
                ('switch', 'user', 'pikachu', 'rattata'),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_double_toxicspikes_causes_toxic(self):
        self.state.user.side_conditions[constants.TOXIC_SPIKES] = 2
        attacker = constants.USER
        switch_pokemon_name = "rattata"

        expected_instructions = TransposeInstruction(
            1,
            [
                ('switch', 'user', 'pikachu', 'rattata'),
                (
                    constants.MUTATOR_APPLY_STATUS,
                    attacker,
                    constants.TOXIC,
                ),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_flying_immune_to_toxicspikes(self):
        self.state.user.side_conditions[constants.TOXIC_SPIKES] = 2
        attacker = constants.USER
        switch_pokemon_name = "rattata"

        self.state.user.reserve[switch_pokemon_name].types = ['flying']

        expected_instructions = TransposeInstruction(
            1,
            [
                ('switch', 'user', 'pikachu', 'rattata'),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_stick_web_drops_speed(self):
        self.state.user.side_conditions[constants.STICKY_WEB] = 1
        attacker = constants.USER
        switch_pokemon_name = "rattata"

        expected_instructions = TransposeInstruction(
            1,
            [
                ('switch', 'user', 'pikachu', 'rattata'),
                (
                    constants.MUTATOR_UNBOOST,
                    attacker,
                    constants.SPEED,
                    1
                ),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_levitate_ability_does_not_cause_sticky_web_effect(self):
        self.state.user.side_conditions[constants.STICKY_WEB] = 1
        attacker = constants.USER
        switch_pokemon_name = "rattata"

        self.state.user.reserve[switch_pokemon_name].ability = 'levitate'

        expected_instructions = TransposeInstruction(
            1,
            [
                ('switch', 'user', 'pikachu', 'rattata'),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_airballoon_item_does_not_cause_sticky_web_effect(self):
        self.state.user.side_conditions[constants.STICKY_WEB] = 1
        attacker = constants.USER
        switch_pokemon_name = "rattata"

        self.state.user.reserve[switch_pokemon_name].item = 'airballoon'

        expected_instructions = TransposeInstruction(
            1,
            [
                ('switch', 'user', 'pikachu', 'rattata'),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_flying_switch_into_sticky_web_does_not_drop_speed(self):
        self.state.user.side_conditions[constants.STICKY_WEB] = 1
        attacker = constants.USER
        switch_pokemon_name = "rattata"

        self.state.user.reserve[switch_pokemon_name].types = ['flying']

        expected_instructions = TransposeInstruction(
            1,
            [
                ('switch', 'user', 'pikachu', 'rattata'),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_stealth_rock_with_1hp_gives_damage_instruction_of_1hp(self):
        self.state.user.side_conditions[constants.STEALTH_ROCK] = 1
        self.state.user.reserve["rattata"].hp = 1
        attacker = constants.USER
        switch_pokemon_name = "rattata"

        expected_instructions = TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_SWITCH,
                    attacker,
                    self.state.user.active.id,
                    switch_pokemon_name
                ),
                (
                    constants.MUTATOR_DAMAGE,
                    attacker,
                    1
                ),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_stealth_rock_as_flying_does_more_damage(self):
        self.state.user.side_conditions[constants.STEALTH_ROCK] = 1
        attacker = constants.USER
        switch_pokemon_name = "pidgey"

        expected_instructions = TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_SWITCH,
                    attacker,
                    self.state.user.active.id,
                    switch_pokemon_name
                ),
                (
                    constants.MUTATOR_DAMAGE,
                    attacker,
                    60.5  # 1/4 of pidgey's 242 max hp is 60.5
                ),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_three_spikes_as_flying_does_nothing(self):
        self.state.user.side_conditions[constants.SPIKES] = 3
        attacker = constants.USER
        switch_pokemon_name = "pidgey"

        expected_instructions = TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_SWITCH,
                    attacker,
                    self.state.user.active.id,
                    switch_pokemon_name
                )
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_volatile_status_is_removed_on_switch_out(self):
        self.state.user.active.volatile_status = {"leechseed"}
        attacker = constants.USER
        switch_pokemon_name = "pidgey"

        expected_instructions = TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_REMOVE_VOLATILE_STATUS,
                    constants.USER,
                    "leechseed"
                ),
                (
                    constants.MUTATOR_SWITCH,
                    attacker,
                    self.state.user.active.id,
                    switch_pokemon_name
                )
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_toxic_count_is_reset_if_it_exists_on_switch_out(self):
        self.state.user.side_conditions[constants.TOXIC_COUNT] = 2
        attacker = constants.USER
        switch_pokemon_name = "pidgey"

        expected_instructions = TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_SIDE_END,
                    constants.USER,
                    constants.TOXIC_COUNT,
                    2
                ),
                (
                    constants.MUTATOR_SWITCH,
                    attacker,
                    self.state.user.active.id,
                    switch_pokemon_name
                )
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_pokemon_with_drought_sets_weather(self):
        attacker = constants.USER
        switch_pokemon_name = "pidgey"
        self.state.user.reserve[switch_pokemon_name].ability = "drought"

        expected_instructions = TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_SWITCH,
                    attacker,
                    self.state.user.active.id,
                    switch_pokemon_name
                ),
                (
                    constants.MUTATOR_WEATHER_START,
                    constants.SUN,
                    None
                ),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_pokemon_with_drizze_sets_weather(self):
        attacker = constants.USER
        switch_pokemon_name = "pidgey"
        self.state.user.reserve[switch_pokemon_name].ability = "drizzle"

        expected_instructions = TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_SWITCH,
                    attacker,
                    self.state.user.active.id,
                    switch_pokemon_name
                ),
                (
                    constants.MUTATOR_WEATHER_START,
                    constants.RAIN,
                    None
                ),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_pokemon_with_drizze_does_not_set_weather_when_desolate_land_is_active(self):
        attacker = constants.USER
        switch_pokemon_name = "pidgey"
        self.state.weather = 'desolateland'
        self.state.user.reserve[switch_pokemon_name].ability = 'drizzle'

        expected_instructions = TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_SWITCH,
                    attacker,
                    self.state.user.active.id,
                    switch_pokemon_name
                ),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_pokemon_with_desolateland_sets_weather_when_primordial_sea_is_active(self):
        attacker = constants.USER
        switch_pokemon_name = "pidgey"
        self.state.weather = constants.HEAVY_RAIN
        self.state.user.reserve[switch_pokemon_name].ability = constants.DESOLATE_LAND

        expected_instructions = TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_SWITCH,
                    attacker,
                    self.state.user.active.id,
                    switch_pokemon_name
                ),
                (
                    constants.MUTATOR_WEATHER_START,
                    constants.DESOLATE_LAND,
                    constants.HEAVY_RAIN
                ),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_pokemon_with_primordialsea_sets_weather_when_desolateland_is_active(self):
        attacker = constants.USER
        switch_pokemon_name = "pidgey"
        self.state.weather = constants.DESOLATE_LAND
        self.state.user.reserve[switch_pokemon_name].ability = constants.HEAVY_RAIN

        expected_instructions = TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_SWITCH,
                    attacker,
                    self.state.user.active.id,
                    switch_pokemon_name
                ),
                (
                    constants.MUTATOR_WEATHER_START,
                    constants.HEAVY_RAIN,
                    constants.DESOLATE_LAND
                ),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_intimidate_lowers_opponent_attack(self):
        attacker = constants.USER
        switch_pokemon_name = "pidgey"
        self.state.user.reserve[switch_pokemon_name].ability = 'intimidate'

        expected_instructions = TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_SWITCH,
                    attacker,
                    self.state.user.active.id,
                    switch_pokemon_name
                ),
                (
                    constants.MUTATOR_UNBOOST,
                    constants.OPPONENT,
                    constants.ATTACK,
                    1
                ),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_intimidate_does_not_lower_attack_when_already_at_negative_6(self):
        attacker = constants.USER
        switch_pokemon_name = "pidgey"
        self.state.user.reserve[switch_pokemon_name].ability = 'intimidate'
        self.state.opponent.active.attack_boost = -6

        expected_instructions = TransposeInstruction(
            1,
            [
                (
                    constants.MUTATOR_SWITCH,
                    attacker,
                    self.state.user.active.id,
                    switch_pokemon_name
                ),
            ],
            False
        )

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_switch(mutator, attacker, switch_pokemon_name, self.previous_instruction)

        self.assertEqual(expected_instructions, instructions)


class TestGetStateFromHealingMoves(unittest.TestCase):
    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                {
                    'rattata': Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    'charmander': Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    'squirtle': Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    'bulbasaur': Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    'pidgey': Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                },
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                {
                    'rattata': Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    'charmander': Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    'squirtle': Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    'bulbasaur': Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    'pidgey': Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                },
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            None,
            None,
            False
        )
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_returns_one_state_with_health_recovered(self):
        self.state.user.active.hp = 50  # this ensures the entire 1/3 * maxhp is in the instruction
        attacker = constants.USER
        move = {
            constants.TARGET: constants.USER,
            constants.HEAL: [1, 3],
            constants.HEAL_TARGET: constants.USER
        }

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_attacker_recovery(mutator, attacker, move, self.previous_instruction)

        heal_instruction = (
            constants.MUTATOR_HEAL,
            attacker,
            1/3 * self.state.user.active.maxhp
        )

        expected_instructions = [
            TransposeInstruction(1.0, [heal_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_previous_instruction_affect_this_instruction(self):
        self.state.user.active.hp = self.state.user.active.maxhp  # this ensures that only the damage taken in previous instructions is recoverable
        self.previous_instruction = TransposeInstruction(
            1,
            [
                (constants.MUTATOR_DAMAGE, constants.USER, 15)
            ],
            False
        )

        attacker = constants.USER
        move = {
            constants.TARGET: constants.USER,
            constants.HEAL: [1, 3],
            constants.HEAL_TARGET: constants.USER
        }

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_attacker_recovery(mutator, attacker, move, self.previous_instruction)

        heal_instruction = (
            constants.MUTATOR_HEAL,
            attacker,
            15.000000000000014
        )

        expected_instructions = [
            TransposeInstruction(1.0, [self.previous_instruction.instructions[0], heal_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_previous_instructions_result_in_correct_recovery(self):
        self.state.user.active.hp = 50

        self.previous_instruction = TransposeInstruction(
            1,
            [
                (constants.MUTATOR_SWITCH, constants.USER, 'pikachu', 'rattata')
            ],
            False
        )

        attacker = constants.USER
        move = {
            constants.TARGET: constants.USER,
            constants.HEAL: [1, 3],
            constants.HEAL_TARGET: constants.USER
        }

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_attacker_recovery(mutator, attacker, move, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, self.previous_instruction.instructions, False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_healing_does_not_exceed_max_health(self):
        self.state.user.active.hp = self.state.user.active.maxhp
        attacker = constants.USER
        move = {
            constants.TARGET: constants.USER,
            constants.HEAL: [1, 1],
            constants.HEAL_TARGET: constants.USER
        }

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_attacker_recovery(mutator, attacker, move, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_negative_healing(self):
        attacker = constants.USER
        move = {
            constants.TARGET: constants.NORMAL,
            constants.HEAL: [-1, 2],
            constants.HEAL_TARGET: constants.USER
        }

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_attacker_recovery(mutator, attacker, move, self.previous_instruction)

        heal_instruction = (
            constants.MUTATOR_HEAL,
            constants.USER,
            -1 / 2 * self.state.user.active.maxhp
        )

        expected_instructions = [
            TransposeInstruction(1.0, [heal_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_frozen_state_does_not_change(self):
        attacker = constants.USER
        move = {
            constants.TARGET: constants.USER,
            constants.HEAL: [1, 3],
            constants.HEAL_TARGET: constants.USER
        }

        self.previous_instruction.frozen = True

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_attacker_recovery(mutator, attacker, move, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], True),
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetStateFromVolatileStatus(unittest.TestCase):
    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            None,
            None,
            False
        )
        self.previous_instruction = TransposeInstruction(1.0, [], False)

    def test_returns_one_state_with_volatile_status_set(self):
        volatile_status = 'leechseed'
        attacker = constants.OPPONENT
        target = constants.NORMAL
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_volatile_statuses(mutator, volatile_status, attacker, target, True, self.previous_instruction)

        instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            constants.USER,
            volatile_status
        )

        expected_instructions = [
            TransposeInstruction(1.0, [instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_frozen_state_is_unaffected(self):
        volatile_status = 'leechseed'
        attacker = constants.OPPONENT
        target = constants.NORMAL
        self.previous_instruction.frozen = True

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_volatile_statuses(mutator, volatile_status, attacker, target, True, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], True),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_does_not_alter_pre_existing_volatile_status(self):
        volatile_status = 'leechseed'
        attacker = constants.OPPONENT
        target = constants.NORMAL
        self.state.user.active.volatile_status.add('confusion')

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_volatile_statuses(mutator, volatile_status, attacker, target, True, self.previous_instruction)

        instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            constants.USER,
            volatile_status
        )

        expected_instructions = [
            TransposeInstruction(1.0, [instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_does_not_apply_duplicate_status(self):
        volatile_status = 'leechseed'
        attacker = constants.OPPONENT
        target = constants.NORMAL
        self.state.user.active.volatile_status.add(volatile_status)

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_volatile_statuses(mutator, volatile_status, attacker, target, True, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_does_not_apply_status_if_substitute_is_active_on_pokemon(self):
        volatile_status = 'leechseed'
        attacker = constants.OPPONENT
        target = constants.NORMAL
        self.state.user.active.volatile_status.add('substitute')

        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_instructions_from_volatile_statuses(mutator, volatile_status, attacker, target, True, self.previous_instruction)

        expected_instructions = [
            TransposeInstruction(1.0, [], False),
        ]

        self.assertEqual(expected_instructions, instructions)


class TestGetStateFromStatusDamage(unittest.TestCase):
    def setUp(self):
        self.state = State(
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            Side(
                Pokemon.from_state_pokemon_dict(StatePokemon("pikachu", 100).to_dict()),
                [
                    Pokemon.from_state_pokemon_dict(StatePokemon("rattata", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("charmander", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("squirtle", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("bulbasaur", 100).to_dict()),
                    Pokemon.from_state_pokemon_dict(StatePokemon("pidgey", 100).to_dict())
                ],
                (0, 0),
                defaultdict(lambda: 0),
                (0, 0)
            ),
            None,
            None,
            False
        )
        self.previous_instruction = TransposeInstruction(1.0, [], False)
        self.dummy_move = {
            constants.ID: constants.DO_NOTHING_MOVE
        }

    def test_poison_does_one_eigth_damage(self):
        side = constants.USER
        self.state.user.active.status = constants.POISON
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        instruction = (
            constants.MUTATOR_DAMAGE,
            side,
            self.state.user.active.maxhp * 0.125
        )

        expected_instructions = [
            TransposeInstruction(1.0, [instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_toxic_does_one_sixteenth_damage_when_toxic_count_is_zero_and_gives_toxic_count_instruction(self):
        side = constants.USER
        self.state.user.active.status = constants.TOXIC
        self.state.user.side_conditions[constants.TOXIC_COUNT] = 0
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            side,
            int(self.state.user.active.maxhp / 16)
        )

        toxic_count_instruction = (
            constants.MUTATOR_SIDE_START,
            side,
            constants.TOXIC_COUNT,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction, toxic_count_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_toxic_does_one_eighth_damage_when_toxic_count_is_one_and_gives_toxic_count_instruction(self):
        side = constants.USER
        self.state.user.active.status = constants.TOXIC
        self.state.user.side_conditions[constants.TOXIC_COUNT] = 1
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            side,
            int(self.state.user.active.maxhp / 8)
        )

        toxic_count_instruction = (
            constants.MUTATOR_SIDE_START,
            side,
            constants.TOXIC_COUNT,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction, toxic_count_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_toxic_does_one_quarter_damage_when_toxic_count_is_3_and_gives_toxic_count_instruction(self):
        side = constants.USER
        self.state.user.active.status = constants.TOXIC
        self.state.user.side_conditions[constants.TOXIC_COUNT] = 3
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            side,
            int(self.state.user.active.maxhp / 4)
        )

        toxic_count_instruction = (
            constants.MUTATOR_SIDE_START,
            side,
            constants.TOXIC_COUNT,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction, toxic_count_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_poison_only_does_one_damage_if_that_is_all_it_has(self):
        side = constants.USER
        self.state.user.active.status = constants.POISON
        self.state.user.active.hp = 1
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        instruction = (
            constants.MUTATOR_DAMAGE,
            side,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_leech_seed_saps_health(self):
        self.state.user.active.volatile_status.add(constants.LEECH_SEED)
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 100
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 50
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            12
        )
        heal_instruction = (
            constants.MUTATOR_HEAL,
            constants.OPPONENT,
            12
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction, heal_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_leech_seed_only_saps_1_when_pokemon_has_1_hp(self):
        self.state.user.active.volatile_status.add(constants.LEECH_SEED)
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 1
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 50
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            1
        )
        heal_instruction = (
            constants.MUTATOR_HEAL,
            constants.OPPONENT,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction, heal_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_leech_seed_does_not_overheal(self):
        self.state.user.active.volatile_status.add(constants.LEECH_SEED)
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 100
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 99
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            12
        )
        heal_instruction = (
            constants.MUTATOR_HEAL,
            constants.OPPONENT,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction, heal_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_dying_from_poison_causes_leechseed_not_to_sap(self):
        self.state.user.active.status = constants.POISON
        self.state.opponent.active.volatile_status.add(constants.LEECH_SEED)
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 1
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 99
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_leftovers_causes_heal(self):
        self.state.user.active.item = 'leftovers'
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 1
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.MUTATOR_HEAL,
            constants.USER,
            6
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_blacksludge_causes_heal(self):
        self.state.user.active.item = 'leftovers'
        self.state.user.active.types = ['poison']
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 1
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.MUTATOR_HEAL,
            constants.USER,
            6
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_leftovers_does_not_overheal(self):
        self.state.user.active.item = 'leftovers'
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 99
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.MUTATOR_HEAL,
            constants.USER,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_blacksludge_does_not_overkill(self):
        self.state.user.active.item = 'blacksludge'
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 1
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_blacksludge_does_damage(self):
        self.state.user.active.item = 'blacksludge'
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 100
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            6
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_poisonheal_heals(self):
        self.state.user.active.item = 'toxicorb'
        self.state.user.active.ability = 'poisonheal'
        self.state.user.active.status = constants.POISON
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 50
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.HEAL,
            constants.USER,
            12
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_poison_damage_and_leftovers_heal_together(self):
        self.state.user.active.item = 'leftovers'
        self.state.user.active.status = constants.POISON
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 50
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.DAMAGE,
            constants.USER,
            12
        )
        heal_instruction = (
            constants.HEAL,
            constants.USER,
            6
        )

        expected_instructions = [
            TransposeInstruction(1.0, [heal_instruction, damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_poison_damage_and_leftovers_heal_together_when_poison_kills(self):
        self.state.user.active.item = 'leftovers'
        self.state.user.active.status = constants.POISON
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 5
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.DAMAGE,
            constants.USER,
            11
        )
        heal_instruction = (
            constants.HEAL,
            constants.USER,
            6
        )

        expected_instructions = [
            TransposeInstruction(1.0, [heal_instruction, damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_poison_killing_into_leechseed(self):
        self.state.user.active.volatile_status.add(constants.LEECH_SEED)
        self.state.user.active.status = constants.POISON
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 5
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            5
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_burn_killing_into_leechseed(self):
        self.state.user.active.volatile_status.add(constants.LEECH_SEED)
        self.state.user.active.status = constants.BURN
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 1
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            1
        )

        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_toxic_status_with_leftovers_when_toxic_kills(self):
        self.state.user.active.status = constants.TOXIC
        self.state.user.side_conditions[constants.TOXIC_COUNT] = 2
        self.state.user.active.item = 'leftovers'
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 6
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        heal_instruction = (
            constants.MUTATOR_HEAL,
            constants.USER,
            6
        )

        additional_toxic_count_instruction = (
            constants.MUTATOR_SIDE_START,
            constants.USER,
            constants.TOXIC_COUNT,
            1
        )

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            12
        )

        expected_instructions = [
            TransposeInstruction(1.0, [heal_instruction, damage_instruction, additional_toxic_count_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_faster_pokemon_dying_from_poison_into_leech_seed_from_other_side(self):
        self.state.user.active.status = constants.POISON
        self.state.opponent.active.volatile_status.add(constants.LEECH_SEED)
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 6
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            6
        )

        # pokemon should be dead, so no leechseed should happen
        expected_instructions = [
            TransposeInstruction(1.0, [damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_previous_instructions_are_interpreted_correctly(self):
        self.state.user.active.status = constants.POISON
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 30
        mutator = StateMutator(self.state)

        previous_instruction = (constants.MUTATOR_DAMAGE, constants.USER, 25)
        self.previous_instruction = TransposeInstruction(1.0, [previous_instruction], False)

        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            5
        )

        # pokemon should be dead, so no leechseed should happen
        expected_instructions = [
            TransposeInstruction(1.0, [previous_instruction, damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_sand_damages_pokemon(self):
        self.state.weather = constants.SAND
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 30
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 30
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        self_damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            6
        )
        opponent_damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.OPPONENT,
            6
        )

        expected_instructions = [
            TransposeInstruction(1.0, [self_damage_instruction, opponent_damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_ice_damages_pokemon(self):
        self.state.weather = constants.HAIL
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 30
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 30
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        self_damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            6
        )
        opponent_damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.OPPONENT,
            6
        )

        expected_instructions = [
            TransposeInstruction(1.0, [self_damage_instruction, opponent_damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_sand_does_not_damage_steel_type(self):
        self.state.weather = constants.SAND
        self.state.user.active.types = ['steel']
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 30
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 30
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        opponent_damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.OPPONENT,
            6
        )

        expected_instructions = [
            TransposeInstruction(1.0, [opponent_damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_hail_does_not_damage_ice_type(self):
        self.state.weather = constants.HAIL
        self.state.user.active.types = ['ice']
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 30
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 30
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        opponent_damage_instruction = (
            constants.MUTATOR_DAMAGE,
            constants.OPPONENT,
            6
        )

        expected_instructions = [
            TransposeInstruction(1.0, [opponent_damage_instruction], False),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_double_leftovers_and_poison_and_weather_and_leechseed_executes_in_correct_order(self):
        self.state.weather = constants.HAIL
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 30
        self.state.user.active.status = constants.POISON
        self.state.user.active.item = 'leftovers'
        self.state.user.active.volatile_status.add(constants.LEECH_SEED)
        self.state.user.active.types = ['normal']

        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 30
        self.state.opponent.active.status = constants.POISON
        self.state.opponent.active.item = 'leftovers'
        self.state.opponent.active.volatile_status.add(constants.LEECH_SEED)
        self.state.opponent.active.types = ['normal']
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        self_leftovers = (
            constants.MUTATOR_HEAL,
            constants.USER,
            6
        )
        opponent_leftovers = (
            constants.MUTATOR_HEAL,
            constants.OPPONENT,
            6
        )
        self_poison = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            12
        )
        opponent_poison = (
            constants.MUTATOR_DAMAGE,
            constants.OPPONENT,
            12
        )
        self_hail = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            6
        )
        opponent_hail = (
            constants.MUTATOR_DAMAGE,
            constants.OPPONENT,
            6
        )
        self_leech_damage = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            12
        )
        opponent_leech_heal = (
            constants.MUTATOR_HEAL,
            constants.OPPONENT,
            12
        )
        opponent_leech_damage = (
            constants.MUTATOR_DAMAGE,
            constants.OPPONENT,
            12
        )
        self_leech_heal = (
            constants.MUTATOR_HEAL,
            constants.USER,
            12
        )

        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    self_hail,
                    opponent_hail,
                    self_leftovers,
                    opponent_leftovers,
                    self_poison,
                    opponent_poison,
                    self_leech_damage,
                    opponent_leech_heal,
                    opponent_leech_damage,
                    self_leech_heal
                ],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_instructions_stop_when_weather_kills(self):
        self.state.weather = constants.HAIL
        self.state.user.active.maxhp = 100
        self.state.user.active.hp = 10
        self.state.user.active.status = constants.POISON
        self.state.user.active.item = 'leftovers'
        self.state.user.active.volatile_status.add(constants.LEECH_SEED)
        self.state.user.active.types = ['normal']

        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 30
        self.state.opponent.active.status = constants.POISON
        self.state.opponent.active.item = 'leftovers'
        self.state.opponent.active.volatile_status.add(constants.LEECH_SEED)
        self.state.opponent.active.types = ['normal']
        mutator = StateMutator(self.state)
        instructions = instruction_generator.get_end_of_turn_instructions(mutator, self.previous_instruction, self.dummy_move, self.dummy_move, True)

        self_leftovers = (
            constants.MUTATOR_HEAL,
            constants.USER,
            6
        )
        opponent_leftovers = (
            constants.MUTATOR_HEAL,
            constants.OPPONENT,
            6
        )
        self_poison = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            10  # kills self's pokemon so it is only 10
        )
        opponent_poison = (
            constants.MUTATOR_DAMAGE,
            constants.OPPONENT,
            12
        )
        self_hail = (
            constants.MUTATOR_DAMAGE,
            constants.USER,
            6
        )
        opponent_hail = (
            constants.MUTATOR_DAMAGE,
            constants.OPPONENT,
            6
        )

        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    self_hail,
                    opponent_hail,
                    self_leftovers,
                    opponent_leftovers,
                    self_poison,
                    opponent_poison,
                ],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)


if __name__ == '__main__':
    unittest.main()
