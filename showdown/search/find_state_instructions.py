from functools import lru_cache

import config
import constants
from data import all_move_json
from showdown.search.instruction_generator import InstructionGenerator
from showdown.calculate_damage import DamageCalculator
from showdown.helpers import boost_multiplier_lookup
from showdown.search.transpose_instruction import TransposeInstruction

from showdown.search.special_effects.abilities.modify_attack_against import ability_modify_attack_against
from showdown.search.special_effects.abilities.modify_attack_being_used import ability_modify_attack_being_used
from showdown.search.special_effects.items.modify_attack_against import item_modify_attack_against
from showdown.search.special_effects.items.modify_attack_being_used import item_modify_attack_being_used
from showdown.search.special_effects.moves.move_special_effect import modify_attack_being_used
from showdown.search.switch_out_moves import switch_out_move_triggered
from showdown.search.switch_out_moves import get_best_switch_pokemon

from copy import copy

damage_calculator = DamageCalculator()
state_generator = InstructionGenerator()


def lookup_move(move_name):
    if move_name.startswith(constants.SWITCH_STRING + " "):
        split_move = move_name.split(" ")
        assert len(split_move) == 2, "Invalid switch string: {}".format(split_move)
        return {
            constants.SWITCH_STRING: split_move[1]
        }

    return all_move_json[move_name.lower()]


def get_effective_speed(state, side):
    boosted_speed = side.active.speed * boost_multiplier_lookup[side.active.speed_boost]

    if state.weather == constants.SUN and side.active.ability == 'chlorophyll':
        boosted_speed *= 2
    elif state.weather == constants.RAIN and side.active.ability == 'swiftswim':
        boosted_speed *= 2
    elif state.weather == constants.SAND and side.active.ability == 'sandrush':
        boosted_speed *= 2
    elif state.weather == constants.HAIL and side.active.ability == 'slushrush':
        boosted_speed *= 2

    if side.active.ability == 'unburden' and not side.active.item:
        boosted_speed *= 2

    if side.side_conditions[constants.TAILWIND]:
        boosted_speed *= 2

    if 'choicescarf' == side.active.item:
        boosted_speed *= 1.5

    if constants.PARALYZED == side.active.status:
        boosted_speed *= 0.5

    return int(boosted_speed)


def user_moves_first(state, user_move, opponent_move):
    user_effective_speed = get_effective_speed(state, state.self)
    opponent_effective_speed = get_effective_speed(state, state.opponent)

    # both users selected a switch
    if constants.SWITCH_STRING in user_move and constants.SWITCH_STRING in opponent_move:
        return user_effective_speed > opponent_effective_speed

    # user selected a switch
    elif constants.SWITCH_STRING in user_move:
        return True

    # opponent selected a switch
    elif constants.SWITCH_STRING in opponent_move:
        return False

    user_priority = user_move[constants.PRIORITY]
    opponent_priority = opponent_move[constants.PRIORITY]
    if state.self.active.ability == 'prankster' and user_move[constants.CATEGORY] == constants.STATUS:
        user_priority += 1
    if state.opponent.active.ability == 'prankster' and opponent_move[constants.CATEGORY] == constants.STATUS:
        opponent_priority += 1

    if user_priority == opponent_priority:
        user_is_faster = user_effective_speed > opponent_effective_speed
        if state.trick_room:
            return not user_is_faster
        else:
            return user_is_faster

    if user_priority > opponent_priority:
        return True
    else:
        return False


def update_damage_calc_from_abilities_and_items(attacking_pokemon, defending_pokemon, attacking_move, defending_move, first_move, weather):
    attacking_move = modify_attack_being_used(
        attacking_move,
        defending_move,
        attacking_pokemon,
        defending_pokemon,
        first_move,
        weather
    )

    attacking_move = ability_modify_attack_against(
        defending_pokemon.ability,
        attacking_move,
        attacking_pokemon,
        defending_pokemon
    )

    attacking_move = ability_modify_attack_being_used(
        attacking_pokemon.ability,
        attacking_move,
        attacking_pokemon,
        defending_pokemon,
        first_move
    )

    attacking_move = item_modify_attack_being_used(
        attacking_pokemon.item,
        attacking_move,
        attacking_pokemon,
        defending_pokemon
    )

    attacking_move = item_modify_attack_against(
        defending_pokemon.item,
        attacking_move,
        attacking_pokemon,
        defending_pokemon
    )

    return attacking_move


