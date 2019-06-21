import unittest
import config
import constants
from collections import defaultdict
from showdown.search.transpose_instruction import TransposeInstruction
from showdown.search.find_state_instructions import get_all_state_instructions
from showdown.search.find_state_instructions import lookup_move
from showdown.search.find_state_instructions import user_moves_first
from showdown.search.objects import State
from showdown.search.objects import Pokemon
from showdown.search.objects import Side
from showdown.state.pokemon import Pokemon as StatePokemon
from showdown.search.state_mutator import StateMutator


class TestGetStateInstructions(unittest.TestCase):
    def setUp(self):
        config.damage_calc_type = "average"  # some tests may override this
        self.state = State(
                        Side(
                            Pokemon.from_state_pokemon_dict(StatePokemon("raichu", 73).to_dict()),
                            {
                                "xatu": Pokemon.from_state_pokemon_dict(StatePokemon("xatu", 81).to_dict()),
                                "starmie": Pokemon.from_state_pokemon_dict(StatePokemon("starmie", 81).to_dict()),
                                "gyarados": Pokemon.from_state_pokemon_dict(StatePokemon("gyarados", 81).to_dict()),
                                "dragonite": Pokemon.from_state_pokemon_dict(StatePokemon("dragonite", 81).to_dict()),
                                "hitmonlee": Pokemon.from_state_pokemon_dict(StatePokemon("hitmonlee", 81).to_dict()),
                            },
                            defaultdict(lambda: 0),
                            False
                        ),
                        Side(
                            Pokemon.from_state_pokemon_dict(StatePokemon("aromatisse", 81).to_dict()),
                            {
                                "yveltal": Pokemon.from_state_pokemon_dict(StatePokemon("yveltal", 73).to_dict()),
                                "slurpuff": Pokemon.from_state_pokemon_dict(StatePokemon("slurpuff", 73).to_dict()),
                                "victini": Pokemon.from_state_pokemon_dict(StatePokemon("victini", 73).to_dict()),
                                "toxapex": Pokemon.from_state_pokemon_dict(StatePokemon("toxapex", 73).to_dict()),
                                "bronzong": Pokemon.from_state_pokemon_dict(StatePokemon("bronzong", 73).to_dict()),
                            },
                            defaultdict(lambda: 0),
                            False
                        ),
                        None,
                        None,
                        False,
                        False,
                        False
                    )

        self.mutator = StateMutator(self.state)

    def test_two_pokemon_switching(self):
        bot_move = "switch xatu"
        opponent_move = "switch yveltal"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('switch', 'self', 'raichu', 'xatu'),
                    ('switch', 'opponent', 'aromatisse', 'yveltal')
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_powder_move_into_tackle_produces_correct_states(self):
        bot_move = "sleeppowder"
        opponent_move = "tackle"
        self.state.opponent.active.types = ['grass']
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_DAMAGE, constants.SELF, 35)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_superpower_correctly_unboosts_opponent(self):
        bot_move = "splash"
        opponent_move = "superpower"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_DAMAGE, constants.SELF, 101),
                    (constants.MUTATOR_BOOST, constants.OPPONENT, constants.ATTACK, -1),
                    (constants.MUTATOR_BOOST, constants.OPPONENT, constants.DEFENSE, -1),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_psyshock_damage_is_the_same_regardless_of_spdef_boost(self):
        bot_move = "psyshock"
        opponent_move = "splash"
        self.state.opponent.active.special_defense_boost = 0
        instructions_without_spdef_boost = get_all_state_instructions(self.mutator, bot_move, opponent_move)

        self.state.opponent.active.special_defense_boost = 6
        instructions_when_spdef_is_maxed = get_all_state_instructions(self.mutator, bot_move, opponent_move)

        self.assertEqual(instructions_without_spdef_boost, instructions_when_spdef_is_maxed)

    def test_powder_into_powder_gives_correct_states(self):
        bot_move = "sleeppowder"
        opponent_move = "sleeppowder"
        self.state.opponent.active.types = ['grass']
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                0.75,
                [
                    (constants.MUTATOR_APPLY_STATUS, constants.SELF, constants.SLEEP)
                ],
                False
            ),
            TransposeInstruction(
                0.25,
                [],
                True
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_focuspunch_into_non_damaging_move_gives_correct_states(self):
        bot_move = "focuspunch"
        opponent_move = "splash"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 46)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_focuspunch_into_damaging_move_gives_correct_states(self):
        bot_move = "focuspunch"
        opponent_move = "tackle"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    (constants.MUTATOR_DAMAGE, constants.SELF, 35)
                ],
                True
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_whirlwind_removes_status_boosts(self):
        bot_move = "whirlwind"
        opponent_move = "splash"
        self.state.opponent.active.attack_boost = 3
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    (constants.MUTATOR_UNBOOST, constants.OPPONENT, constants.ATTACK, 3)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_haze_removes_status_boosts(self):
        bot_move = "haze"
        opponent_move = "splash"
        self.state.opponent.active.attack_boost = 3
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    (constants.MUTATOR_UNBOOST, constants.OPPONENT, constants.ATTACK, 3)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_clearsmog_removes_status_boosts(self):
        bot_move = "clearsmog"
        opponent_move = "splash"
        self.state.opponent.active.attack_boost = 3
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 55),
                    (constants.MUTATOR_UNBOOST, constants.OPPONENT, constants.ATTACK, 3)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_seismic_toss_deals_damage_by_level(self):
        bot_move = "seismictoss"
        opponent_move = "splash"
        self.state.self.active.level = 99
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 99),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_ghost_immune_to_seismic_toss(self):
        bot_move = "seismictoss"
        opponent_move = "splash"
        self.state.self.active.level = 99
        self.state.opponent.active.types = ["ghost"]
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_normal_immune_to_night_shade(self):
        bot_move = "nightshade"
        opponent_move = "splash"
        self.state.self.active.level = 99
        self.state.opponent.active.types = ["normal"]
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_superfang_does_half_health(self):
        bot_move = "superfang"
        opponent_move = "splash"
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 80
        self.state.opponent.active.types = ["normal"]
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                0.9,
                [
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 40)
                ],
                False
            ),
            TransposeInstruction(
                0.09999999999999998,
                [],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_finalgambit_does_damage_equal_to_health_and_faints_user(self):
        bot_move = "finalgambit"
        opponent_move = "splash"
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 100
        self.state.self.active.maxhp = 100
        self.state.self.active.hp = 80
        self.state.opponent.active.types = ["normal"]
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 80),
                    (constants.MUTATOR_HEAL, constants.SELF, -80),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_endeavor_brings_hp_to_equal(self):
        bot_move = "endeavor"
        opponent_move = "splash"
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 100
        self.state.self.active.maxhp = 100
        self.state.self.active.hp = 80
        self.state.opponent.active.types = ["normal"]
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 20)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_endeavor_does_nothing_when_user_hp_greater_than_target_hp(self):
        bot_move = "endeavor"
        opponent_move = "splash"
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 60
        self.state.self.active.maxhp = 100
        self.state.self.active.hp = 80
        self.state.opponent.active.types = ["normal"]
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_knockoff_does_more_damage_when_item_can_be_removed(self):
        bot_move = "knockoff"
        opponent_move = "splash"
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 100
        self.state.self.active.maxhp = 100
        self.state.self.active.hp = 100
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    # this move does 20 damage without knockoff boost
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 30)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_knockoff_does_not_amplify_damage_for_mega(self):
        bot_move = "knockoff"
        opponent_move = "splash"
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 100
        self.state.self.active.maxhp = 100
        self.state.self.active.hp = 100
        self.state.opponent.active.id = "blastoisemega"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    # this move does 20 damage without knockoff boost
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 20)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_knockoff_does_not_amplify_damage_for_primal(self):
        bot_move = "knockoff"
        opponent_move = "splash"
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 100
        self.state.self.active.maxhp = 100
        self.state.self.active.hp = 100
        self.state.opponent.active.id = "groudonprimal"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    # this move does 20 damage without knockoff boost
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 20)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_rest_heals_user_and_puts_to_sleep(self):
        bot_move = "rest"
        opponent_move = "splash"
        self.state.self.active.maxhp = 100
        self.state.self.active.hp = 50
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_APPLY_STATUS, constants.SELF, constants.SLEEP),
                    (constants.MUTATOR_HEAL, constants.SELF, 50),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_ghost_immune_to_superfang(self):
        bot_move = "superfang"
        opponent_move = "splash"
        self.state.opponent.active.maxhp = 100
        self.state.opponent.active.hp = 100
        self.state.opponent.active.types = ["ghost"]
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_fast_uturn_results_in_switching_out_move_for_enemy(self):
        bot_move = "splash"
        opponent_move = "uturn"
        self.state.self.active.speed = 1
        self.state.opponent.active.speed = 2
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                        (constants.MUTATOR_DAMAGE, constants.SELF, 60),
                        (constants.MUTATOR_SWITCH, constants.OPPONENT, 'aromatisse', 'slurpuff')
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_fast_uturn_results_in_switching_out_for_bot(self):
        bot_move = "uturn"
        opponent_move = "tackle"
        self.state.self.active.speed = 2
        self.state.opponent.active.speed = 1
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                        (constants.MUTATOR_DAMAGE, constants.OPPONENT, 22),
                        (constants.MUTATOR_SWITCH, constants.SELF, 'raichu', 'gyarados'),
                        (constants.MUTATOR_DAMAGE, constants.SELF, 24)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_slow_uturn_results_in_switching_out_for_bot(self):
        bot_move = "uturn"
        opponent_move = "tackle"
        self.state.self.active.speed = 1
        self.state.opponent.active.speed = 2
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                        (constants.MUTATOR_DAMAGE, constants.SELF, 35),
                        (constants.MUTATOR_DAMAGE, constants.OPPONENT, 22),
                        (constants.MUTATOR_SWITCH, constants.SELF, 'raichu', 'gyarados')
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_slow_uturn_results_in_switching_out_for_opponent(self):
        bot_move = "tackle"
        opponent_move = "uturn"
        self.state.self.active.speed = 2
        self.state.opponent.active.speed = 1
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                        (constants.MUTATOR_DAMAGE, constants.OPPONENT, 25),
                        (constants.MUTATOR_DAMAGE, constants.SELF, 60),
                        (constants.MUTATOR_SWITCH, constants.OPPONENT, 'aromatisse', 'slurpuff')
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_uturn_works_with_multiple_states_before(self):
        bot_move = "thunderbolt"
        opponent_move = "uturn"
        self.state.self.active.speed = 2
        self.state.opponent.active.speed = 1
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                0.07500000000000001,
                [
                    ('damage', 'opponent', 72),
                    ('apply_status', 'opponent', 'par'),
                    ('damage', 'self', 60),
                    ('switch', 'opponent', 'aromatisse', 'slurpuff')
                ],
                False
            ),
            TransposeInstruction(
                0.025,
                [
                    ('damage', 'opponent', 72),
                    ('apply_status', 'opponent', 'par'),
                ],
                True
            ),
            TransposeInstruction(
                0.9,
                [
                    ('damage', 'opponent', 72),
                    ('damage', 'self', 60),
                    ('switch', 'opponent', 'aromatisse', 'slurpuff')
                ],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_fast_voltswitch_results_in_switching_out_for_opponent(self):
        self.state.self.active.ability = None  # raichu has lightningrod lol
        bot_move = "tackle"
        opponent_move = "voltswitch"
        self.state.self.active.speed = 1
        self.state.opponent.active.speed = 2
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                        (constants.MUTATOR_DAMAGE, constants.SELF, 29),
                        (constants.MUTATOR_SWITCH, constants.OPPONENT, 'aromatisse', 'bronzong'),
                        (constants.MUTATOR_DAMAGE, constants.OPPONENT, 10),

                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_immune_by_ability_does_not_allow_voltswitch(self):
        bot_move = "tackle"
        opponent_move = "voltswitch"
        self.state.self.active.speed = 1
        self.state.opponent.active.speed = 2
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    (constants.MUTATOR_BOOST, constants.SELF, constants.SPECIAL_ATTACK, 1),
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 25),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_ground_type_does_not_allow_voltswitch(self):
        self.state.self.active.ability = None  # raichu has lightningrod lol
        self.state.self.active.types = ['ground']
        bot_move = "tackle"
        opponent_move = "voltswitch"
        self.state.self.active.speed = 1
        self.state.opponent.active.speed = 2
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 25),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_bellydrum_works_properly_in_basic_case(self):
        bot_move = "bellydrum"
        opponent_move = "splash"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    (constants.MUTATOR_BOOST, constants.SELF, constants.ATTACK, 6),
                    (constants.MUTATOR_HEAL, constants.SELF, -1 * self.state.self.active.maxhp / 2)

                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_bellydrum_kills_user_when_hp_is_less_than_half(self):
        bot_move = "bellydrum"
        opponent_move = "splash"
        self.state.self.active.hp = 1
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    (constants.MUTATOR_BOOST, constants.SELF, constants.ATTACK, 6),
                    (constants.MUTATOR_HEAL, constants.SELF, -1)

                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_gryo_ball_does_damage(self):
        bot_move = "gyroball"
        opponent_move = "splash"
        self.state.self.active.speed = 1
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 186),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_whirlwind_behaves_correctly_with_a_regular_move(self):
        bot_move = "whirlwind"
        opponent_move = "flamethrower"
        self.state.opponent.active.attack_boost = 3
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                0.1,
                [
                    (constants.MUTATOR_DAMAGE, constants.SELF, 74),
                    (constants.MUTATOR_APPLY_STATUS, constants.SELF, constants.BURN),
                    (constants.MUTATOR_DAMAGE, constants.SELF, 13),
                    (constants.MUTATOR_UNBOOST, constants.OPPONENT, constants.ATTACK, 3),
                ],
                False
            ),
            TransposeInstruction(
                0.9,
                [
                    (constants.MUTATOR_DAMAGE, constants.SELF, 74),
                    (constants.MUTATOR_UNBOOST, constants.OPPONENT, constants.ATTACK, 3)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_pokemon_with_active_substitute_switching_into_phazing_move(self):
        bot_move = "switch starmie"
        opponent_move = "roar"
        self.state.self.active.volatile_status = {'substitute'}
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    (constants.MUTATOR_REMOVE_VOLATILE_STATUS, constants.SELF, constants.SUBSTITUTE),
                    (constants.MUTATOR_SWITCH, constants.SELF, 'raichu', 'starmie')
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_pokemon_with_active_substitute_switching_into_phazing_move_that_gets_reflected(self):
        bot_move = "switch starmie"
        opponent_move = "roar"
        self.state.self.active.volatile_status = {'substitute'}
        self.state.self.reserve['starmie'].ability = 'magicbounce'
        self.state.opponent.active.attack_boost = 5
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    (constants.MUTATOR_REMOVE_VOLATILE_STATUS, constants.SELF, constants.SUBSTITUTE),
                    (constants.MUTATOR_SWITCH, constants.SELF, 'raichu', 'starmie'),
                    (constants.MUTATOR_UNBOOST, constants.OPPONENT, constants.ATTACK, 5)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_dragontail_behaves_well_with_regular_move(self):
        bot_move = "dragontail"
        opponent_move = "tackle"
        self.state.opponent.active.types = ['normal']
        self.state.opponent.active.attack_boost = 3
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                0.9,
                [
                    (constants.MUTATOR_DAMAGE, constants.SELF, 127),
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 37),
                    (constants.MUTATOR_UNBOOST, constants.OPPONENT, constants.ATTACK, 3)
                ],
                False
            ),
            TransposeInstruction(
                0.09999999999999998,
                [
                    (constants.MUTATOR_DAMAGE, constants.SELF, 127)
                ],
                True
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_whirlwind_removes_volatile_statuses(self):
        bot_move = "whirlwind"
        opponent_move = "splash"
        self.state.opponent.active.volatile_status.add('confusion')
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    (constants.MUTATOR_REMOVE_VOLATILE_STATUS, constants.OPPONENT, constants.CONFUSION)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_suckerpunch_into_tackle_makes_suckerpunch_hit(self):
        bot_move = "suckerpunch"
        opponent_move = "tackle"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('damage', 'opponent', 22),
                    ('damage', 'self', 35),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_substitute_into_weak_attack_does_not_remove_volatile_status(self):
        self.state.self.active.speed = 100
        self.state.opponent.active.speed = 99
        bot_move = "substitute"
        opponent_move = "tackle"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_APPLY_VOLATILE_STATUS, constants.SELF, constants.SUBSTITUTE),
                    (constants.MUTATOR_DAMAGE, constants.SELF, self.state.self.active.maxhp * 0.25),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_substitute_into_string_attack_removes_volatile_status(self):
        self.state.self.active.speed = 100
        self.state.opponent.active.speed = 99
        bot_move = "substitute"
        opponent_move = "earthquake"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_APPLY_VOLATILE_STATUS, constants.SELF, constants.SUBSTITUTE),
                    (constants.MUTATOR_DAMAGE, constants.SELF, self.state.self.active.maxhp * 0.25),
                    (constants.MUTATOR_REMOVE_VOLATILE_STATUS, constants.SELF, constants.SUBSTITUTE),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_substitute_fails_if_user_has_less_than_one_quarter_maxhp(self):
        self.state.self.active.speed = 100
        self.state.opponent.active.speed = 99
        self.state.self.active.hp = 0.2 * self.state.self.active.maxhp
        bot_move = "substitute"
        opponent_move = "earthquake"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_DAMAGE, constants.SELF, 41.6),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_highjumpkick_causes_crash(self):
        self.state.self.active.speed = 100
        self.state.opponent.active.speed = 99
        bot_move = "highjumpkick"
        opponent_move = "splash"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                0.9,
                [
                    ('damage', 'opponent', 40),
                ],
                False
            ),
            TransposeInstruction(
                0.09999999999999998,
                [
                    ('damage', 'self', 104),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_suckerpunch_into_swordsdance_makes_suckerpunch_miss(self):
        bot_move = "suckerpunch"
        opponent_move = "swordsdance"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_BOOST, constants.OPPONENT, constants.ATTACK, 2)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_rockhead_removes_recoil_for_one_but_not_the_other(self):
        bot_move = "doubleedge"
        opponent_move = "doubleedge"
        self.state.self.active.ability = 'rockhead'
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 74),
                    (constants.MUTATOR_DAMAGE, constants.SELF, 101),
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 33),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_tackle_into_ironbarbs_causes_recoil(self):
        bot_move = "splash"
        opponent_move = "tackle"
        self.state.self.active.ability = 'ironbarbs'
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_DAMAGE, constants.SELF, 35),
                    (constants.MUTATOR_HEAL, constants.OPPONENT, -37),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_tackle_into_roughskin_causes_recoil(self):
        bot_move = "splash"
        opponent_move = "tackle"
        self.state.self.active.ability = 'roughskin'
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_DAMAGE, constants.SELF, 35),
                    (constants.MUTATOR_HEAL, constants.OPPONENT, -18.5),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_regular_damaging_move_with_speed_boost(self):
        bot_move = "tackle"
        opponent_move = "splash"
        self.state.self.active.ability = 'speedboost'
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 25),
                    (constants.MUTATOR_BOOST, constants.SELF, constants.SPEED, 1)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_fire_type_cannot_be_burned(self):
        bot_move = "willowisp"
        opponent_move = "splash"
        self.state.opponent.active.types = ['fire']
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_fire_type_cannot_be_burned_from_secondary(self):
        bot_move = "flamethrower"
        opponent_move = "splash"
        self.state.opponent.active.types = ['fire']
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 24)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_analytic_boosts_damage(self):
        bot_move = "tackle"
        opponent_move = "splash"
        self.state.self.active.ability = 'analytic'
        self.state.self.active.speed = 1
        self.state.opponent.active.speed = 2
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 33)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_poisoning_move_shows_poison_damage_on_opponents_turn(self):
        bot_move = "poisonjab"
        opponent_move = "tackle"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                0.3,
                [
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 99),
                    (constants.MUTATOR_APPLY_STATUS, constants.OPPONENT, constants.POISON),
                    (constants.MUTATOR_DAMAGE, constants.SELF, 35),
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, self.state.opponent.active.maxhp * 0.125)
                ],
                False
            ),
            TransposeInstruction(
                0.7,
                [
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 99),
                    (constants.MUTATOR_DAMAGE, constants.SELF, 35),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_avalanche_into_switch_does_not_increase_avalanche_damage(self):
        bot_move = "avalanche"
        opponent_move = "switch yveltal"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    (constants.MUTATOR_SWITCH, constants.OPPONENT, 'aromatisse', 'yveltal'),
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 68)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_using_toxic_results_in_first_damage_to_be_one_sixteenth(self):
        bot_move = "toxic"
        opponent_move = "splash"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                0.9,
                [
                    (constants.MUTATOR_APPLY_STATUS, constants.OPPONENT, constants.TOXIC),
                    (constants.MUTATOR_SIDE_START, constants.OPPONENT, constants.TOXIC_COUNT, 1),
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, int(self.state.opponent.active.maxhp / 16)),
                ],
                False
            ),
            TransposeInstruction(
                0.09999999999999998,
                [],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_previously_existing_toxic_results_in_correct_damage(self):
        bot_move = "splash"
        opponent_move = "splash"
        self.state.opponent.active.status = constants.TOXIC
        self.state.opponent.side_conditions[constants.TOXIC_COUNT] = 1
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_SIDE_START, constants.OPPONENT, constants.TOXIC_COUNT, 1),
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, int(self.state.opponent.active.maxhp / 8)),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_toxic_cannot_drop_below_0_hp(self):
        bot_move = "splash"
        opponent_move = "splash"
        self.state.opponent.active.status = constants.TOXIC
        self.state.opponent.active.hp = 1
        self.state.opponent.side_conditions[constants.TOXIC_COUNT] = 1
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_SIDE_START, constants.OPPONENT, constants.TOXIC_COUNT, 1),
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 1),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_stealthrock_produces_correct_instruction(self):
        bot_move = "stealthrock"
        opponent_move = "splash"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_SIDE_START, constants.OPPONENT, constants.STEALTH_ROCK, 1)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_desolate_land_makes_water_moves_fail(self):
        bot_move = "surf"
        opponent_move = "splash"
        self.state.weather = constants.DESOLATE_LAND
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_stealthrock_produces_no_instructions_when_it_exists(self):
        bot_move = "stealthrock"
        opponent_move = "splash"
        self.state.opponent.side_conditions[constants.STEALTH_ROCK] = 1
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_spikes_goes_to_3_layers(self):
        bot_move = "spikes"
        opponent_move = "splash"
        self.state.opponent.side_conditions[constants.SPIKES] = 2
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_SIDE_START, constants.OPPONENT, constants.SPIKES, 1)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_reflect_halves_damage_when_used(self):
        bot_move = "reflect"  # bot is faster
        opponent_move = "tackle"
        self.state.opponent.side_conditions[constants.SPIKES] = 2
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_SIDE_START, constants.SELF, constants.REFLECT, 1),
                    (constants.MUTATOR_DAMAGE, constants.SELF, 17),  # non-reflect does 35
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_toxicspikes_plus_damage(self):
        bot_move = "switch starmie"
        opponent_move = "tackle"
        self.state.self.side_conditions[constants.TOXIC_SPIKES] = 1
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_SWITCH, constants.SELF, "raichu", "starmie"),
                    (constants.MUTATOR_APPLY_STATUS, constants.SELF, constants.POISON),
                    (constants.MUTATOR_DAMAGE, constants.SELF, 24),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_toxicspikes_plus_setting_rocks_from_opponent(self):
        bot_move = "switch starmie"
        opponent_move = "stealthrock"
        self.state.self.side_conditions[constants.TOXIC_SPIKES] = 2
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_SWITCH, constants.SELF, "raichu", "starmie"),
                    (constants.MUTATOR_APPLY_STATUS, constants.SELF, constants.TOXIC),
                    (constants.MUTATOR_SIDE_START, constants.SELF, constants.STEALTH_ROCK, 1),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_spikes_into_rapid_spin_clears_the_spikes(self):
        bot_move = "spikes"
        opponent_move = "rapidspin"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_SIDE_START, constants.OPPONENT, constants.SPIKES, 1),
                    (constants.MUTATOR_DAMAGE, constants.SELF, 18),
                    (constants.MUTATOR_SIDE_END, constants.OPPONENT, constants.SPIKES, 1),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_spikes_into_rapid_spin_does_not_clear_spikes_when_user_is_ghost_type(self):
        bot_move = "spikes"
        opponent_move = "rapidspin"

        self.state.self.active.types = ['ghost']

        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_SIDE_START, constants.OPPONENT, constants.SPIKES, 1),
                ],
                True
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_defog_works_even_if_defender_is_ghost(self):
        bot_move = "spikes"
        opponent_move = "defog"

        self.state.self.active.types = ['ghost']

        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_SIDE_START, constants.OPPONENT, constants.SPIKES, 1),
                    (constants.MUTATOR_SIDE_END, constants.OPPONENT, constants.SPIKES, 1),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_stealthrock_into_switch(self):
        bot_move = "stealthrock"
        opponent_move = "switch yveltal"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_SWITCH, constants.OPPONENT, 'aromatisse', 'yveltal'),
                    (constants.MUTATOR_SIDE_START, constants.OPPONENT, constants.STEALTH_ROCK, 1)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_fainting_pokemon_does_not_move(self):
        self.state.opponent.active.hp = 1

        bot_move = "tackle"
        opponent_move = "tackle"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('damage', 'opponent', 1),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_negative_boost_inflictions(self):
        bot_move = "crunch"
        opponent_move = "moonblast"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                0.06,
                [
                    ('damage', 'opponent', 24),
                    ('boost', 'opponent', 'defense', -1),
                    ('damage', 'self', 119),
                    ('boost', 'self', 'special-attack', -1)
                ],
                False
            ),
            TransposeInstruction(
                0.13999999999999999,
                [
                    ('damage', 'opponent', 24),
                    ('boost', 'opponent', 'defense', -1),
                    ('damage', 'self', 119),
                ],
                False
            ),
            TransposeInstruction(
                0.24,
                [
                    ('damage', 'opponent', 24),
                    ('damage', 'self', 119),
                    ('boost', 'self', 'special-attack', -1)
                ],
                False
            ),
            TransposeInstruction(
                0.5599999999999999,
                [
                    ('damage', 'opponent', 24),
                    ('damage', 'self', 119),
                ],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_reflect_halves_physical_damage(self):
        bot_move = "tackle"
        opponent_move = "tackle"
        self.state.self.side_conditions[constants.REFLECT] = 1
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('damage', 'opponent', 25),
                    ('damage', 'self', 17)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_reflect_does_not_halve_special_damage(self):
        bot_move = "tackle"
        opponent_move = "fairywind"
        self.state.self.side_conditions[constants.REFLECT] = 1
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('damage', 'opponent', 25),
                    ('damage', 'self', 51)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_light_screen_halves_special_damage(self):
        bot_move = "tackle"
        opponent_move = "fairywind"
        self.state.self.side_conditions[constants.LIGHT_SCREEN] = 1
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('damage', 'opponent', 25),
                    ('damage', 'self', 25)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_rain_doubles_water_damage(self):
        bot_move = "surf"
        opponent_move = "tackle"
        self.state.weather = constants.RAIN
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('damage', 'opponent', 72),
                    ('damage', 'self', 35)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_sun_doubles_fire_damage(self):
        bot_move = "eruption"
        opponent_move = "tackle"
        self.state.weather = constants.SUN
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('damage', 'opponent', 119),
                    ('damage', 'self', 35)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_sand_properly_increses_special_defense_for_rock(self):
        bot_move = "surf"
        opponent_move = "splash"
        self.state.weather = constants.SAND
        self.state.opponent.active.types = ['rock']
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('damage', 'opponent', 64),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_sand_does_not_increase_special_defense_for_ground(self):
        bot_move = "surf"
        opponent_move = "splash"
        self.state.weather = constants.SAND
        self.state.opponent.active.types = ['ground']
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('damage', 'opponent', 96),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_lifeorb_gives_recoil(self):
        bot_move = "tackle"
        opponent_move = "tackle"
        self.state.self.active.item = 'lifeorb'
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('damage', 'opponent', 33),
                    ('heal', 'self', -20.8),
                    ('damage', 'self', 35)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_choice_band_boosts_damage(self):
        bot_move = "tackle"
        opponent_move = "tackle"
        self.state.self.active.item = 'choiceband'
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('damage', 'opponent', 37),
                    ('damage', 'self', 35)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_eviolite_reduces_damage(self):
        bot_move = "tackle"
        opponent_move = "tackle"
        self.state.self.active.item = 'eviolite'
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('damage', 'opponent', 25),
                    ('damage', 'self', 18)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_rocky_helmet_hurts_attacker(self):
        bot_move = "tackle"
        opponent_move = "tackle"
        self.state.self.active.item = 'rockyhelmet'
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('damage', 'opponent', 25),
                    ('damage', 'self', 35),
                    ('heal', 'opponent', -49.33333333333333)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_taunt_sets_taunt_status(self):
        bot_move = "taunt"
        opponent_move = "splash"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_APPLY_VOLATILE_STATUS, constants.OPPONENT, constants.TAUNT)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_taunt_volatile_status_prevents_non_damaging_move(self):
        bot_move = "taunt"
        opponent_move = "calmmind"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_APPLY_VOLATILE_STATUS, constants.OPPONENT, constants.TAUNT)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_taunt_volatile_status_does_not_prevent_damaging_move(self):
        bot_move = "taunt"
        opponent_move = "tackle"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_APPLY_VOLATILE_STATUS, constants.OPPONENT, constants.TAUNT),
                    (constants.MUTATOR_DAMAGE, constants.SELF, 35)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_ninetales_starts_sun_weather(self):
        bot_move = "switch ninetales"
        opponent_move = "splash"
        self.state.self.reserve['ninetales'] = Pokemon.from_state_pokemon_dict(StatePokemon("ninetales", 81).to_dict())
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_SWITCH, 'self', self.state.self.active.id, 'ninetales'),
                    (constants.MUTATOR_WEATHER_START, constants.SUN)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_politoed_starts_rain_weather(self):
        bot_move = "switch politoed"
        opponent_move = "splash"
        self.state.self.reserve['politoed'] = Pokemon.from_state_pokemon_dict(StatePokemon("politoed", 81).to_dict())
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_SWITCH, 'self', self.state.self.active.id, 'politoed'),
                    (constants.MUTATOR_WEATHER_START, constants.RAIN)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_politoed_does_not_start_rain_weather_when_desolate_land_is_active(self):
        bot_move = "switch politoed"
        opponent_move = "splash"
        self.state.weather = constants.DESOLATE_LAND
        self.state.self.reserve['politoed'] = Pokemon.from_state_pokemon_dict(StatePokemon("politoed", 81).to_dict())
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_SWITCH, 'self', self.state.self.active.id, 'politoed'),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_politoed_does_not_start_rain_weather_when_rain_is_already_active(self):
        bot_move = "switch politoed"
        opponent_move = "splash"
        self.state.weather = constants.DESOLATE_LAND
        self.state.self.reserve['politoed'] = Pokemon.from_state_pokemon_dict(StatePokemon("politoed", 81).to_dict())
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_SWITCH, 'self', self.state.self.active.id, 'politoed'),
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_intimidate_causes_opponent_attack_to_lower(self):
        bot_move = "switch xatu"
        opponent_move = "splash"
        self.state.self.reserve['xatu'].ability = 'intimidate'
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_SWITCH, 'self', self.state.self.active.id, 'xatu'),
                    (constants.MUTATOR_UNBOOST, constants.OPPONENT, constants.ATTACK, 1)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_dousedrive_makes_waterabsorb_activate(self):
        bot_move = "technoblast"
        opponent_move = "splash"
        self.state.self.active.item = 'dousedrive'
        self.state.opponent.active.ability = 'waterabsorb'
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_airballoon_makes_immune(self):
        bot_move = "tackle"
        opponent_move = "earthquake"
        self.state.self.active.item = 'airballoon'
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('damage', 'opponent', 25)
                ],
                True
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_inflicting_with_leechseed_produces_sap_instruction(self):
        bot_move = "leechseed"
        opponent_move = "splash"
        self.state.opponent.active.maxhp = 100
        self.state.self.active.maxhp = 100
        self.state.self.active.hp = 50
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_APPLY_VOLATILE_STATUS, constants.OPPONENT, constants.LEECH_SEED),
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 12),
                    (constants.MUTATOR_HEAL, constants.SELF, 12)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_skill_link_increases_tailslap_damage(self):
        bot_move = "tailslap"
        opponent_move = "splash"
        self.state.self.active.ability = 'skilllink'
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                0.85,
                [
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 77),
                ],
                False
            ),
            TransposeInstruction(
                0.15000000000000002,
                [],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_pre_existing_leechseed_produces_sap_instruction(self):
        bot_move = "tackle"
        opponent_move = "splash"
        self.state.opponent.active.volatile_status.add("leechseed")
        self.state.opponent.active.maxhp = 100
        self.state.self.active.maxhp = 100
        self.state.self.active.hp = 50
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 25),
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 12),
                    (constants.MUTATOR_HEAL, constants.SELF, 12)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_pre_existing_leechseed_produces_sap_instruction_with_one_health_after_damage(self):
        bot_move = "tackle"
        opponent_move = "splash"
        self.state.opponent.active.volatile_status.add("leechseed")
        self.state.opponent.active.hp = 26
        self.state.opponent.active.maxhp = 100
        self.state.self.active.maxhp = 100
        self.state.self.active.hp = 50
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 25),
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 1),
                    (constants.MUTATOR_HEAL, constants.SELF, 1)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_double_zap_cannon(self):
        bot_move = "zapcannon"
        opponent_move = "zapcannon"

        # raichu's default ability should be lightningrod
        self.state.self.active.ability = None

        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                0.1875,
                [
                    ('damage', 'opponent', 95),
                    ('apply_status', 'opponent', 'par'),
                    ('damage', 'self', 49),
                    ('apply_status', 'self', 'par')
                ],
                False
            ),
            TransposeInstruction(
                0.1875,
                [
                    ('damage', 'opponent', 95),
                    ('apply_status', 'opponent', 'par'),
                ],
                True
            ),
            TransposeInstruction(
                0.125,
                [
                    ('damage', 'opponent', 95),
                    ('apply_status', 'opponent', 'par'),
                ],
                True
            ),
            TransposeInstruction(
                0.25,
                [
                    ('damage', 'self', 49),
                    ('apply_status', 'self', 'par')
                ],
                False
            ),
            TransposeInstruction(
                0.25,
                [],
                True
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_thunder_produces_all_states(self):
        bot_move = "thunder"
        opponent_move = "splash"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                0.1575,
                [
                    ('damage', 'opponent', 88),
                    ('apply_status', 'opponent', 'par'),
                ],
                False
            ),
            TransposeInstruction(
                0.0525,
                [
                    ('damage', 'opponent', 88),
                    ('apply_status', 'opponent', 'par'),
                ],
                True
            ),
            TransposeInstruction(
                0.48999999999999994,
                [
                    ('damage', 'opponent', 88),
                ],
                False
            ),
            TransposeInstruction(
                0.30000000000000004,
                [
                ],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_thunder_produces_all_states_with_damage_rolls_accounted_for(self):
        config.damage_calc_type = "min_max_average"
        bot_move = "thunder"
        opponent_move = "splash"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                0.05249999999999999,
                [
                    ('damage', 'opponent', 88),
                    ('apply_status', 'opponent', 'par'),
                ],
                False
            ),
            TransposeInstruction(
                0.017499999999999998,
                [
                    ('damage', 'opponent', 88),
                    ('apply_status', 'opponent', 'par'),
                ],
                True
            ),
            TransposeInstruction(
                0.1633333333333333,
                [
                    ('damage', 'opponent', 88),
                ],
                False
            ),
            TransposeInstruction(
                0.1,
                [
                ],
                False
            ),
            TransposeInstruction(
                0.05249999999999999,
                [
                    ('damage', 'opponent', 81),
                    ('apply_status', 'opponent', 'par'),
                ],
                False
            ),
            TransposeInstruction(
                0.017499999999999998,
                [
                    ('damage', 'opponent', 81),
                    ('apply_status', 'opponent', 'par'),
                ],
                True
            ),
            TransposeInstruction(
                0.1633333333333333,
                [
                    ('damage', 'opponent', 81),
                ],
                False
            ),
            TransposeInstruction(
                0.1,
                [
                ],
                False
            ),
            TransposeInstruction(
                0.05249999999999999,
                [
                    ('damage', 'opponent', 96),
                    ('apply_status', 'opponent', 'par'),
                ],
                False
            ),
            TransposeInstruction(
                0.017499999999999998,
                [
                    ('damage', 'opponent', 96),
                    ('apply_status', 'opponent', 'par'),
                ],
                True
            ),
            TransposeInstruction(
                0.1633333333333333,
                [
                    ('damage', 'opponent', 96),
                ],
                False
            ),
            TransposeInstruction(
                0.1,
                [
                ],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_flinching_move_versus_secondary_effect_produces_three_states(self):
        bot_move = "ironhead"
        opponent_move = "moonblast"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                0.3,
                [
                    ('damage', 'opponent', 99),
                    ('apply_volatile_status', 'opponent', 'flinch'),
                    ('remove_volatile_status', 'opponent', 'flinch')
                ],
                True
            ),
            TransposeInstruction(
                0.21,
                [
                    ('damage', 'opponent', 99),
                    ('damage', 'self', 119),
                    ('boost', 'self', 'special-attack', -1),
                ],
                False
            ),
            TransposeInstruction(
                0.48999999999999994,
                [
                    ('damage', 'opponent', 99),
                    ('damage', 'self', 119),
                ],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_switch_flying_into_earthquake(self):
        bot_move = "switch xatu"
        opponent_move = "earthquake"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('switch', 'self', 'raichu', 'xatu'),
                ],
                True
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_flinching_as_second_move_does_not_produce_extra_state(self):
        bot_move = "switch xatu"
        opponent_move = "ironhead"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('switch', 'self', 'raichu', 'xatu'),
                    ('damage', 'self', 52),
                ],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_attack_into_healing_produces_one_state(self):
        bot_move = "tackle"
        opponent_move = "recover"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('damage', 'opponent', 25),
                    ('heal', 'opponent', 25),
                ],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_attack_into_healing_with_multiple_attack_damage_rolls(self):
        config.damage_calc_type = "min_max_average"
        bot_move = "tackle"
        opponent_move = "recover"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1 / 3,
                [
                    ('damage', 'opponent', 25),
                    ('heal', 'opponent', 25),
                ],
                False
            ),
            TransposeInstruction(
                1 / 3,
                [
                    ('damage', 'opponent', 28),
                    ('heal', 'opponent', 28),
                ],
                False
            ),
            TransposeInstruction(
                1 / 3,
                [
                    ('damage', 'opponent', 23),
                    ('heal', 'opponent', 23),
                ],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_fainted_pokemon_cannot_heal(self):
        self.state.opponent.active.hp = 1

        bot_move = "tackle"
        opponent_move = "recover"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('damage', 'opponent', 1),
                ],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_switch_into_rocks_does_neutral_damage(self):
        self.state.opponent.side_conditions[constants.STEALTH_ROCK] = 1

        bot_move = "splash"
        opponent_move = "switch toxapex"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    ('switch', 'opponent', 'aromatisse', 'toxapex'),
                    ('damage', 'opponent', 24.125),
                ],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_stealthrock_into_magicbounce_properly_reflects(self):
        self.state.self.active.ability = 'magicbounce'
        bot_move = "splash"
        opponent_move = "stealthrock"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                    (constants.MUTATOR_SIDE_START, constants.OPPONENT, constants.STEALTH_ROCK, 1),
                ],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_magic_bounced_stealthrock_doesnt_exceed_one_level(self):
        self.state.self.active.ability = 'magicbounce'
        bot_move = "splash"
        opponent_move = "stealthrock"
        self.state.opponent.side_conditions[constants.STEALTH_ROCK] = 1
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_double_earthquake_with_double_levitate_does_nothing(self):
        self.state.self.active.ability = 'levitate'
        self.state.opponent.active.ability = 'levitate'

        bot_move = "earthquake"
        opponent_move = "earthquake"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1,
                [
                ],
                True
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_paralyzed_pokemon_produces_two_states_when_trying_to_attack(self):
        self.state.self.active.status = constants.PARALYZED
        bot_move = "tackle"
        opponent_move = "tackle"
        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                0.75,
                [
                    ('damage', 'opponent', 25),
                    ('damage', 'self', 35),

                ],
                False
            ),
            TransposeInstruction(
                0.25,
                [
                    ('damage', 'self', 35)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_fireblast_into_crunch_when_already_burned_produces_four_states(self):
        self.state = State.from_dict(
            {
                'self': {
                    'active': {
                        'canMegaEvo': False,
                        'id': 'ninetales',
                        'level': 83,
                        'hp': 228,
                        'maxhp': 257,
                        'ability': 'drought',
                        'item': '',
                        'baseStats': {
                            'hp': 73,
                            'attack': 76,
                            'defense': 75,
                            'special-attack': 81,
                            'special-defense': 100,
                            'speed': 100
                        },
                        'attack': 174,
                        'defense': 172,
                        'special-attack': 182,
                        'special-defense': 214,
                        'speed': 214,
                        'attack_boost': 0,
                        'defense_boost': 0,
                        'special_attack_boost': 0,
                        'special_defense_boost': 0,
                        'speed_boost': 0,
                        'status': None,
                        'volatileStatus': [

                        ],
                        'moves': [
                            {
                                'id': 'hiddenpower',
                                'disabled': False,
                                'current_pp': 24
                            },
                            {
                                'id': 'willowisp',
                                'disabled': False,
                                'current_pp': 24
                            },
                            {
                                'id': 'substitute',
                                'disabled': False,
                                'current_pp': 16
                            },
                            {
                                'id': 'fireblast',
                                'disabled': False,
                                'current_pp': 8
                            }
                        ],
                        'types': [
                            'fire'
                        ]
                    },
                    'reserve': {
                        'registeel': {
                            'canMegaEvo': False,
                            'id': 'registeel',
                            'level': 79,
                            'hp': 256,
                            'maxhp': 256,
                            'ability': 'clearbody',
                            'item': '',
                            'baseStats': {
                                'hp': 80,
                                'attack': 75,
                                'defense': 150,
                                'special-attack': 75,
                                'special-defense': 150,
                                'speed': 50
                            },
                            'attack': 164,
                            'defense': 283,
                            'special-attack': 164,
                            'special-defense': 283,
                            'speed': 125,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'rest',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'curse',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'sleeptalk',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'ironhead',
                                    'disabled': False,
                                    'current_pp': 24
                                }
                            ],
                            'types': [
                                'steel'
                            ]
                        },
                        'swanna': {
                            'canMegaEvo': False,
                            'id': 'swanna',
                            'level': 83,
                            'hp': 259,
                            'maxhp': 260,
                            'ability': 'hydration',
                            'item': '',
                            'baseStats': {
                                'hp': 75,
                                'attack': 87,
                                'defense': 63,
                                'special-attack': 87,
                                'special-defense': 63,
                                'speed': 98
                            },
                            'attack': 192,
                            'defense': 152,
                            'special-attack': 192,
                            'special-defense': 152,
                            'speed': 210,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'icebeam',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'raindance',
                                    'disabled': False,
                                    'current_pp': 8
                                },
                                {
                                    'id': 'hurricane',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'scald',
                                    'disabled': False,
                                    'current_pp': 24
                                }
                            ],
                            'types': [
                                'water',
                                'flying'
                            ]
                        },
                        'kommoo': {
                            'canMegaEvo': False,
                            'id': 'kommoo',
                            'level': 79,
                            'hp': 37,
                            'maxhp': 248,
                            'ability': 'bulletproof',
                            'item': '',
                            'baseStats': {
                                'hp': 75,
                                'attack': 110,
                                'defense': 125,
                                'special-attack': 100,
                                'special-defense': 105,
                                'speed': 85
                            },
                            'attack': 219,
                            'defense': 243,
                            'special-attack': 204,
                            'special-defense': 211,
                            'speed': 180,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'skyuppercut',
                                    'disabled': False,
                                    'current_pp': 24
                                },
                                {
                                    'id': 'poisonjab',
                                    'disabled': False,
                                    'current_pp': 32
                                },
                                {
                                    'id': 'dragonclaw',
                                    'disabled': False,
                                    'current_pp': 24
                                },
                                {
                                    'id': 'dragondance',
                                    'disabled': False,
                                    'current_pp': 32
                                }
                            ],
                            'types': [
                                'dragon',
                                'fighting'
                            ]
                        },
                        'mothim': {
                            'canMegaEvo': False,
                            'id': 'mothim',
                            'level': 83,
                            'hp': 251,
                            'maxhp': 252,
                            'ability': 'tintedlens',
                            'item': '',
                            'baseStats': {
                                'hp': 70,
                                'attack': 94,
                                'defense': 50,
                                'special-attack': 94,
                                'special-defense': 50,
                                'speed': 66
                            },
                            'attack': 204,
                            'defense': 131,
                            'special-attack': 204,
                            'special-defense': 131,
                            'speed': 157,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'quiverdance',
                                    'disabled': False,
                                    'current_pp': 32
                                },
                                {
                                    'id': 'gigadrain',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'bugbuzz',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'airslash',
                                    'disabled': False,
                                    'current_pp': 24
                                }
                            ],
                            'types': [
                                'bug',
                                'flying'
                            ]
                        },
                        'magearna': {
                            'canMegaEvo': False,
                            'id': 'magearna',
                            'level': 75,
                            'hp': 244,
                            'maxhp': 244,
                            'ability': 'soulheart',
                            'item': '',
                            'baseStats': {
                                'hp': 80,
                                'attack': 95,
                                'defense': 115,
                                'special-attack': 130,
                                'special-defense': 115,
                                'speed': 65
                            },
                            'attack': 186,
                            'defense': 216,
                            'special-attack': 239,
                            'special-defense': 216,
                            'speed': 141,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'icebeam',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'flashcannon',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'fleurcannon',
                                    'disabled': False,
                                    'current_pp': 8
                                },
                                {
                                    'id': 'thunderbolt',
                                    'disabled': False,
                                    'current_pp': 24
                                }
                            ],
                            'types': [
                                'steel',
                                'fairy'
                            ]
                        }
                    },
                    'side_conditions': {
                        'stealthrock': 0,
                        'spikes': 0
                    },
                    'trapped': False
                },
                'opponent': {
                    'active': {
                        'canMegaEvo': False,
                        'id': 'luxray',
                        'level': 83,
                        'hp': 115.24,
                        'maxhp': 268,
                        'ability': None,
                        'item': '',
                        'baseStats': {
                            'hp': 80,
                            'attack': 120,
                            'defense': 79,
                            'special-attack': 95,
                            'special-defense': 79,
                            'speed': 70
                        },
                        'attack': 247,
                        'defense': 179,
                        'special-attack': 205,
                        'special-defense': 179,
                        'speed': 164,
                        'attack_boost': 0,
                        'defense_boost': 0,
                        'special_attack_boost': 0,
                        'special_defense_boost': 0,
                        'speed_boost': 0,
                        'status': 'brn',
                        'volatileStatus': [

                        ],
                        'moves': [
                            {
                                'id': 'icefang',
                                'disabled': False,
                                'current_pp': 24
                            },
                            {
                                'id': 'facade',
                                'disabled': False,
                                'current_pp': 32
                            }
                        ],
                        'types': [
                            'electric'
                        ]
                    },
                    'reserve': {

                    },
                    'side_conditions': {

                    },
                    'trapped': False
                },
                'weather': None,
                'field': None,
                'forceSwitch': False,
                'wait': False,
                'trickroom': False
            }
        )
        self.mutator.state = self.state

        bot_move = "fireblast"
        opponent_move = "crunch"

        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                0.17,
                [
                    ('damage', 'opponent', 111),
                    ('damage', 'self', 37),
                    ('boost', 'self', 'defense', -1),
                    ('damage', 'opponent', 4)

                ],
                False
            ),
            TransposeInstruction(
                0.68,
                [
                    ('damage', 'opponent', 111),
                    ('damage', 'self', 37),
                    ('damage', 'opponent', 4)

                ],
                False
            ),
            TransposeInstruction(
                0.030000000000000006,
                [
                    ('damage', 'self', 37),
                    ('boost', 'self', 'defense', -1),
                    ('damage', 'opponent', 16)

                ],
                False
            ),
            TransposeInstruction(
                0.12000000000000002,
                [
                    ('damage', 'self', 37),
                    ('damage', 'opponent', 16)

                ],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_fireblast_into_crunch_produces_six_states(self):
        self.state = State.from_dict(
            {
                'self': {
                    'active': {
                        'canMegaEvo': False,
                        'id': 'ninetales',
                        'level': 83,
                        'hp': 228,
                        'maxhp': 257,
                        'ability': 'drought',
                        'item': '',
                        'baseStats': {
                            'hp': 73,
                            'attack': 76,
                            'defense': 75,
                            'special-attack': 81,
                            'special-defense': 100,
                            'speed': 100
                        },
                        'attack': 174,
                        'defense': 172,
                        'special-attack': 182,
                        'special-defense': 214,
                        'speed': 214,
                        'attack_boost': 0,
                        'defense_boost': 0,
                        'special_attack_boost': 0,
                        'special_defense_boost': 0,
                        'speed_boost': 0,
                        'status': None,
                        'volatileStatus': [

                        ],
                        'moves': [
                            {
                                'id': 'hiddenpower',
                                'disabled': False,
                                'current_pp': 24
                            },
                            {
                                'id': 'willowisp',
                                'disabled': False,
                                'current_pp': 24
                            },
                            {
                                'id': 'substitute',
                                'disabled': False,
                                'current_pp': 16
                            },
                            {
                                'id': 'fireblast',
                                'disabled': False,
                                'current_pp': 8
                            }
                        ],
                        'types': [
                            'fire'
                        ]
                    },
                    'reserve': {
                        'registeel': {
                            'canMegaEvo': False,
                            'id': 'registeel',
                            'level': 79,
                            'hp': 256,
                            'maxhp': 256,
                            'ability': 'clearbody',
                            'item': '',
                            'baseStats': {
                                'hp': 80,
                                'attack': 75,
                                'defense': 150,
                                'special-attack': 75,
                                'special-defense': 150,
                                'speed': 50
                            },
                            'attack': 164,
                            'defense': 283,
                            'special-attack': 164,
                            'special-defense': 283,
                            'speed': 125,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'rest',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'curse',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'sleeptalk',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'ironhead',
                                    'disabled': False,
                                    'current_pp': 24
                                }
                            ],
                            'types': [
                                'steel'
                            ]
                        },
                        'swanna': {
                            'canMegaEvo': False,
                            'id': 'swanna',
                            'level': 83,
                            'hp': 259,
                            'maxhp': 260,
                            'ability': 'hydration',
                            'item': '',
                            'baseStats': {
                                'hp': 75,
                                'attack': 87,
                                'defense': 63,
                                'special-attack': 87,
                                'special-defense': 63,
                                'speed': 98
                            },
                            'attack': 192,
                            'defense': 152,
                            'special-attack': 192,
                            'special-defense': 152,
                            'speed': 210,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'icebeam',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'raindance',
                                    'disabled': False,
                                    'current_pp': 8
                                },
                                {
                                    'id': 'hurricane',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'scald',
                                    'disabled': False,
                                    'current_pp': 24
                                }
                            ],
                            'types': [
                                'water',
                                'flying'
                            ]
                        },
                        'kommoo': {
                            'canMegaEvo': False,
                            'id': 'kommoo',
                            'level': 79,
                            'hp': 37,
                            'maxhp': 248,
                            'ability': 'bulletproof',
                            'item': '',
                            'baseStats': {
                                'hp': 75,
                                'attack': 110,
                                'defense': 125,
                                'special-attack': 100,
                                'special-defense': 105,
                                'speed': 85
                            },
                            'attack': 219,
                            'defense': 243,
                            'special-attack': 204,
                            'special-defense': 211,
                            'speed': 180,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'skyuppercut',
                                    'disabled': False,
                                    'current_pp': 24
                                },
                                {
                                    'id': 'poisonjab',
                                    'disabled': False,
                                    'current_pp': 32
                                },
                                {
                                    'id': 'dragonclaw',
                                    'disabled': False,
                                    'current_pp': 24
                                },
                                {
                                    'id': 'dragondance',
                                    'disabled': False,
                                    'current_pp': 32
                                }
                            ],
                            'types': [
                                'dragon',
                                'fighting'
                            ]
                        },
                        'mothim': {
                            'canMegaEvo': False,
                            'id': 'mothim',
                            'level': 83,
                            'hp': 251,
                            'maxhp': 252,
                            'ability': 'tintedlens',
                            'item': '',
                            'baseStats': {
                                'hp': 70,
                                'attack': 94,
                                'defense': 50,
                                'special-attack': 94,
                                'special-defense': 50,
                                'speed': 66
                            },
                            'attack': 204,
                            'defense': 131,
                            'special-attack': 204,
                            'special-defense': 131,
                            'speed': 157,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'quiverdance',
                                    'disabled': False,
                                    'current_pp': 32
                                },
                                {
                                    'id': 'gigadrain',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'bugbuzz',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'airslash',
                                    'disabled': False,
                                    'current_pp': 24
                                }
                            ],
                            'types': [
                                'bug',
                                'flying'
                            ]
                        },
                        'magearna': {
                            'canMegaEvo': False,
                            'id': 'magearna',
                            'level': 75,
                            'hp': 244,
                            'maxhp': 244,
                            'ability': 'soulheart',
                            'item': '',
                            'baseStats': {
                                'hp': 80,
                                'attack': 95,
                                'defense': 115,
                                'special-attack': 130,
                                'special-defense': 115,
                                'speed': 65
                            },
                            'attack': 186,
                            'defense': 216,
                            'special-attack': 239,
                            'special-defense': 216,
                            'speed': 141,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'icebeam',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'flashcannon',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'fleurcannon',
                                    'disabled': False,
                                    'current_pp': 8
                                },
                                {
                                    'id': 'thunderbolt',
                                    'disabled': False,
                                    'current_pp': 24
                                }
                            ],
                            'types': [
                                'steel',
                                'fairy'
                            ]
                        }
                    },
                    'side_conditions': {
                        'stealthrock': 0,
                        'spikes': 0
                    },
                    'trapped': False
                },
                'opponent': {
                    'active': {
                        'canMegaEvo': False,
                        'id': 'luxray',
                        'level': 83,
                        'hp': 115.24,
                        'maxhp': 268,
                        'ability': None,
                        'item': '',
                        'baseStats': {
                            'hp': 80,
                            'attack': 120,
                            'defense': 79,
                            'special-attack': 95,
                            'special-defense': 79,
                            'speed': 70
                        },
                        'attack': 247,
                        'defense': 179,
                        'special-attack': 205,
                        'special-defense': 179,
                        'speed': 164,
                        'attack_boost': 0,
                        'defense_boost': 0,
                        'special_attack_boost': 0,
                        'special_defense_boost': 0,
                        'speed_boost': 0,
                        'status': None,
                        'volatileStatus': [

                        ],
                        'moves': [
                            {
                                'id': 'icefang',
                                'disabled': False,
                                'current_pp': 24
                            },
                            {
                                'id': 'facade',
                                'disabled': False,
                                'current_pp': 32
                            }
                        ],
                        'types': [
                            'electric'
                        ]
                    },
                    'reserve': {

                    },
                    'side_conditions': {

                    },
                    'trapped': False
                },
                'weather': None,
                'field': None,
                'forceSwitch': False,
                'wait': False,
                'trickroom': False
            }
        )
        self.mutator.state = self.state

        bot_move = "fireblast"
        opponent_move = "crunch"

        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                0.017,
                [
                    ('damage', 'opponent', 111),
                    ('apply_status', 'opponent', 'brn'),
                    ('damage', 'self', 37),
                    ('boost', 'self', 'defense', -1),
                    ('damage', 'opponent', 4)

                ],
                False
            ),
            TransposeInstruction(
                0.068,
                [
                    ('damage', 'opponent', 111),
                    ('apply_status', 'opponent', 'brn'),
                    ('damage', 'self', 37),
                    ('damage', 'opponent', 4)

                ],
                False
            ),
            TransposeInstruction(
                0.15300000000000002,
                [
                    ('damage', 'opponent', 111),
                    ('damage', 'self', 75),
                    ('boost', 'self', 'defense', -1)

                ],
                False
            ),
            TransposeInstruction(
                0.6120000000000001,
                [
                    ('damage', 'opponent', 111),
                    ('damage', 'self', 75),

                ],
                False
            ),
            TransposeInstruction(
                0.030000000000000006,
                [
                    ('damage', 'self', 75),
                    ('boost', 'self', 'defense', -1)

                ],
                False
            ),
            TransposeInstruction(
                0.12000000000000002,
                [
                    ('damage', 'self', 75),

                ],
                False
            ),
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_removes_flinch_status_when_pokemon_faints(self):
        self.state = State.from_dict(
            {
                'self': {
                    'active': {
                        'canMegaEvo': False,
                        'id': 'excadrill',
                        'level': 83,
                        'hp': 228,
                        'maxhp': 257,
                        'ability': 'moldbreaker',
                        'item': '',
                        'baseStats': {
                            'hp': 73,
                            'attack': 76,
                            'defense': 75,
                            'special-attack': 81,
                            'special-defense': 100,
                            'speed': 100
                        },
                        'attack': 174,
                        'defense': 172,
                        'special-attack': 182,
                        'special-defense': 214,
                        'speed': 214,
                        'attack_boost': 0,
                        'defense_boost': 0,
                        'special_attack_boost': 0,
                        'special_defense_boost': 0,
                        'speed_boost': 0,
                        'status': None,
                        'volatileStatus': [

                        ],
                        'moves': [
                            {
                                'id': 'hiddenpower',
                                'disabled': False,
                                'current_pp': 24
                            },
                            {
                                'id': 'willowisp',
                                'disabled': False,
                                'current_pp': 24
                            },
                            {
                                'id': 'substitute',
                                'disabled': False,
                                'current_pp': 16
                            },
                            {
                                'id': 'fireblast',
                                'disabled': False,
                                'current_pp': 8
                            }
                        ],
                        'types': [
                            'ground',
                            'steel'
                        ]
                    },
                    'reserve': {
                        'registeel': {
                            'canMegaEvo': False,
                            'id': 'registeel',
                            'level': 79,
                            'hp': 256,
                            'maxhp': 256,
                            'ability': 'clearbody',
                            'item': '',
                            'baseStats': {
                                'hp': 80,
                                'attack': 75,
                                'defense': 150,
                                'special-attack': 75,
                                'special-defense': 150,
                                'speed': 50
                            },
                            'attack': 164,
                            'defense': 283,
                            'special-attack': 164,
                            'special-defense': 283,
                            'speed': 125,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'rest',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'curse',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'sleeptalk',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'ironhead',
                                    'disabled': False,
                                    'current_pp': 24
                                }
                            ],
                            'types': [
                                'steel'
                            ]
                        },
                        'swanna': {
                            'canMegaEvo': False,
                            'id': 'swanna',
                            'level': 83,
                            'hp': 259,
                            'maxhp': 260,
                            'ability': 'hydration',
                            'item': '',
                            'baseStats': {
                                'hp': 75,
                                'attack': 87,
                                'defense': 63,
                                'special-attack': 87,
                                'special-defense': 63,
                                'speed': 98
                            },
                            'attack': 192,
                            'defense': 152,
                            'special-attack': 192,
                            'special-defense': 152,
                            'speed': 210,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'icebeam',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'raindance',
                                    'disabled': False,
                                    'current_pp': 8
                                },
                                {
                                    'id': 'hurricane',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'scald',
                                    'disabled': False,
                                    'current_pp': 24
                                }
                            ],
                            'types': [
                                'water',
                                'flying'
                            ]
                        },
                        'kommoo': {
                            'canMegaEvo': False,
                            'id': 'kommoo',
                            'level': 79,
                            'hp': 37,
                            'maxhp': 248,
                            'ability': 'bulletproof',
                            'item': '',
                            'baseStats': {
                                'hp': 75,
                                'attack': 110,
                                'defense': 125,
                                'special-attack': 100,
                                'special-defense': 105,
                                'speed': 85
                            },
                            'attack': 219,
                            'defense': 243,
                            'special-attack': 204,
                            'special-defense': 211,
                            'speed': 180,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'skyuppercut',
                                    'disabled': False,
                                    'current_pp': 24
                                },
                                {
                                    'id': 'poisonjab',
                                    'disabled': False,
                                    'current_pp': 32
                                },
                                {
                                    'id': 'dragonclaw',
                                    'disabled': False,
                                    'current_pp': 24
                                },
                                {
                                    'id': 'dragondance',
                                    'disabled': False,
                                    'current_pp': 32
                                }
                            ],
                            'types': [
                                'dragon',
                                'fighting'
                            ]
                        },
                        'mothim': {
                            'canMegaEvo': False,
                            'id': 'mothim',
                            'level': 83,
                            'hp': 251,
                            'maxhp': 252,
                            'ability': 'tintedlens',
                            'item': '',
                            'baseStats': {
                                'hp': 70,
                                'attack': 94,
                                'defense': 50,
                                'special-attack': 94,
                                'special-defense': 50,
                                'speed': 66
                            },
                            'attack': 204,
                            'defense': 131,
                            'special-attack': 204,
                            'special-defense': 131,
                            'speed': 157,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'quiverdance',
                                    'disabled': False,
                                    'current_pp': 32
                                },
                                {
                                    'id': 'gigadrain',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'bugbuzz',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'airslash',
                                    'disabled': False,
                                    'current_pp': 24
                                }
                            ],
                            'types': [
                                'bug',
                                'flying'
                            ]
                        },
                        'magearna': {
                            'canMegaEvo': False,
                            'id': 'magearna',
                            'level': 75,
                            'hp': 244,
                            'maxhp': 244,
                            'ability': 'soulheart',
                            'item': '',
                            'baseStats': {
                                'hp': 80,
                                'attack': 95,
                                'defense': 115,
                                'special-attack': 130,
                                'special-defense': 115,
                                'speed': 65
                            },
                            'attack': 186,
                            'defense': 216,
                            'special-attack': 239,
                            'special-defense': 216,
                            'speed': 141,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'icebeam',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'flashcannon',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'fleurcannon',
                                    'disabled': False,
                                    'current_pp': 8
                                },
                                {
                                    'id': 'thunderbolt',
                                    'disabled': False,
                                    'current_pp': 24
                                }
                            ],
                            'types': [
                                'steel',
                                'fairy'
                            ]
                        }
                    },
                    'side_conditions': {
                        'stealthrock': 0,
                        'spikes': 0
                    },
                    'trapped': False
                },
                'opponent': {
                    'active': {
                        'canMegaEvo': False,
                        'id': 'luxray',
                        'level': 83,
                        'hp': 44,
                        'maxhp': 268,
                        'ability': None,
                        'item': '',
                        'baseStats': {
                            'hp': 80,
                            'attack': 120,
                            'defense': 79,
                            'special-attack': 95,
                            'special-defense': 79,
                            'speed': 70
                        },
                        'attack': 247,
                        'defense': 179,
                        'special-attack': 205,
                        'special-defense': 179,
                        'speed': 164,
                        'attack_boost': 0,
                        'defense_boost': 0,
                        'special_attack_boost': 0,
                        'special_defense_boost': 0,
                        'speed_boost': 0,
                        'status': None,
                        'volatileStatus': [

                        ],
                        'moves': [
                            {
                                'id': 'icefang',
                                'disabled': False,
                                'current_pp': 24
                            },
                            {
                                'id': 'facade',
                                'disabled': False,
                                'current_pp': 32
                            }
                        ],
                        'types': [
                            'electric'
                        ]
                    },
                    'reserve': {

                    },
                    'side_conditions': {

                    },
                    'trapped': False
                },
                'weather': None,
                'field': None,
                'forceSwitch': False,
                'wait': False,
                'trickroom': False
            }
        )
        self.mutator.state = self.state

        bot_move = "rockslide"
        opponent_move = "splash"

        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                0.27,
                [
                    (constants.DAMAGE, constants.OPPONENT, 44),
                    (constants.MUTATOR_APPLY_VOLATILE_STATUS, constants.OPPONENT, constants.FLINCH),
                    (constants.MUTATOR_REMOVE_VOLATILE_STATUS, constants.OPPONENT, constants.FLINCH)
                ],
                True
            ),
            TransposeInstruction(
                0.63,
                [
                    (constants.DAMAGE, constants.OPPONENT, 44)

                ],
                False
            ),
            TransposeInstruction(
                0.09999999999999998,
                [],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_explosion_kills_the_user(self):
        self.state = State.from_dict(
            {
                'self': {
                    'active': {
                        'canMegaEvo': False,
                        'id': 'ninetales',
                        'level': 83,
                        'hp': 228,
                        'maxhp': 257,
                        'ability': 'drought',
                        'item': '',
                        'baseStats': {
                            'hp': 73,
                            'attack': 76,
                            'defense': 75,
                            'special-attack': 81,
                            'special-defense': 100,
                            'speed': 100
                        },
                        'attack': 174,
                        'defense': 172,
                        'special-attack': 182,
                        'special-defense': 214,
                        'speed': 214,
                        'attack_boost': 0,
                        'defense_boost': 0,
                        'special_attack_boost': 0,
                        'special_defense_boost': 0,
                        'speed_boost': 0,
                        'status': None,
                        'volatileStatus': [

                        ],
                        'moves': [
                            {
                                'id': 'hiddenpower',
                                'disabled': False,
                                'current_pp': 24
                            },
                            {
                                'id': 'willowisp',
                                'disabled': False,
                                'current_pp': 24
                            },
                            {
                                'id': 'substitute',
                                'disabled': False,
                                'current_pp': 16
                            },
                            {
                                'id': 'fireblast',
                                'disabled': False,
                                'current_pp': 8
                            }
                        ],
                        'types': [
                            'fire'
                        ]
                    },
                    'reserve': {
                        'registeel': {
                            'canMegaEvo': False,
                            'id': 'registeel',
                            'level': 79,
                            'hp': 256,
                            'maxhp': 256,
                            'ability': 'clearbody',
                            'item': '',
                            'baseStats': {
                                'hp': 80,
                                'attack': 75,
                                'defense': 150,
                                'special-attack': 75,
                                'special-defense': 150,
                                'speed': 50
                            },
                            'attack': 164,
                            'defense': 283,
                            'special-attack': 164,
                            'special-defense': 283,
                            'speed': 125,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'rest',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'curse',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'sleeptalk',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'ironhead',
                                    'disabled': False,
                                    'current_pp': 24
                                }
                            ],
                            'types': [
                                'steel'
                            ]
                        },
                        'swanna': {
                            'canMegaEvo': False,
                            'id': 'swanna',
                            'level': 83,
                            'hp': 259,
                            'maxhp': 260,
                            'ability': 'hydration',
                            'item': '',
                            'baseStats': {
                                'hp': 75,
                                'attack': 87,
                                'defense': 63,
                                'special-attack': 87,
                                'special-defense': 63,
                                'speed': 98
                            },
                            'attack': 192,
                            'defense': 152,
                            'special-attack': 192,
                            'special-defense': 152,
                            'speed': 210,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'icebeam',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'raindance',
                                    'disabled': False,
                                    'current_pp': 8
                                },
                                {
                                    'id': 'hurricane',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'scald',
                                    'disabled': False,
                                    'current_pp': 24
                                }
                            ],
                            'types': [
                                'water',
                                'flying'
                            ]
                        },
                        'kommoo': {
                            'canMegaEvo': False,
                            'id': 'kommoo',
                            'level': 79,
                            'hp': 37,
                            'maxhp': 248,
                            'ability': 'bulletproof',
                            'item': '',
                            'baseStats': {
                                'hp': 75,
                                'attack': 110,
                                'defense': 125,
                                'special-attack': 100,
                                'special-defense': 105,
                                'speed': 85
                            },
                            'attack': 219,
                            'defense': 243,
                            'special-attack': 204,
                            'special-defense': 211,
                            'speed': 180,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'skyuppercut',
                                    'disabled': False,
                                    'current_pp': 24
                                },
                                {
                                    'id': 'poisonjab',
                                    'disabled': False,
                                    'current_pp': 32
                                },
                                {
                                    'id': 'dragonclaw',
                                    'disabled': False,
                                    'current_pp': 24
                                },
                                {
                                    'id': 'dragondance',
                                    'disabled': False,
                                    'current_pp': 32
                                }
                            ],
                            'types': [
                                'dragon',
                                'fighting'
                            ]
                        },
                        'mothim': {
                            'canMegaEvo': False,
                            'id': 'mothim',
                            'level': 83,
                            'hp': 251,
                            'maxhp': 252,
                            'ability': 'tintedlens',
                            'item': '',
                            'baseStats': {
                                'hp': 70,
                                'attack': 94,
                                'defense': 50,
                                'special-attack': 94,
                                'special-defense': 50,
                                'speed': 66
                            },
                            'attack': 204,
                            'defense': 131,
                            'special-attack': 204,
                            'special-defense': 131,
                            'speed': 157,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'quiverdance',
                                    'disabled': False,
                                    'current_pp': 32
                                },
                                {
                                    'id': 'gigadrain',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'bugbuzz',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'airslash',
                                    'disabled': False,
                                    'current_pp': 24
                                }
                            ],
                            'types': [
                                'bug',
                                'flying'
                            ]
                        },
                        'magearna': {
                            'canMegaEvo': False,
                            'id': 'magearna',
                            'level': 75,
                            'hp': 244,
                            'maxhp': 244,
                            'ability': 'soulheart',
                            'item': '',
                            'baseStats': {
                                'hp': 80,
                                'attack': 95,
                                'defense': 115,
                                'special-attack': 130,
                                'special-defense': 115,
                                'speed': 65
                            },
                            'attack': 186,
                            'defense': 216,
                            'special-attack': 239,
                            'special-defense': 216,
                            'speed': 141,
                            'attack_boost': 0,
                            'defense_boost': 0,
                            'special_attack_boost': 0,
                            'special_defense_boost': 0,
                            'speed_boost': 0,
                            'status': None,
                            'volatileStatus': [

                            ],
                            'moves': [
                                {
                                    'id': 'icebeam',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'flashcannon',
                                    'disabled': False,
                                    'current_pp': 16
                                },
                                {
                                    'id': 'fleurcannon',
                                    'disabled': False,
                                    'current_pp': 8
                                },
                                {
                                    'id': 'thunderbolt',
                                    'disabled': False,
                                    'current_pp': 24
                                }
                            ],
                            'types': [
                                'steel',
                                'fairy'
                            ]
                        }
                    },
                    'side_conditions': {
                        'stealthrock': 0,
                        'spikes': 0
                    },
                    'trapped': False
                },
                'opponent': {
                    'active': {
                        'canMegaEvo': False,
                        'id': 'luxray',
                        'level': 83,
                        'hp': 115.24,
                        'maxhp': 268,
                        'ability': None,
                        'item': '',
                        'baseStats': {
                            'hp': 80,
                            'attack': 120,
                            'defense': 79,
                            'special-attack': 95,
                            'special-defense': 79,
                            'speed': 70
                        },
                        'attack': 247,
                        'defense': 179,
                        'special-attack': 205,
                        'special-defense': 179,
                        'speed': 164,
                        'attack_boost': 0,
                        'defense_boost': 0,
                        'special_attack_boost': 0,
                        'special_defense_boost': 0,
                        'speed_boost': 0,
                        'status': 'brn',
                        'volatileStatus': [

                        ],
                        'moves': [
                            {
                                'id': 'icefang',
                                'disabled': False,
                                'current_pp': 24
                            },
                            {
                                'id': 'facade',
                                'disabled': False,
                                'current_pp': 32
                            }
                        ],
                        'types': [
                            'electric'
                        ]
                    },
                    'reserve': {

                    },
                    'side_conditions': {

                    },
                    'trapped': False
                },
                'weather': 'sunnyday',
                'field': None,
                'forceSwitch': False,
                'wait': False,
                'trickroom': False
            }
        )
        self.mutator.state = self.state

        bot_move = "explosion"
        opponent_move = "crunch"

        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    ('damage', 'opponent', 115.24),
                    ('heal', 'self', -228.0)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_closecombat_kills_and_reduces_stats(self):
        self.state = State.from_dict(
            {'self': {'active': {'id': 'hitmontop', 'level': 81, 'hp': 77, 'maxhp': 214, 'ability': 'intimidate',
                                 'item': None,
                                 'baseStats': {'hp': 50, 'attack': 95, 'defense': 95, 'special-attack': 35,
                                               'special-defense': 110, 'speed': 70}, 'attack': 201, 'defense': 201,
                                 'special-attack': 103, 'special-defense': 225, 'speed': 160, 'attack_boost': 0,
                                 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                 'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                 'moves': [{'id': 'toxic', 'disabled': False, 'current_pp': 11},
                                           {'id': 'suckerpunch', 'disabled': False, 'current_pp': 8},
                                           {'id': 'rapidspin', 'disabled': False, 'current_pp': 59},
                                           {'id': 'machpunch', 'disabled': False, 'current_pp': 8}],
                                 'types': ['fighting'], 'canMegaEvo': False}, 'reserve': {
                'seismitoad': {'id': 'seismitoad', 'level': 81, 'hp': 195, 'maxhp': 303, 'ability': 'waterabsorb',
                               'item': None, 'baseStats': {'hp': 105, 'attack': 95, 'defense': 75, 'special-attack': 85,
                                                           'special-defense': 75, 'speed': 74}, 'attack': 201,
                               'defense': 168, 'special-attack': 184, 'special-defense': 168, 'speed': 167,
                               'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0,
                               'special_defense_boost': 0, 'speed_boost': 0, 'status': 'tox', 'volatileStatus': [],
                               'moves': [{'id': 'earthquake', 'disabled': False, 'current_pp': 16},
                                         {'id': 'stealthrock', 'disabled': False, 'current_pp': 32},
                                         {'id': 'scald', 'disabled': False, 'current_pp': 24},
                                         {'id': 'knockoff', 'disabled': False, 'current_pp': 32}],
                               'types': ['water', 'ground'], 'canMegaEvo': False},
                'ribombee': {'id': 'ribombee', 'level': 80, 'hp': 0, 'maxhp': 227, 'ability': 'shielddust',
                             'item': None, 'baseStats': {'hp': 60, 'attack': 55, 'defense': 60, 'special-attack': 95,
                                                         'special-defense': 70, 'speed': 124}, 'attack': 134,
                             'defense': 142, 'special-attack': 198, 'special-defense': 158, 'speed': 245,
                             'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0,
                             'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [],
                             'moves': [{'id': 'bugbuzz', 'disabled': False, 'current_pp': 16},
                                       {'id': 'moonblast', 'disabled': False, 'current_pp': 24},
                                       {'id': 'roost', 'disabled': False, 'current_pp': 16},
                                       {'id': 'quiverdance', 'disabled': False, 'current_pp': 32}],
                             'types': ['bug', 'fairy'], 'canMegaEvo': False},
                'leafeon': {'id': 'leafeon', 'level': 84, 'hp': 0, 'maxhp': 246, 'ability': 'chlorophyll', 'item': None,
                            'baseStats': {'hp': 65, 'attack': 110, 'defense': 130, 'special-attack': 60,
                                          'special-defense': 65, 'speed': 95}, 'attack': 233, 'defense': 267,
                            'special-attack': 149, 'special-defense': 157, 'speed': 208, 'attack_boost': 0,
                            'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0,
                            'status': None, 'volatileStatus': [],
                            'moves': [{'id': 'xscissor', 'disabled': False, 'current_pp': 24},
                                      {'id': 'healbell', 'disabled': False, 'current_pp': 8},
                                      {'id': 'leafblade', 'disabled': False, 'current_pp': 24},
                                      {'id': 'swordsdance', 'disabled': False, 'current_pp': 32}], 'types': ['grass'],
                            'canMegaEvo': False},
                'lickilicky': {'id': 'lickilicky', 'level': 84, 'hp': 0, 'maxhp': 322, 'ability': 'cloudnine',
                               'item': None, 'baseStats': {'hp': 110, 'attack': 85, 'defense': 95, 'special-attack': 80,
                                                           'special-defense': 95, 'speed': 50}, 'attack': 191,
                               'defense': 208, 'special-attack': 183, 'special-defense': 208, 'speed': 132,
                               'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0,
                               'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [],
                               'moves': [{'id': 'bodyslam', 'disabled': False, 'current_pp': 24},
                                         {'id': 'powerwhip', 'disabled': False, 'current_pp': 16},
                                         {'id': 'wish', 'disabled': False, 'current_pp': 16},
                                         {'id': 'earthquake', 'disabled': False, 'current_pp': 16}],
                               'types': ['normal'], 'canMegaEvo': False},
                'magmortar': {'id': 'magmortar', 'level': 81, 'hp': 0, 'maxhp': 254, 'ability': 'vitalspirit',
                              'item': None, 'baseStats': {'hp': 75, 'attack': 95, 'defense': 67, 'special-attack': 125,
                                                          'special-defense': 95, 'speed': 83}, 'attack': 201,
                              'defense': 155, 'special-attack': 249, 'special-defense': 201, 'speed': 181,
                              'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0,
                              'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [],
                              'moves': [{'id': 'thunderbolt', 'disabled': False, 'current_pp': 24},
                                        {'id': 'fireblast', 'disabled': False, 'current_pp': 8},
                                        {'id': 'hiddenpowerice60', 'disabled': False, 'current_pp': 24},
                                        {'id': 'earthquake', 'disabled': False, 'current_pp': 16}], 'types': ['fire'],
                              'canMegaEvo': False}},
                      'side_conditions': {'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0,
                                          'stealthrock': 0, 'spikes': 0, 'stickyweb': 0, 'toxicspikes': 0, 'Wish': 0},
                      'trapped': False}, 'opponent': {
                'active': {'id': 'steelixmega', 'level': 77, 'hp': 4.84, 'maxhp': 242, 'ability': 'sandforce',
                           'item': None, 'baseStats': {'hp': 75, 'attack': 125, 'defense': 230, 'special-attack': 55,
                                                       'special-defense': 95, 'speed': 30}, 'attack': 237,
                           'defense': 399, 'special-attack': 129, 'special-defense': 191, 'speed': 91,
                           'attack_boost': -4, 'defense_boost': 0, 'special_attack_boost': 0,
                           'special_defense_boost': 0, 'speed_boost': 0, 'status': 'par', 'volatileStatus': [],
                           'moves': [{'id': 'heavyslam', 'disabled': False, 'current_pp': 16},
                                     {'id': 'earthquake', 'disabled': False, 'current_pp': 16},
                                     {'id': 'toxic', 'disabled': False, 'current_pp': 16},
                                     {'id': 'roar', 'disabled': False, 'current_pp': 32}], 'types': ['steel', 'ground'],
                           'canMegaEvo': False}, 'reserve': {
                    'beartic': {'id': 'beartic', 'level': 84, 'hp': 297, 'maxhp': 297, 'ability': 'swiftswim',
                                'item': None,
                                'baseStats': {'hp': 95, 'attack': 130, 'defense': 80, 'special-attack': 70,
                                              'special-defense': 80, 'speed': 50}, 'attack': 267, 'defense': 183,
                                'special-attack': 166, 'special-defense': 183, 'speed': 132, 'attack_boost': 0,
                                'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [], 'types': ['ice'],
                                'canMegaEvo': False},
                    'carbink': {'id': 'carbink', 'level': 84, 'hp': 0, 'maxhp': 221, 'ability': 'sturdy', 'item': None,
                                'baseStats': {'hp': 50, 'attack': 50, 'defense': 150, 'special-attack': 50,
                                              'special-defense': 150, 'speed': 50}, 'attack': 132, 'defense': 300,
                                'special-attack': 132, 'special-defense': 300, 'speed': 132, 'attack_boost': 0,
                                'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                'moves': [{'id': 'stealthrock', 'disabled': False, 'current_pp': 32},
                                          {'id': 'powergem', 'disabled': False, 'current_pp': 32}],
                                'types': ['rock', 'fairy'], 'canMegaEvo': False},
                    'deoxysspeed': {'id': 'deoxysspeed', 'level': 73, 'hp': 73.34, 'maxhp': 193, 'ability': 'pressure',
                                    'item': 'Life Orb',
                                    'baseStats': {'hp': 50, 'attack': 95, 'defense': 90, 'special-attack': 95,
                                                  'special-defense': 90, 'speed': 180}, 'attack': 181, 'defense': 174,
                                    'special-attack': 181, 'special-defense': 174, 'speed': 305, 'attack_boost': 0,
                                    'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                    'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                    'moves': [{'id': 'psychoboost', 'disabled': False, 'current_pp': 8},
                                              {'id': 'superpower', 'disabled': False, 'current_pp': 8}],
                                    'types': ['psychic'], 'canMegaEvo': False},
                    'volbeat': {'id': 'volbeat', 'level': 84, 'hp': 177.12, 'maxhp': 246, 'ability': 'prankster',
                                'item': 'Leftovers',
                                'baseStats': {'hp': 65, 'attack': 73, 'defense': 75, 'special-attack': 47,
                                              'special-defense': 85, 'speed': 85}, 'attack': 171, 'defense': 174,
                                'special-attack': 127, 'special-defense': 191, 'speed': 191, 'attack_boost': 0,
                                'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                'speed_boost': 0, 'status': 'par', 'volatileStatus': [],
                                'moves': [{'id': 'tailwind', 'disabled': False, 'current_pp': 24},
                                          {'id': 'thunderwave', 'disabled': False, 'current_pp': 32},
                                          {'id': 'uturn', 'disabled': False, 'current_pp': 32},
                                          {'id': 'roost', 'disabled': False, 'current_pp': 16}], 'types': ['bug'],
                                'canMegaEvo': False}},
                'side_conditions': {'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0, 'stealthrock': 1,
                                    'spikes': 0, 'stickyweb': 0, 'toxicspikes': 0}, 'trapped': False}, 'weather': None,
             'field': None, 'forceSwitch': False, 'wait': False, 'trickroom': False}
        )
        self.mutator.state = self.state

        bot_move = "closecombat"
        opponent_move = "tackle"

        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    (constants.MUTATOR_DAMAGE, constants.OPPONENT, 4.84),
                    (constants.MUTATOR_BOOST, constants.SELF, constants.DEFENSE, -1),
                    (constants.MUTATOR_BOOST, constants.SELF, constants.SPECIAL_DEFENSE, -1)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_willowisp_on_flashfire(self):
        self.state = State.from_dict(
            {'self': {'active': {'id': 'gardevoirmega', 'level': 76, 'hp': 96, 'maxhp': 228, 'ability': 'pixilate',
                                 'item': None,
                                 'baseStats': {'hp': 68, 'attack': 85, 'defense': 65, 'special-attack': 165,
                                               'special-defense': 135, 'speed': 100}, 'attack': 173, 'defense': 143,
                                 'special-attack': 295, 'special-defense': 249, 'speed': 196, 'attack_boost': 0,
                                 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                 'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                 'moves': [{'id': 'hypervoice', 'disabled': False, 'current_pp': 13},
                                           {'id': 'substitute', 'disabled': False, 'current_pp': 16},
                                           {'id': 'psyshock', 'disabled': False, 'current_pp': 15},
                                           {'id': 'willowisp', 'disabled': False, 'current_pp': 23}],
                                 'types': ['psychic', 'fairy'], 'canMegaEvo': False}, 'reserve': {
                'ninjask': {'id': 'ninjask', 'level': 84, 'hp': 0, 'maxhp': 240, 'ability': 'speedboost', 'item': None,
                            'baseStats': {'hp': 61, 'attack': 90, 'defense': 45, 'special-attack': 50,
                                          'special-defense': 50, 'speed': 160}, 'attack': 199, 'defense': 124,
                            'special-attack': 132, 'special-defense': 132, 'speed': 317, 'attack_boost': 0,
                            'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0,
                            'status': None, 'volatileStatus': [],
                            'moves': [{'id': 'nightslash', 'disabled': False, 'current_pp': 24},
                                      {'id': 'swordsdance', 'disabled': False, 'current_pp': 32},
                                      {'id': 'leechlife', 'disabled': False, 'current_pp': 16},
                                      {'id': 'aerialace', 'disabled': False, 'current_pp': 32}],
                            'types': ['bug', 'flying'], 'canMegaEvo': False},
                'mudsdale': {'id': 'mudsdale', 'level': 83, 'hp': 0, 'maxhp': 302, 'ability': 'stamina', 'item': None,
                             'baseStats': {'hp': 100, 'attack': 125, 'defense': 100, 'special-attack': 55,
                                           'special-defense': 85, 'speed': 35}, 'attack': 255, 'defense': 214,
                             'special-attack': 139, 'special-defense': 189, 'speed': 106, 'attack_boost': 0,
                             'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                             'speed_boost': 0, 'status': None, 'volatileStatus': [],
                             'moves': [{'id': 'closecombat', 'disabled': False, 'current_pp': 8},
                                       {'id': 'earthquake', 'disabled': False, 'current_pp': 16},
                                       {'id': 'stealthrock', 'disabled': False, 'current_pp': 32},
                                       {'id': 'heavyslam', 'disabled': False, 'current_pp': 16}], 'types': ['ground'],
                             'canMegaEvo': False},
                'terrakion': {'id': 'terrakion', 'level': 77, 'hp': 241, 'maxhp': 267, 'ability': 'justified',
                              'item': None, 'baseStats': {'hp': 91, 'attack': 129, 'defense': 90, 'special-attack': 72,
                                                          'special-defense': 90, 'speed': 108}, 'attack': 243,
                              'defense': 183, 'special-attack': 155, 'special-defense': 183, 'speed': 211,
                              'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0,
                              'special_defense_boost': 0, 'speed_boost': 0, 'status': 'par', 'volatileStatus': [],
                              'moves': [{'id': 'earthquake', 'disabled': False, 'current_pp': 16},
                                        {'id': 'stoneedge', 'disabled': False, 'current_pp': 8},
                                        {'id': 'swordsdance', 'disabled': False, 'current_pp': 32},
                                        {'id': 'closecombat', 'disabled': False, 'current_pp': 8}],
                              'types': ['rock', 'fighting'], 'canMegaEvo': False},
                'dhelmise': {'id': 'dhelmise', 'level': 81, 'hp': 246, 'maxhp': 246, 'ability': 'steelworker',
                             'item': None, 'baseStats': {'hp': 70, 'attack': 131, 'defense': 100, 'special-attack': 86,
                                                         'special-defense': 90, 'speed': 40}, 'attack': 259,
                             'defense': 209, 'special-attack': 186, 'special-defense': 192, 'speed': 111,
                             'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0,
                             'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [],
                             'moves': [{'id': 'rapidspin', 'disabled': False, 'current_pp': 64},
                                       {'id': 'anchorshot', 'disabled': False, 'current_pp': 32},
                                       {'id': 'earthquake', 'disabled': False, 'current_pp': 16},
                                       {'id': 'powerwhip', 'disabled': False, 'current_pp': 16}],
                             'types': ['ghost', 'grass'], 'canMegaEvo': False},
                'plusle': {'id': 'plusle', 'level': 84, 'hp': 238, 'maxhp': 238, 'ability': 'lightningrod',
                           'item': None, 'baseStats': {'hp': 60, 'attack': 50, 'defense': 40, 'special-attack': 85,
                                                       'special-defense': 75, 'speed': 95}, 'attack': 132,
                           'defense': 115, 'special-attack': 191, 'special-defense': 174, 'speed': 208,
                           'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                           'speed_boost': 0, 'status': None, 'volatileStatus': [],
                           'moves': [{'id': 'encore', 'disabled': False, 'current_pp': 8},
                                     {'id': 'hiddenpowerice60', 'disabled': False, 'current_pp': 24},
                                     {'id': 'nastyplot', 'disabled': False, 'current_pp': 32},
                                     {'id': 'thunderbolt', 'disabled': False, 'current_pp': 24}], 'types': ['electric'],
                           'canMegaEvo': False}},
                      'side_conditions': {'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0,
                                          'stealthrock': 1, 'spikes': 0, 'stickyweb': 0, 'toxicspikes': 0},
                      'trapped': False}, 'opponent': {
                'active': {'id': 'heatran', 'level': 75, 'hp': 213.2, 'maxhp': 260, 'ability': 'flashfire',
                           'item': None, 'baseStats': {'hp': 91, 'attack': 90, 'defense': 106, 'special-attack': 130,
                                                       'special-defense': 106, 'speed': 77}, 'attack': 179,
                           'defense': 203, 'special-attack': 239, 'special-defense': 203, 'speed': 159,
                           'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                           'speed_boost': 0, 'status': None, 'volatileStatus': ['flashfire'],
                           'moves': [{'id': 'stealthrock', 'disabled': False, 'current_pp': 32}],
                           'types': ['fire', 'steel'], 'canMegaEvo': False}, 'reserve': {
                    'victini': {'id': 'victini', 'level': 75, 'hp': 0, 'maxhp': 274, 'ability': 'victorystar',
                                'item': None,
                                'baseStats': {'hp': 100, 'attack': 100, 'defense': 100, 'special-attack': 100,
                                              'special-defense': 100, 'speed': 100}, 'attack': 194, 'defense': 194,
                                'special-attack': 194, 'special-defense': 194, 'speed': 194, 'attack_boost': 0,
                                'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                'moves': [{'id': 'grassknot', 'disabled': False, 'current_pp': 32}],
                                'types': ['psychic', 'fire'], 'canMegaEvo': False},
                    'porygon2': {'id': 'porygon2', 'level': 79, 'hp': 44.88, 'maxhp': 264, 'ability': 'download',
                                 'item': None,
                                 'baseStats': {'hp': 85, 'attack': 80, 'defense': 90, 'special-attack': 105,
                                               'special-defense': 95, 'speed': 60}, 'attack': 172, 'defense': 188,
                                 'special-attack': 211, 'special-defense': 196, 'speed': 140, 'attack_boost': 0,
                                 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                 'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                 'moves': [{'id': 'triattack', 'disabled': False, 'current_pp': 16},
                                           {'id': 'thunderwave', 'disabled': False, 'current_pp': 32}],
                                 'types': ['normal'], 'canMegaEvo': False},
                    'beautifly': {'id': 'beautifly', 'level': 84, 'hp': 238, 'maxhp': 238, 'ability': 'swarm',
                                  'item': None,
                                  'baseStats': {'hp': 60, 'attack': 70, 'defense': 50, 'special-attack': 100,
                                                'special-defense': 50, 'speed': 65}, 'attack': 166, 'defense': 132,
                                  'special-attack': 216, 'special-defense': 132, 'speed': 157, 'attack_boost': 0,
                                  'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                  'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [],
                                  'types': ['bug', 'flying'], 'canMegaEvo': False},
                    'carnivine': {'id': 'carnivine', 'level': 84, 'hp': 0, 'maxhp': 262, 'ability': 'levitate',
                                  'item': 'Leftovers',
                                  'baseStats': {'hp': 74, 'attack': 100, 'defense': 72, 'special-attack': 90,
                                                'special-defense': 72, 'speed': 46}, 'attack': 216, 'defense': 169,
                                  'special-attack': 199, 'special-defense': 169, 'speed': 125, 'attack_boost': 0,
                                  'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                  'speed_boost': 0, 'status': 'par', 'volatileStatus': [],
                                  'moves': [{'id': 'swordsdance', 'disabled': False, 'current_pp': 32},
                                            {'id': 'return', 'disabled': False, 'current_pp': 32}], 'types': ['grass'],
                                  'canMegaEvo': False},
                    'dusknoir': {'id': 'dusknoir', 'level': 84, 'hp': 0, 'maxhp': 213, 'ability': 'pressure',
                                 'item': 'Leftovers',
                                 'baseStats': {'hp': 45, 'attack': 100, 'defense': 135, 'special-attack': 65,
                                               'special-defense': 135, 'speed': 45}, 'attack': 216, 'defense': 275,
                                 'special-attack': 157, 'special-defense': 275, 'speed': 124, 'attack_boost': 0,
                                 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                 'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                 'moves': [{'id': 'substitute', 'disabled': False, 'current_pp': 16},
                                           {'id': 'shadowsneak', 'disabled': False, 'current_pp': 48}],
                                 'types': ['ghost'], 'canMegaEvo': False}},
                'side_conditions': {'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0, 'stealthrock': 0,
                                    'spikes': 0, 'stickyweb': 0, 'toxicspikes': 0}, 'trapped': False}, 'weather': None,
             'field': None, 'forceSwitch': False, 'wait': False, 'trickroom': False}
        )
        self.mutator.state = self.state

        bot_move = "willowisp"
        opponent_move = "splash"

        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_ground_immune_to_thunderwave(self):
        self.state = State.from_dict(
            {'self': {
                'active': {'id': 'aggronmega', 'level': 77, 'hp': 88, 'maxhp': 234, 'ability': 'filter', 'item': None,
                           'baseStats': {'hp': 70, 'attack': 140, 'defense': 230, 'special-attack': 60,
                                         'special-defense': 80, 'speed': 50}, 'attack': 260, 'defense': 399,
                           'special-attack': 137, 'special-defense': 168, 'speed': 122, 'attack_boost': 0,
                           'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0,
                           'status': None, 'volatileStatus': [],
                           'moves': [{'id': 'heavyslam', 'disabled': False, 'current_pp': 15},
                                     {'id': 'earthquake', 'disabled': False, 'current_pp': 16},
                                     {'id': 'thunderwave', 'disabled': False, 'current_pp': 32},
                                     {'id': 'roar', 'disabled': False, 'current_pp': 32}], 'types': ['steel'],
                           'canMegaEvo': False}, 'reserve': {
                    'corsola': {'id': 'corsola', 'level': 84, 'hp': 0, 'maxhp': 246, 'ability': 'naturalcure',
                                'item': None, 'baseStats': {'hp': 65, 'attack': 55, 'defense': 95, 'special-attack': 65,
                                                            'special-defense': 95, 'speed': 35}, 'attack': 141,
                                'defense': 208, 'special-attack': 157, 'special-defense': 208, 'speed': 107,
                                'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0,
                                'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                'moves': [{'id': 'stealthrock', 'disabled': False, 'current_pp': 32},
                                          {'id': 'toxic', 'disabled': False, 'current_pp': 16},
                                          {'id': 'scald', 'disabled': False, 'current_pp': 24},
                                          {'id': 'powergem', 'disabled': False, 'current_pp': 32}],
                                'types': ['water', 'rock'], 'canMegaEvo': False},
                    'excadrill': {'id': 'excadrill', 'level': 75, 'hp': 0, 'maxhp': 289, 'ability': 'moldbreaker',
                                  'item': None,
                                  'baseStats': {'hp': 110, 'attack': 135, 'defense': 60, 'special-attack': 50,
                                                'special-defense': 65, 'speed': 88}, 'attack': 246, 'defense': 134,
                                  'special-attack': 119, 'special-defense': 141, 'speed': 176, 'attack_boost': 0,
                                  'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                  'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                  'moves': [{'id': 'swordsdance', 'disabled': False, 'current_pp': 32},
                                            {'id': 'earthquake', 'disabled': False, 'current_pp': 16},
                                            {'id': 'rockslide', 'disabled': False, 'current_pp': 16},
                                            {'id': 'ironhead', 'disabled': False, 'current_pp': 24}],
                                  'types': ['ground', 'steel'], 'canMegaEvo': False},
                    'purugly': {'id': 'purugly', 'level': 84, 'hp': 256, 'maxhp': 256, 'ability': 'thickfat',
                                'item': None, 'baseStats': {'hp': 71, 'attack': 82, 'defense': 64, 'special-attack': 64,
                                                            'special-defense': 59, 'speed': 112}, 'attack': 186,
                                'defense': 156, 'special-attack': 156, 'special-defense': 147, 'speed': 236,
                                'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0,
                                'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                'moves': [{'id': 'fakeout', 'disabled': False, 'current_pp': 16},
                                          {'id': 'uturn', 'disabled': False, 'current_pp': 32},
                                          {'id': 'return', 'disabled': False, 'current_pp': 32},
                                          {'id': 'knockoff', 'disabled': False, 'current_pp': 32}], 'types': ['normal'],
                                'canMegaEvo': False},
                    'beedrill': {'id': 'beedrill', 'level': 84, 'hp': 246, 'maxhp': 246, 'ability': 'swarm',
                                 'item': None,
                                 'baseStats': {'hp': 65, 'attack': 90, 'defense': 40, 'special-attack': 45,
                                               'special-defense': 80, 'speed': 75}, 'attack': 199, 'defense': 115,
                                 'special-attack': 124, 'special-defense': 183, 'speed': 174, 'attack_boost': 0,
                                 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                 'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                 'moves': [{'id': 'uturn', 'disabled': False, 'current_pp': 32},
                                           {'id': 'toxicspikes', 'disabled': False, 'current_pp': 32},
                                           {'id': 'poisonjab', 'disabled': False, 'current_pp': 32},
                                           {'id': 'tailwind', 'disabled': False, 'current_pp': 24}],
                                 'types': ['bug', 'poison'], 'canMegaEvo': False},
                    'lurantis': {'id': 'lurantis', 'level': 83, 'hp': 0, 'maxhp': 252, 'ability': 'contrary',
                                 'item': None,
                                 'baseStats': {'hp': 70, 'attack': 105, 'defense': 90, 'special-attack': 80,
                                               'special-defense': 90, 'speed': 45}, 'attack': 222, 'defense': 197,
                                 'special-attack': 180, 'special-defense': 197, 'speed': 122, 'attack_boost': 0,
                                 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                 'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                 'moves': [{'id': 'superpower', 'disabled': False, 'current_pp': 8},
                                           {'id': 'synthesis', 'disabled': False, 'current_pp': 8},
                                           {'id': 'hiddenpowerice60', 'disabled': False, 'current_pp': 24},
                                           {'id': 'leafstorm', 'disabled': False, 'current_pp': 8}], 'types': ['grass'],
                                 'canMegaEvo': False}},
                'side_conditions': {'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0, 'stealthrock': 1,
                                    'spikes': 0, 'stickyweb': 0, 'toxicspikes': 0}, 'trapped': False}, 'opponent': {
                'active': {'id': 'mudsdale', 'level': 83, 'hp': 277.84000000000003, 'maxhp': 302, 'ability': 'stamina',
                           'item': None, 'baseStats': {'hp': 100, 'attack': 125, 'defense': 100, 'special-attack': 55,
                                                       'special-defense': 85, 'speed': 35}, 'attack': 255,
                           'defense': 214, 'special-attack': 139, 'special-defense': 189, 'speed': 106,
                           'attack_boost': 0, 'defense_boost': 2, 'special_attack_boost': 0, 'special_defense_boost': 0,
                           'speed_boost': 0, 'status': None, 'volatileStatus': [],
                           'moves': [{'id': 'earthquake', 'disabled': False, 'current_pp': 16}], 'types': ['ground'],
                           'canMegaEvo': False}, 'reserve': {
                    'dragonite': {'id': 'dragonite', 'level': 76, 'hp': 170.95000000000002, 'maxhp': 263,
                                  'ability': 'multiscale', 'item': None,
                                  'baseStats': {'hp': 91, 'attack': 134, 'defense': 95, 'special-attack': 100,
                                                'special-defense': 100, 'speed': 80}, 'attack': 248, 'defense': 188,
                                  'special-attack': 196, 'special-defense': 196, 'speed': 166, 'attack_boost': 0,
                                  'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                  'speed_boost': 0, 'status': None, 'volatileStatus': [], 'moves': [],
                                  'types': ['dragon', 'flying'], 'canMegaEvo': False},
                    'volcanion': {'id': 'volcanion', 'level': 77, 'hp': 0, 'maxhp': 250, 'ability': 'waterabsorb',
                                  'item': 'Leftovers',
                                  'baseStats': {'hp': 80, 'attack': 110, 'defense': 120, 'special-attack': 130,
                                                'special-defense': 90, 'speed': 70}, 'attack': 214, 'defense': 229,
                                  'special-attack': 245, 'special-defense': 183, 'speed': 152, 'attack_boost': 0,
                                  'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                  'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                  'moves': [{'id': 'substitute', 'disabled': False, 'current_pp': 16},
                                            {'id': 'steameruption', 'disabled': False, 'current_pp': 8},
                                            {'id': 'fireblast', 'disabled': False, 'current_pp': 8}],
                                  'types': ['fire', 'water'], 'canMegaEvo': False},
                    'wormadamsandy': {'id': 'wormadamsandy', 'level': 84, 'hp': 135.66, 'maxhp': 238,
                                      'ability': 'overcoat', 'item': 'Leftovers',
                                      'baseStats': {'hp': 60, 'attack': 79, 'defense': 105, 'special-attack': 59,
                                                    'special-defense': 85, 'speed': 36}, 'attack': 181, 'defense': 225,
                                      'special-attack': 147, 'special-defense': 191, 'speed': 109, 'attack_boost': 0,
                                      'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                      'speed_boost': 0, 'status': 'tox', 'volatileStatus': [],
                                      'moves': [{'id': 'stealthrock', 'disabled': False, 'current_pp': 32},
                                                {'id': 'protect', 'disabled': False, 'current_pp': 16},
                                                {'id': 'toxic', 'disabled': False, 'current_pp': 16}],
                                      'types': ['bug', 'ground'], 'canMegaEvo': False},
                    'illumise': {'id': 'illumise', 'level': 84, 'hp': 24.6, 'maxhp': 246, 'ability': 'prankster',
                                 'item': 'Leftovers',
                                 'baseStats': {'hp': 65, 'attack': 47, 'defense': 75, 'special-attack': 73,
                                               'special-defense': 85, 'speed': 85}, 'attack': 127, 'defense': 174,
                                 'special-attack': 171, 'special-defense': 191, 'speed': 191, 'attack_boost': 0,
                                 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                 'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                 'moves': [{'id': 'wish', 'disabled': False, 'current_pp': 16}], 'types': ['bug'],
                                 'canMegaEvo': False}},
                'side_conditions': {'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0, 'toxicspikes': 0,
                                    'stealthrock': 0, 'spikes': 0, 'stickyweb': 0, 'Wish': 0}, 'trapped': False},
             'weather': None, 'field': None, 'forceSwitch': False, 'wait': False, 'trickroom': False}
        )
        self.mutator.state = self.state

        bot_move = "thunderwave"
        opponent_move = "splash"

        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)

    def test_dryskin_from_hydropump(self):
        self.state = State.from_dict(
            {'self': {'active': {'id': 'blastoisemega', 'level': 79, 'hp': 133, 'maxhp': 254, 'ability': 'megalauncher',
                                 'item': None,
                                 'baseStats': {'hp': 79, 'attack': 103, 'defense': 120, 'special-attack': 135,
                                               'special-defense': 115, 'speed': 78}, 'attack': 208, 'defense': 235,
                                 'special-attack': 259, 'special-defense': 227, 'speed': 169, 'attack_boost': 0,
                                 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                 'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                 'moves': [{'id': 'dragontail', 'disabled': False, 'current_pp': 15},
                                           {'id': 'rapidspin', 'disabled': False, 'current_pp': 64},
                                           {'id': 'aurasphere', 'disabled': False, 'current_pp': 32},
                                           {'id': 'hydropump', 'disabled': False, 'current_pp': 7}], 'types': ['water'],
                                 'canMegaEvo': False}, 'reserve': {
                'florges': {'id': 'florges', 'level': 79, 'hp': 0, 'maxhp': 253, 'ability': 'flowerveil', 'item': None,
                            'baseStats': {'hp': 78, 'attack': 65, 'defense': 68, 'special-attack': 112,
                                          'special-defense': 154, 'speed': 75}, 'attack': 148, 'defense': 153,
                            'special-attack': 223, 'special-defense': 289, 'speed': 164, 'attack_boost': 0,
                            'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0,
                            'status': None, 'volatileStatus': [],
                            'moves': [{'id': 'moonblast', 'disabled': False, 'current_pp': 24},
                                      {'id': 'wish', 'disabled': False, 'current_pp': 16},
                                      {'id': 'toxic', 'disabled': False, 'current_pp': 16},
                                      {'id': 'protect', 'disabled': False, 'current_pp': 16}], 'types': ['fairy'],
                            'canMegaEvo': False},
                'smeargle': {'id': 'smeargle', 'level': 84, 'hp': 230, 'maxhp': 230, 'ability': 'owntempo',
                             'item': None, 'baseStats': {'hp': 55, 'attack': 20, 'defense': 35, 'special-attack': 20,
                                                         'special-defense': 45, 'speed': 75}, 'attack': 82,
                             'defense': 107, 'special-attack': 82, 'special-defense': 124, 'speed': 174,
                             'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0,
                             'special_defense_boost': 0, 'speed_boost': 0, 'status': None, 'volatileStatus': [],
                             'moves': [{'id': 'stealthrock', 'disabled': False, 'current_pp': 32},
                                       {'id': 'destinybond', 'disabled': False, 'current_pp': 8},
                                       {'id': 'stickyweb', 'disabled': False, 'current_pp': 32},
                                       {'id': 'spore', 'disabled': False, 'current_pp': 24}], 'types': ['normal'],
                             'canMegaEvo': False},
                'crabominable': {'id': 'crabominable', 'level': 84, 'hp': 0, 'maxhp': 300, 'ability': 'ironfist',
                                 'item': None,
                                 'baseStats': {'hp': 97, 'attack': 132, 'defense': 77, 'special-attack': 62,
                                               'special-defense': 67, 'speed': 43}, 'attack': 270, 'defense': 178,
                                 'special-attack': 152, 'special-defense': 161, 'speed': 120, 'attack_boost': 0,
                                 'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                 'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                 'moves': [{'id': 'earthquake', 'disabled': False, 'current_pp': 16},
                                           {'id': 'closecombat', 'disabled': False, 'current_pp': 8},
                                           {'id': 'stoneedge', 'disabled': False, 'current_pp': 8},
                                           {'id': 'icehammer', 'disabled': False, 'current_pp': 16}],
                                 'types': ['fighting', 'ice'], 'canMegaEvo': False},
                'haxorus': {'id': 'haxorus', 'level': 77, 'hp': 0, 'maxhp': 244, 'ability': 'moldbreaker', 'item': None,
                            'baseStats': {'hp': 76, 'attack': 147, 'defense': 90, 'special-attack': 60,
                                          'special-defense': 70, 'speed': 97}, 'attack': 271, 'defense': 183,
                            'special-attack': 137, 'special-defense': 152, 'speed': 194, 'attack_boost': 0,
                            'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0,
                            'status': None, 'volatileStatus': [],
                            'moves': [{'id': 'swordsdance', 'disabled': False, 'current_pp': 32},
                                      {'id': 'earthquake', 'disabled': False, 'current_pp': 16},
                                      {'id': 'poisonjab', 'disabled': False, 'current_pp': 32},
                                      {'id': 'outrage', 'disabled': False, 'current_pp': 16}], 'types': ['dragon'],
                            'canMegaEvo': False},
                'dewgong': {'id': 'dewgong', 'level': 84, 'hp': 0, 'maxhp': 288, 'ability': 'thickfat', 'item': None,
                            'baseStats': {'hp': 90, 'attack': 70, 'defense': 80, 'special-attack': 70,
                                          'special-defense': 95, 'speed': 70}, 'attack': 166, 'defense': 183,
                            'special-attack': 166, 'special-defense': 208, 'speed': 166, 'attack_boost': 0,
                            'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0,
                            'status': None, 'volatileStatus': [],
                            'moves': [{'id': 'icebeam', 'disabled': False, 'current_pp': 16},
                                      {'id': 'toxic', 'disabled': False, 'current_pp': 16},
                                      {'id': 'surf', 'disabled': False, 'current_pp': 24},
                                      {'id': 'protect', 'disabled': False, 'current_pp': 16}],
                            'types': ['water', 'ice'], 'canMegaEvo': False}},
                      'side_conditions': {'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0,
                                          'stealthrock': 0, 'Wish': 0, 'spikes': 0, 'stickyweb': 0, 'toxicspikes': 0},
                      'trapped': False}, 'opponent': {
                'active': {'id': 'toxicroak', 'level': 79, 'hp': 261, 'maxhp': 261, 'ability': 'dryskin', 'item': None,
                           'baseStats': {'hp': 83, 'attack': 106, 'defense': 65, 'special-attack': 86,
                                         'special-defense': 65, 'speed': 85}, 'attack': 213, 'defense': 148,
                           'special-attack': 181, 'special-defense': 148, 'speed': 180, 'attack_boost': 0,
                           'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0, 'speed_boost': 0,
                           'status': None, 'volatileStatus': [],
                           'moves': [{'id': 'gunkshot', 'disabled': False, 'current_pp': 8}],
                           'types': ['poison', 'fighting'], 'canMegaEvo': False}, 'reserve': {
                    'dugtrio': {'id': 'dugtrio', 'level': 77, 'hp': 0, 'maxhp': 180, 'ability': 'sandforce',
                                'item': None,
                                'baseStats': {'hp': 35, 'attack': 100, 'defense': 50, 'special-attack': 50,
                                              'special-defense': 70, 'speed': 120}, 'attack': 199, 'defense': 122,
                                'special-attack': 122, 'special-defense': 152, 'speed': 229, 'attack_boost': 0,
                                'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                'moves': [{'id': 'earthquake', 'disabled': False, 'current_pp': 16}],
                                'types': ['ground'], 'canMegaEvo': False},
                    'kyuremwhite': {'id': 'kyuremwhite', 'level': 73, 'hp': 0, 'maxhp': 303, 'ability': 'turboblaze',
                                    'item': None,
                                    'baseStats': {'hp': 125, 'attack': 120, 'defense': 90, 'special-attack': 170,
                                                  'special-defense': 100, 'speed': 95}, 'attack': 218, 'defense': 174,
                                    'special-attack': 291, 'special-defense': 188, 'speed': 181, 'attack_boost': 0,
                                    'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                    'speed_boost': 0, 'status': 'tox', 'volatileStatus': [],
                                    'moves': [{'id': 'focusblast', 'disabled': False, 'current_pp': 8}],
                                    'types': ['dragon', 'ice'], 'canMegaEvo': False},
                    'amoonguss': {'id': 'amoonguss', 'level': 77, 'hp': 0, 'maxhp': 302, 'ability': 'regenerator',
                                  'item': 'Black Sludge',
                                  'baseStats': {'hp': 114, 'attack': 85, 'defense': 70, 'special-attack': 85,
                                                'special-defense': 80, 'speed': 30}, 'attack': 175, 'defense': 152,
                                  'special-attack': 175, 'special-defense': 168, 'speed': 91, 'attack_boost': 0,
                                  'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                  'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                  'moves': [{'id': 'sludgebomb', 'disabled': False, 'current_pp': 16}],
                                  'types': ['grass', 'poison'], 'canMegaEvo': False},
                    'bellossom': {'id': 'bellossom', 'level': 84, 'hp': 0, 'maxhp': 263, 'ability': 'chlorophyll',
                                  'item': 'Life Orb',
                                  'baseStats': {'hp': 75, 'attack': 80, 'defense': 95, 'special-attack': 90,
                                                'special-defense': 100, 'speed': 50}, 'attack': 183, 'defense': 208,
                                  'special-attack': 199, 'special-defense': 216, 'speed': 132, 'attack_boost': 0,
                                  'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                  'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                  'moves': [{'id': 'moonblast', 'disabled': False, 'current_pp': 24}],
                                  'types': ['grass'], 'canMegaEvo': False},
                    'hoopaunbound': {'id': 'hoopaunbound', 'level': 76, 'hp': 138.32000000000002, 'maxhp': 247,
                                     'ability': 'magician', 'item': 'Life Orb',
                                     'baseStats': {'hp': 80, 'attack': 160, 'defense': 60, 'special-attack': 170,
                                                   'special-defense': 130, 'speed': 80}, 'attack': 287, 'defense': 135,
                                     'special-attack': 302, 'special-defense': 242, 'speed': 166, 'attack_boost': 0,
                                     'defense_boost': 0, 'special_attack_boost': 0, 'special_defense_boost': 0,
                                     'speed_boost': 0, 'status': None, 'volatileStatus': [],
                                     'moves': [{'id': 'focusblast', 'disabled': False, 'current_pp': 8},
                                               {'id': 'psyshock', 'disabled': False, 'current_pp': 16}],
                                     'types': ['psychic', 'dark'], 'canMegaEvo': False}},
                'side_conditions': {'tailwind': 0, 'reflect': 0, 'lightscreen': 0, 'auroraveil': 0, 'stealthrock': 0,
                                    'stickyweb': 0, 'spikes': 0, 'toxicspikes': 0}, 'trapped': False}, 'weather': None,
             'field': None, 'forceSwitch': False, 'wait': False, 'trickroom': False}
        )
        self.mutator.state = self.state

        self.state.opponent.active.hp = self.state.opponent.active.maxhp - 1

        bot_move = "hydropump"
        opponent_move = "splash"

        instructions = get_all_state_instructions(self.mutator, bot_move, opponent_move)
        expected_instructions = [
            TransposeInstruction(
                1.0,
                [
                    (constants.HEAL, constants.OPPONENT, 1)
                ],
                False
            )
        ]

        self.assertEqual(expected_instructions, instructions)


