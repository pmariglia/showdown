import unittest
from collections import defaultdict

import constants
from showdown.engine.objects import State
from showdown.engine.objects import Side
from showdown.engine.objects import Pokemon
from showdown.battle import Pokemon as StatePokemon


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
                            (0, 0),
                            defaultdict(lambda: 0),
                (0, 0)
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
                            (0, 0),
                            defaultdict(lambda: 0),
                (0, 0)
                        ),
                        None,
                        None,
                        False
                    )

        self.state.user.active.moves = [
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
        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)

    def test_partiallytrapped_removes_switch_options_for_bot(self):
        self.state.user.active.volatile_status.add(constants.PARTIALLY_TRAPPED)
        expected_options = (
            [
                'tackle',
                'charm',
                'growl',
                'stringshot'
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
        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)

    def test_partiallytrapped_removes_switch_options_for_opponent(self):
        self.state.opponent.active.volatile_status.add(constants.PARTIALLY_TRAPPED)
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
                'stringshot'
            ]
        )
        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)

    def test_bot_with_shadowtag_prevents_switch_options_for_opponent(self):
        self.state.user.active.ability = 'shadowtag'
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
                'stringshot'
            ]
        )
        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)

    def test_opponent_with_shadowtag_prevents_switch_options(self):
        self.state.opponent.active.ability = 'shadowtag'
        expected_options = (
            [
                'tackle',
                'charm',
                'growl',
                'stringshot'
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
        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)

    def test_ghost_type_can_switch_out_versus_shadow_tag(self):
        self.state.opponent.active.ability = 'shadowtag'
        self.state.user.active.types = ['ghost']
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
        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)

    def test_non_steel_can_switch_out_versus_magnetpull(self):
        self.state.opponent.active.ability = 'magnetpull'
        self.state.user.active.types = ['ghost']
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
        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)

    def test_self_pokemon_with_phantomforce_volatilestatus_must_use_phantomforce(self):
        self.state.user.active.moves = [
            {constants.ID: 'phantomforce', constants.DISABLED: False},
            {constants.ID: 'charm', constants.DISABLED: False},
            {constants.ID: 'growl', constants.DISABLED: False},
            {constants.ID: 'stringshot', constants.DISABLED: False},
        ]
        self.state.user.active.volatile_status = ("phantomforce",)
        expected_options = (
            [
                'phantomforce'
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
        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)

    def test_opponent_pokemon_with_phantomforce_volatilestatus_must_use_phantomforce(self):
        self.state.user.active.moves = [
            {constants.ID: 'tackle', constants.DISABLED: False},
            {constants.ID: 'charm', constants.DISABLED: False},
            {constants.ID: 'growl', constants.DISABLED: False},
            {constants.ID: 'stringshot', constants.DISABLED: False},
        ]
        self.state.opponent.active.moves = [
            {constants.ID: 'phantomforce', constants.DISABLED: False},
            {constants.ID: 'charm', constants.DISABLED: False},
            {constants.ID: 'growl', constants.DISABLED: False},
            {constants.ID: 'stringshot', constants.DISABLED: False},
        ]
        self.state.opponent.active.volatile_status = ("phantomforce",)
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
                'phantomforce'
            ]
        )
        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)

    def test_shedshell_can_always_switch(self):
        self.state.opponent.active.ability = 'shadowtag'
        self.state.user.active.item = 'shedshell'
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
        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)

    def test_bot_can_switch_as_flying_type_versus_arenatrap(self):
        self.state.opponent.active.ability = 'arenatrap'
        self.state.user.active.types = ['flying']
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
        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)

    def test_airballoon_allows_holder_to_switch(self):
        self.state.opponent.active.ability = 'arenatrap'
        self.state.user.active.types = ['normal']
        self.state.user.active.item = 'airballoon'
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
        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)

    def test_arenatrap_traps_non_grounded(self):
        self.state.opponent.active.ability = 'arenatrap'
        expected_options = (
            [
                'tackle',
                'charm',
                'growl',
                'stringshot'
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
        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)

    def test_steel_type_cannot_switch_out_versus_magnetpull(self):
        self.state.opponent.active.ability = 'magnetpull'
        self.state.user.active.types = ['steel']
        expected_options = (
            [
                'tackle',
                'charm',
                'growl',
                'stringshot'
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
        options = self.state.get_all_options()

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
        self.state.user.active.hp = 0

        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)

    def test_returns_nothing_for_user_when_opponent_active_is_dead(self):
        self.state.opponent.active.hp = 0
        expected_user_options = [
            constants.DO_NOTHING_MOVE
        ]

        options = self.state.get_all_options()

        self.assertEqual(expected_user_options, options[0])

    def test_double_faint_returns_correct_decisions(self):
        self.state.user.active.hp = 0
        self.state.opponent.active.hp = 0
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

        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)

    def test_double_faint_with_no_reserve_pokemon_returns_correct_decisions(self):
        self.state.user.active.hp = 0
        self.state.opponent.active.hp = 0

        for mon in self.state.user.reserve.values():
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

        options = self.state.get_all_options()

        self.assertEqual(expected_options, options)
