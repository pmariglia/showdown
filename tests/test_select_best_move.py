import unittest
from collections import defaultdict

import constants
from showdown.engine.objects import StateMutator
from showdown.engine.objects import State
from showdown.engine.objects import Side
from showdown.engine.objects import Pokemon
from showdown.battle import Pokemon as StatePokemon
from showdown.engine.select_best_move import get_all_options


class TestGetAllOptions(unittest.TestCase):
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

        self.state.self.active.moves = [
            {constants.ID: 'tackle', constants.DISABLED: False},
            {constants.ID: 'charm', constants.DISABLED: False},
            {constants.ID: 'growl', constants.DISABLED: False},
            {constants.ID: 'stringshot', constants.DISABLED: False},
        ]
        self.state.opponent.active.moves = [
            {constants.ID: 'tackle', constants.DISABLED: False},
            {constants.ID: 'charm', constants.DISABLED: False},
            {constants.ID: 'growl', constants.DISABLED: False},
            {constants.ID: 'stringshot', constants.DISABLED: False},
        ]

    def test_returns_all_options_in_normal_situation(self):
        expected_options = (
            [
                'tackle',
                'charm',
                'growl',
                'stringshot',
                'switch xatu',
                'switch starmie',
                'switch gyarados',
                'switch dragonite',
                'switch hitmonlee'
            ],
            [
                'tackle',
                'charm',
                'growl',
                'stringshot',
                'switch yveltal',
                'switch slurpuff',
                'switch victini',
                'switch toxapex',
                'switch bronzong'
            ]
        )
        options = get_all_options(self.state)

        self.assertEqual(expected_options, options)

    def test_returns_only_switches_for_user_and_nothing_for_opponent_when_user_active_is_dead(self):
        expected_options = (
            [
                'switch xatu',
                'switch starmie',
                'switch gyarados',
                'switch dragonite',
                'switch hitmonlee'
            ],
            [
                constants.DO_NOTHING_MOVE
            ]
        )
        self.state.self.active.hp = 0

        options = get_all_options(self.state)

        self.assertEqual(expected_options, options)

    def test_returns_nothing_for_user_when_wait_is_active(self):
        self.state.wait = True
        expected_user_options = [
            constants.DO_NOTHING_MOVE
        ]

        options = get_all_options(self.state)

        self.assertEqual(expected_user_options, options[0])

    def test_double_faint_returns_correct_decisions(self):
        self.state.self.active.hp = 0
        self.state.opponent.active.hp = 0
        self.state.force_switch = True
        expected_options = (
            [
                'switch xatu',
                'switch starmie',
                'switch gyarados',
                'switch dragonite',
                'switch hitmonlee'
            ],
            [
                'switch yveltal',
                'switch slurpuff',
                'switch victini',
                'switch toxapex',
                'switch bronzong'
            ],
        )

        options = get_all_options(self.state)

        self.assertEqual(expected_options, options)

    def test_double_faint_with_no_reserve_pokemon_returns_correct_decisions(self):
        self.state.self.active.hp = 0
        self.state.opponent.active.hp = 0
        self.state.force_switch = True

        for mon in self.state.self.reserve.values():
            mon.hp = 0

        expected_options = (
            [
                constants.DO_NOTHING_MOVE
            ],
            [
                'switch yveltal',
                'switch slurpuff',
                'switch victini',
                'switch toxapex',
                'switch bronzong'
            ],
        )

        options = get_all_options(self.state)

        self.assertEqual(expected_options, options)