def get_state_instructions_from_move(mutator, attacking_move, defending_move, attacker, defender, first_move, instructions):
    instructions.frozen = False

    if constants.SWITCH_STRING in attacking_move:
        return state_generator.get_instructions_from_switch(mutator, attacker, attacking_move[constants.SWITCH_STRING], instructions)

    mutator.apply(instructions.instructions)
    attacking_side = InstructionGenerator.get_side_from_state(mutator.state, attacker)
    defending_side = InstructionGenerator.get_side_from_state(mutator.state, defender)
    attacking_pokemon = attacking_side.active
    defending_pokemon = defending_side.active
    active_weather = mutator.state.weather

    if constants.TAUNT in attacking_pokemon.volatile_status and attacking_move[constants.CATEGORY] not in constants.DAMAGING_CATEGORIES:
        attacking_move = lookup_move(constants.DO_NOTHING_MOVE)

    conditions = {
        constants.REFLECT: defending_side.side_conditions[constants.REFLECT],
        constants.LIGHT_SCREEN: defending_side.side_conditions[constants.LIGHT_SCREEN],
        constants.AURORA_VEIL: defending_side.side_conditions[constants.AURORA_VEIL],
        constants.WEATHER: active_weather,
        constants.TERRAIN: mutator.state.field
    }

    if attacking_pokemon.hp == 0:
        mutator.reverse(instructions.instructions)
        all_instructions = state_generator.get_instructions_from_flinched(mutator, attacker, instructions)
        return all_instructions

    attacking_move = update_damage_calc_from_abilities_and_items(
        attacking_pokemon,
        defending_pokemon,
        attacking_move,
        defending_move,
        first_move,
        mutator.state.weather
    )

    damage_amounts = None
    move_status_effect = None
    flinch_accuracy = None
    boosts = None
    boosts_target = None
    boosts_chance = None
    side_condition = None
    hazard_clearing_move = None
    volatile_status = attacking_move.get(constants.VOLATILE_STATUS)

    move_accuracy = min(100, attacking_move[constants.ACCURACY])
    move_status_accuracy = move_accuracy

    move_target = attacking_move[constants.TARGET]
    if move_target == constants.SELF:
        move_status_target = attacker
    else:
        move_status_target = defender

    if attacking_move[constants.ID] in constants.HAZARD_CLEARING_MOVES:
        hazard_clearing_move = attacking_move

    # move is a damaging move
    if attacking_move[constants.CATEGORY] in constants.DAMAGING_CATEGORIES:
        damage_amounts = damage_calculator.calculate_damage(attacking_pokemon, defending_pokemon, attacking_move, conditions=conditions, calc_type=config.damage_calc_type)

        attacking_move_secondary = attacking_move[constants.SECONDARY]
        attacking_move_self = attacking_move.get(constants.SELF)
        if attacking_move_secondary:
            # flinching (iron head)
            if attacking_move_secondary.get(constants.VOLATILE_STATUS) == constants.FLINCH and first_move:
                flinch_accuracy = attacking_move_secondary.get(constants.CHANCE)

            # secondary status effects (thunderbolt paralyzing)
            elif attacking_move_secondary.get(constants.STATUS) is not None:
                move_status_effect = attacking_move_secondary[constants.STATUS]
                move_status_accuracy = attacking_move_secondary[constants.CHANCE]

            # boosts from moves that boost in secondary (charge beam)
            elif attacking_move_secondary.get(constants.SELF) is not None:
                if constants.BOOSTS in attacking_move_secondary[constants.SELF]:
                    boosts = attacking_move_secondary[constants.SELF][constants.BOOSTS]
                    boosts_target = attacker
                    boosts_chance = attacking_move_secondary[constants.CHANCE]

            # boosts from secondary, but it is a guaranteed boost (dracometeor)
            elif attacking_move.get(constants.SELF) is not None:
                if constants.BOOSTS in attacking_move[constants.SELF]:
                    boosts = attacking_move[constants.SELF][constants.BOOSTS]
                    boosts_target = attacker
                    boosts_chance = 100

            # boosts from secondary, but to the defender (crunch)
            elif attacking_move_secondary and attacking_move_secondary.get(constants.BOOSTS) is not None:
                boosts = attacking_move_secondary[constants.BOOSTS]
                boosts_target = defender
                boosts_chance = attacking_move_secondary[constants.CHANCE]

        elif attacking_move_self:
            if constants.BOOSTS in attacking_move_self:
                boosts = attacking_move_self[constants.BOOSTS]
                boosts_target = attacker
                boosts_chance = 100

        elif constants.BOOSTS in attacking_move:
            boosts = attacking_move[constants.BOOSTS]
            boosts_target = attacker
            boosts_chance = 100

    # move is a status move
    else:
        move_status_effect = attacking_move.get(constants.STATUS)
        side_condition = attacking_move.get(constants.SIDE_CONDITIONS)

        # boosts from moves that only boost (dragon dance)
        if attacking_move.get(constants.BOOSTS) is not None:
            boosts = attacking_move[constants.BOOSTS]
            boosts_target = attacker if attacking_move[constants.TARGET] == constants.SELF else defender
            boosts_chance = attacking_move[constants.ACCURACY]

    mutator.reverse(instructions.instructions)

    all_instructions = state_generator.get_instructions_from_flinched(mutator, attacker, instructions)

    temp_instructions = []
    for instruction_set in all_instructions:
        temp_instructions += state_generator.get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, attacking_move, instruction_set)
    all_instructions = temp_instructions

    if damage_amounts is not None:
        temp_instructions = []
        for instruction_set in all_instructions:
            amount_of_damage_rolls = len(damage_amounts)
            for dmg in damage_amounts:
                these_instructions = copy(instruction_set)
                these_instructions.update_percentage(1 / amount_of_damage_rolls)
                temp_instructions += state_generator.get_states_from_damage(mutator, defender, dmg, move_accuracy, attacking_move.get(constants.DRAIN), attacking_move.get(constants.RECOIL), attacking_move.get(constants.CRASH), these_instructions)
        all_instructions = temp_instructions

    if side_condition is not None:
        temp_instructions = []
        for instruction_set in all_instructions:
            temp_instructions += state_generator.get_instructions_from_side_conditions(mutator, attacker, move_target, side_condition, instruction_set)
        all_instructions = temp_instructions

    if hazard_clearing_move is not None:
        temp_instructions = []
        for instruction_set in all_instructions:
            temp_instructions += state_generator.get_instructions_from_hazard_clearing_moves(mutator, attacker, attacking_move, instruction_set)
        all_instructions = temp_instructions

    if volatile_status is not None:
        temp_instructions = []
        for instruction_set in all_instructions:
            temp_instructions += state_generator.get_state_from_volatile_status(mutator, volatile_status, attacker, move_target, instruction_set)
        all_instructions = temp_instructions

    if move_status_effect is not None:
        temp_instructions = []
        for instruction_set in all_instructions:
            temp_instructions += state_generator.get_states_from_status_effects(mutator, move_status_target, move_status_effect, move_status_accuracy, instruction_set)
        all_instructions = temp_instructions

    if boosts is not None:
        temp_instructions = []
        for instruction_set in all_instructions:
            temp_instructions += state_generator.get_states_from_boosts(mutator, boosts_target, boosts, boosts_chance, instruction_set)
        all_instructions = temp_instructions

    if attacking_move.get(constants.HEAL) is not None:
        temp_instructions = []
        for instruction_set in all_instructions:
            temp_instructions += state_generator.get_state_from_attacker_recovery(mutator, attacker, attacking_move, instruction_set)
        all_instructions = temp_instructions

    if flinch_accuracy is not None:
        temp_instructions = []
        for instruction_set in all_instructions:
            temp_instructions += state_generator.get_states_from_flinching_moves(defender, flinch_accuracy, first_move, instruction_set)
        all_instructions = temp_instructions

    # technically this block should occur after both moves happen (i.e. at the end of the turn)
    temp_instructions = []
    for instruction_set in all_instructions:
        temp_instructions += state_generator.get_state_from_status_damage(mutator, attacker, instruction_set)
    all_instructions = temp_instructions

    temp_instructions = []
    for instruction_set in all_instructions:
        temp_instructions += state_generator.get_state_from_drag(mutator, attacking_move, attacker, move_target, instruction_set)
    all_instructions = temp_instructions

    if switch_out_move_triggered(attacking_move, damage_amounts):
        temp_instructions = []
        for i in all_instructions:
            best_switch = get_best_switch_pokemon(mutator, i, attacker, attacking_side, defending_move, first_move)
            if best_switch is not None:
                temp_instructions += state_generator.get_instructions_from_switch(mutator, attacker, best_switch, i)
            else:
                temp_instructions.append(i)

        all_instructions = temp_instructions

    return all_instructions


@lru_cache(maxsize=None)
def get_all_state_instructions(mutator, user_move_string, opponent_move_string):
    user_move = lookup_move(user_move_string)
    opponent_move = lookup_move(opponent_move_string)

    bot_moves_first = user_moves_first(mutator.state, user_move, opponent_move)

    instructions = TransposeInstruction(1.0, [], False)

    all_instructions = []
    if bot_moves_first:
        instructions = get_state_instructions_from_move(mutator, user_move, opponent_move, constants.SELF, constants.OPPONENT, True, instructions)
        for instruction in instructions:
            all_instructions += get_state_instructions_from_move(mutator, opponent_move, user_move, constants.OPPONENT, constants.SELF, False, instruction)
    else:
        instructions = get_state_instructions_from_move(mutator, opponent_move, user_move, constants.OPPONENT, constants.SELF, True, instructions)
        for instruction in instructions:
            all_instructions += get_state_instructions_from_move(mutator, user_move, opponent_move, constants.SELF, constants.OPPONENT, False, instruction)

    return all_instructions
