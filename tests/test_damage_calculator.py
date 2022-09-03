import unittest
from collections import defaultdict

import constants
from showdown.engine.damage_calculator import _calculate_damage
from showdown.engine.damage_calculator import calculate_damage
from showdown.engine.objects import State
from showdown.engine.objects import Side
from showdown.engine.objects import Pokemon

from showdown.battle import Pokemon as StatePokemon


class TestCalculateDamageAmount(unittest.TestCase):
    def setUp(self):
        self.charizard = Pokemon.from_state_pokemon_dict(StatePokemon("charizard", 100).to_dict())
        self.venusaur = Pokemon.from_state_pokemon_dict(StatePokemon("venusaur", 100).to_dict())

    def test_fire_blast_from_charizard_to_venusaur_without_modifiers(self):
        move = 'fireblast'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, calc_type='max')
        self.assertEqual([300], dmg)

    def test_flashfire_increases_fire_move_damage(self):
        move = 'fireblast'
        self.charizard.volatile_status.add('flashfire')

        dmg = _calculate_damage(self.charizard, self.venusaur, move, calc_type='max')
        self.assertEqual([450], dmg)

    def test_stab_without_weakness_calculates_properly(self):
        move = 'sludgebomb'

        dmg = _calculate_damage(self.venusaur, self.charizard, move, calc_type='max')
        self.assertEqual([130], dmg)

    def test_4x_weakness_calculates_properly(self):
        move = 'rockslide'

        dmg = _calculate_damage(self.venusaur, self.charizard, move, calc_type='max')
        self.assertEqual([268], dmg)

    def test_4x_resistance_calculates_properly(self):
        move = 'gigadrain'

        dmg = _calculate_damage(self.venusaur, self.charizard, move, calc_type='max')
        self.assertEqual([27], dmg)

    def test_immunity_calculates_properly(self):
        move = 'earthquake'

        dmg = _calculate_damage(self.venusaur, self.charizard, move, calc_type='max')
        self.assertEqual([0], dmg)

    def test_burn_modifier_properly_halves_physical_damage(self):
        move = 'rockslide'

        self.venusaur.status = constants.BURN

        dmg = _calculate_damage(self.venusaur, self.charizard, move, calc_type='max')
        self.assertEqual([134], dmg)

    def test_burn_does_not_modify_special_move(self):
        move = 'fireblast'

        self.venusaur.status  = constants.BURN

        dmg = _calculate_damage(self.charizard, self.venusaur, move, calc_type='max')
        self.assertEqual([300], dmg)

    def test_sun_stab_and_2x_weakness(self):

        conditions = {
            'weather': constants.SUN
        }

        move = 'fireblast'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, conditions, calc_type='max')
        self.assertEqual([450], dmg)

    def test_sun_weakens_water_moves(self):

        conditions = {
            'weather': constants.SUN
        }

        move = 'surf'

        dmg = _calculate_damage(self.venusaur, self.charizard, move, conditions, calc_type='max')
        self.assertEqual([87], dmg)

    def test_sand_increases_rock_spdef(self):

        self.venusaur.types = ['rock']

        conditions = {
            'weather': constants.SAND
        }

        move = 'fireblast'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, conditions, calc_type='max')
        self.assertEqual([51], dmg)

    def test_sand_does_not_double_ground_spdef(self):

        self.venusaur.types = ['water']

        conditions = {
            'weather': constants.SAND
        }

        move = 'fireblast'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, conditions, calc_type='max')
        self.assertEqual([75], dmg)

    def test_electric_terrain_increases_electric_damage_for_grounded_pokemon(self):
        self.charizard.types = ['fire']

        conditions = {
            constants.TERRAIN: constants.ELECTRIC_TERRAIN
        }

        move = 'thunderbolt'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, conditions, calc_type='max')

        # normally this is 41
        self.assertEqual([53], dmg)

    def test_psychic_terrain_increases_psychic_damage(self):
        self.charizard.types = ['fire']

        conditions = {
            constants.TERRAIN: constants.PSYCHIC_TERRAIN
        }

        move = 'psychic'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, conditions, calc_type='max')

        # normally this is 164
        self.assertEqual([213], dmg)

    def test_damage_is_not_increased_if_attacker_is_not_grounded(self):
        self.charizard.types = ['fire', 'flying']

        conditions = {
            constants.TERRAIN: constants.PSYCHIC_TERRAIN
        }

        move = 'psychic'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, conditions, calc_type='max')

        self.assertEqual([164], dmg)

    def test_grassy_terrain_increases_grass_type_move(self):
        self.charizard.types = ['fire']

        conditions = {
            constants.TERRAIN: constants.GRASSY_TERRAIN
        }

        move = 'gigadrain'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, conditions, calc_type='max')

        # normally this is 17
        self.assertEqual([22], dmg)

    def test_misty_terrain_halves_dragon_moves(self):
        self.charizard.types = ['fire']

        conditions = {
            constants.TERRAIN: constants.MISTY_TERRAIN
        }

        move = 'outrage'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, conditions, calc_type='max')

        # normally this is 103
        self.assertEqual([51], dmg)

    def test_psychic_terrain_makes_priority_move_do_nothing(self):
        self.charizard.types = ['fire']

        conditions = {
            constants.TERRAIN: constants.PSYCHIC_TERRAIN
        }

        move = 'machpunch'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, conditions, calc_type='max')

        self.assertEqual([0], dmg)

    def test_psychic_terrain_does_not_affect_priority_on_non_grounded(self):
        conditions = {
            constants.TERRAIN: constants.PSYCHIC_TERRAIN
        }

        move = 'machpunch'

        dmg = _calculate_damage(self.venusaur, self.charizard, move, conditions, calc_type='max')

        self.assertNotEqual([0], dmg)

    def test_rain_properly_amplifies_water_damage(self):

        conditions = {
            'weather': constants.RAIN
        }

        move = 'surf'

        dmg = _calculate_damage(self.venusaur, self.charizard, move, conditions, calc_type='max')
        self.assertEqual([261], dmg)

    def test_rain_properly_reduces_fire_damage(self):

        conditions = {
            'weather': constants.RAIN
        }

        move = 'fireblast'

        dmg = _calculate_damage(self.venusaur, self.charizard, move, conditions, calc_type='max')
        self.assertEqual([26], dmg)

    def test_reflect_properly_halves_damage(self):

        conditions = {
            'reflect': 1
        }

        move = 'rockslide'

        dmg = _calculate_damage(self.venusaur, self.charizard, move, conditions, calc_type='max')
        self.assertEqual([134], dmg)

    def test_light_screen_properly_halves_damage(self):

        conditions = {
            'lightscreen': 1
        }

        move = 'psychic'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, conditions, calc_type='max')
        self.assertEqual([82], dmg)

    def test_aurora_veil_properly_halves_damage(self):

        conditions = {
            'auroraveil': 1
        }

        move = 'fireblast'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, conditions, calc_type='max')
        self.assertEqual([150], dmg)

    def test_boosts_properly_affect_damage_calculation(self):
        self.charizard.special_attack_boost = 2

        move = 'fireblast'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, calc_type='max')
        self.assertEqual([597], dmg)

    def test_move_versus_partially_typeless_pokemon(self):
        self.venusaur.types = ["typeless", "grass"]
        move = 'fireblast'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, calc_type='max')
        self.assertEqual([300], dmg)

    def test_move_versus_partially_typeless_pokemon_with_question_mark_type(self):
        self.venusaur.types = ["???", "grass"]
        move = 'fireblast'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, calc_type='max')
        self.assertEqual([300], dmg)

    def test_move_versus_completely_typeless_pokemon(self):
        self.venusaur.types = ["typeless"]
        move = 'fireblast'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, calc_type='max')
        self.assertEqual([150], dmg)

    def test_move_versus_completely_typeless_pokemon_with_question_mark_type(self):
        self.venusaur.types = ["???"]
        move = 'fireblast'

        dmg = _calculate_damage(self.charizard, self.venusaur, move, calc_type='max')
        self.assertEqual([150], dmg)