class TestUserMovesFirst(unittest.TestCase):
    def setUp(self):
        self.state = State(
                        Side(
                            Pokemon.from_state_pokemon_dict(StatePokemon("raichu", 73).to_dict()),
                            {
                                "xatu": Pokemon.from_state_pokemon_dict(StatePokemon("xatu", 81).to_dict()),
                                "starmie": Pokemon.from_state_pokemon_dict(StatePokemon("starmie", 81).to_dict()),
                                "gyarados": Pokemon.from_state_pokemon_dict(StatePokemon("gyarados", 81).to_dict()),
                                "dragonite": Pokemon.from_state_pokemon_dict(StatePokemon("dragonite", 81).to_dict()),
                                "hitmonlee": Pokemon.from_state_pokemon_dict(StatePokemon("hitmonlee", 81).to_dict()),
                            },
                            defaultdict(lambda: 0),
                            False
                        ),
                        Side(
                            Pokemon.from_state_pokemon_dict(StatePokemon("aromatisse", 81).to_dict()),
                            {
                                "yveltal": Pokemon.from_state_pokemon_dict(StatePokemon("yveltal", 73).to_dict()),
                                "slurpuff": Pokemon.from_state_pokemon_dict(StatePokemon("slurpuff", 73).to_dict()),
                                "victini": Pokemon.from_state_pokemon_dict(StatePokemon("victini", 73).to_dict()),
                                "toxapex": Pokemon.from_state_pokemon_dict(StatePokemon("toxapex", 73).to_dict()),
                                "bronzong": Pokemon.from_state_pokemon_dict(StatePokemon("bronzong", 73).to_dict()),
                            },
                            defaultdict(lambda: 0),
                            False
                        ),
                        None,
                        None,
                        False,
                        False,
                        False
                    )

        self.mutator = StateMutator(self.state)

    def test_bot_moves_first_when_move_priorities_are_the_same_and_it_is_faster(self):
        user = self.state.self
        opponent = self.state.opponent
        user_move = lookup_move('tackle')
        opponent_move = lookup_move('tackle')

        user.active.speed = 2
        opponent.active.speed = 1

        self.assertTrue(user_moves_first(self.state, user_move, opponent_move))

    def test_paralysis_reduces_speed_by_half(self):
        user = self.state.self
        opponent = self.state.opponent
        user_move = lookup_move('tackle')
        opponent_move = lookup_move('tackle')

        user.active.status = constants.PARALYZED

        user.active.speed = 10
        opponent.active.speed = 7

        self.assertFalse(user_moves_first(self.state, user_move, opponent_move))

    def test_opponent_moves_first_when_move_priorities_are_the_same_and_it_is_faster(self):
        user = self.state.self
        opponent = self.state.opponent
        user_move = lookup_move('tackle')
        opponent_move = lookup_move('tackle')

        user.active.speed = 1
        opponent.active.speed = 2

        self.assertFalse(user_moves_first(self.state, user_move, opponent_move))

    def test_priority_causes_slower_to_move_first(self):
        user = self.state.self
        opponent = self.state.opponent
        user_move = lookup_move('quickattack')
        opponent_move = lookup_move('tackle')

        user.active.speed = 1
        opponent.active.speed = 2

        self.assertTrue(user_moves_first(self.state, user_move, opponent_move))

    def test_both_using_priority_causes_faster_to_move_first(self):
        user = self.state.self
        opponent = self.state.opponent
        user_move = lookup_move('quickattack')
        opponent_move = lookup_move('quickattack')

        user.active.speed = 1
        opponent.active.speed = 2

        self.assertFalse(user_moves_first(self.state, user_move, opponent_move))

    def test_choice_scarf_causes_a_difference_in_effective_speed(self):
        user = self.state.self
        opponent = self.state.opponent
        user_move = lookup_move('tackle')
        opponent_move = lookup_move('tackle')

        user.active.item = 'choicescarf'
        user.active.speed = 5
        opponent.active.speed = 6

        self.assertTrue(user_moves_first(self.state, user_move, opponent_move))

    def test_tailwind_doubling_speed(self):
        user = self.state.self
        opponent = self.state.opponent
        user_move = lookup_move('tackle')
        opponent_move = lookup_move('tackle')

        user.side_conditions[constants.TAILWIND] = 1
        user.active.speed = 51
        opponent.active.speed = 100

        self.assertTrue(user_moves_first(self.state, user_move, opponent_move))

    def test_tailwind_at_0_does_not_boost(self):
        user = self.state.self
        opponent = self.state.opponent
        user_move = lookup_move('tackle')
        opponent_move = lookup_move('tackle')

        user.side_conditions[constants.TAILWIND] = 0
        user.active.speed = 51
        opponent.active.speed = 100

        self.assertFalse(user_moves_first(self.state, user_move, opponent_move))

    def test_switch_always_moves_first(self):
        user = self.state.self
        opponent = self.state.opponent
        user_move = "{} x".format(constants.SWITCH_STRING)
        opponent_move = lookup_move('quickattack')

        user.active.speed = 1
        opponent.active.speed = 2

        self.assertTrue(user_moves_first(self.state, user_move, opponent_move))

    def test_double_switch_results_in_faster_moving_first(self):
        user = self.state.self
        opponent = self.state.opponent
        user_move = "{} x".format(constants.SWITCH_STRING)
        opponent_move = "{} x".format(constants.SWITCH_STRING)

        user.active.speed = 1
        opponent.active.speed = 2

        self.assertFalse(user_moves_first(self.state, user_move, opponent_move))

    def test_prankster_results_in_status_move_going_first(self):
        user = self.state.self
        opponent = self.state.opponent
        user_move = lookup_move('willowisp')
        opponent_move = lookup_move('tackle')

        user.active.speed = 1
        opponent.active.speed = 2
        user.active.ability = 'prankster'

        self.assertTrue(user_moves_first(self.state, user_move, opponent_move))

    def test_quickattack_still_goes_first_when_user_has_prankster(self):
        user = self.state.self
        opponent = self.state.opponent
        user_move = lookup_move('willowisp')
        opponent_move = lookup_move('quickattack')

        user.active.speed = 1
        opponent.active.speed = 2
        user.active.ability = 'prankster'

        self.assertFalse(user_moves_first(self.state, user_move, opponent_move))

    def test_prankster_does_not_result_in_tackle_going_first(self):
        user = self.state.self
        opponent = self.state.opponent
        user_move = lookup_move('tackle')
        opponent_move = lookup_move('tackle')

        user.active.speed = 1
        opponent.active.speed = 2
        user.active.ability = 'prankster'

        self.assertFalse(user_moves_first(self.state, user_move, opponent_move))

    def test_trickroom_results_in_slower_pokemon_going_first(self):
        user = self.state.self
        opponent = self.state.opponent
        user_move = lookup_move('tackle')
        opponent_move = lookup_move('tackle')

        self.state.trick_room = True
        user.active.speed = 1
        opponent.active.speed = 2

        self.assertTrue(user_moves_first(self.state, user_move, opponent_move))

    def test_priority_move_goes_first_in_trickroom(self):
        user = self.state.self
        opponent = self.state.opponent
        user_move = lookup_move('tackle')
        opponent_move = lookup_move('quickattack')

        self.state.field = 'trickroom'
        user.active.speed = 1
        opponent.active.speed = 2

        self.assertFalse(user_moves_first(self.state, user_move, opponent_move))