class TestCalculateDamage(unittest.TestCase):
    def setUp(self):
        self.blastoise = Pokemon.from_state_pokemon_dict(StatePokemon("blastoise", 100).to_dict())
        self.venusaur = Pokemon.from_state_pokemon_dict(StatePokemon("venusaur", 100).to_dict())

        self.state = State(
            Side(self.blastoise, dict(), (0, 0), defaultdict(lambda: 0), (0, 0)),
            Side(self.venusaur, dict(), (0, 0), defaultdict(lambda: 0), (0, 0)),
            None,
            None,
            None
        )

    def test_earthquake_into_levitate_does_zero_damage(self):
        self.state.user.active.ability = 'levitate'

        damage_amounts = calculate_damage(
            self.state,
            constants.OPPONENT,
            'earthquake',
            'splash'
        )

        self.assertEqual(0, damage_amounts[0])

    def test_bots_reflect_does_not_reduce_its_own_damage(self):
        self.state.opponent.side_conditions[constants.REFLECT] = 1

        damage_amounts = calculate_damage(
            self.state,
            constants.OPPONENT,
            'earthquake',
            'splash'
        )

        # should do normal damage of 68
        # the attacker (opponent) having reflect up shouldn't change anything
        self.assertEqual(68, damage_amounts[0])

    def test_moldbreaker_ignores_levitate(self):
        self.state.user.active.ability = 'levitate'
        self.state.opponent.active.ability = 'moldbreaker'

        damage_amounts = calculate_damage(
            self.state,
            constants.OPPONENT,
            'earthquake',
            'splash'
        )

        self.assertNotEqual(0, damage_amounts[0])

    def test_solarbeam_move_produces_damage_amount(self):
        damage_amounts = calculate_damage(
            self.state,
            constants.OPPONENT,
            'solarbeam',
            'splash'
        )

        self.assertNotEqual(0, damage_amounts[0])

    def test_phantomforce_move_produces_damage_amount(self):
        damage_amounts = calculate_damage(
            self.state,
            constants.OPPONENT,
            'phantomforce',
            'splash'
        )

        self.assertNotEqual(0, damage_amounts[0])
