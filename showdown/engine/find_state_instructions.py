from copy import copy

import config
import constants
from data import all_move_json

from . import instruction_generator
from .damage_calculator import _calculate_damage
from .objects import TransposeInstruction
from .special_effects.abilities.modify_attack_against import ability_modify_attack_against
from .special_effects.abilities.modify_attack_being_used import ability_modify_attack_being_used
from .special_effects.items.modify_attack_against import item_modify_attack_against
from .special_effects.items.modify_attack_being_used import item_modify_attack_being_used
from .special_effects.moves.modify_move import modify_attack_being_used
from .special_effects.abilities.before_move import ability_before_move
from .switch_out_moves import switch_out_move_triggered
from .switch_out_moves import get_best_switch_pokemon


def lookup_move(move_name):
    if move_name.startswith(constants.SWITCH_STRING + " "):
        split_move = move_name.split(" ")
        assert len(split_move) == 2, "Invalid switch string: {}".format(split_move)
        return {
            constants.SWITCH_STRING: split_move[1]
        }

    return all_move_json[move_name.lower()]


def get_effective_speed(state, side):
    boosted_speed = side.active.calculate_boosted_stats()[constants.SPEED]

    if state.weather == constants.SUN and side.active.ability == 'chlorophyll':
        boosted_speed *= 2
    elif state.weather == constants.RAIN and side.active.ability == 'swiftswim':
        boosted_speed *= 2
    elif state.weather == constants.SAND and side.active.ability == 'sandrush':
        boosted_speed *= 2
    elif state.weather == constants.HAIL and side.active.ability == 'slushrush':
        boosted_speed *= 2

    if state.field == constants.ELECTRIC_TERRAIN and side.active.ability == 'surgesurfer':
        boosted_speed *= 2

    if side.active.ability == 'unburden' and not side.active.item:
        boosted_speed *= 2
    elif side.active.ability == 'quickfeet' and side.active.status is not None:
        boosted_speed *= 1.5

    if side.side_conditions[constants.TAILWIND]:
        boosted_speed *= 2

    if 'choicescarf' == side.active.item:
        boosted_speed *= 1.5

    if constants.PARALYZED == side.active.status and side.active.ability != 'quickfeet':
        boosted_speed *= 0.5

    return int(boosted_speed)


def get_effective_priority(side, move, field):
    priority = move[constants.PRIORITY]
    if side.active.ability == 'prankster' and move[constants.CATEGORY] == constants.STATUS:
        priority += 1
    elif side.active.ability == 'galewings' and (side.active.hp == side.active.maxhp) and ('flying' in move[constants.TYPE]):
        priority += 1
    elif side.active.ability == 'triage' and constants.HEAL in move[constants.FLAGS]:
        priority += 3
    elif field == constants.GRASSY_TERRAIN and move[constants.ID] == 'grassyglide':
        priority += 1

    return priority


def user_moves_first(state, user_move, opponent_move):
    user_effective_speed = get_effective_speed(state, state.user)
    opponent_effective_speed = get_effective_speed(state, state.opponent)

    # both users selected a switch
    if constants.SWITCH_STRING in user_move and constants.SWITCH_STRING in opponent_move:
        return user_effective_speed > opponent_effective_speed

    # user selected a switch
    elif constants.SWITCH_STRING in user_move:
        if opponent_move[constants.ID] == 'pursuit':
            return False
        return True

    # opponent selected a switch
    elif constants.SWITCH_STRING in opponent_move:
        if user_move[constants.ID] == 'pursuit':
            return True
        return False

    user_priority = get_effective_priority(state.user, user_move, state.field)
    opponent_priority = get_effective_priority(state.opponent, opponent_move, state.field)

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


def update_attacking_move(attacking_pokemon, defending_pokemon, attacking_move, defending_move, first_move, weather, terrain):
    # update the attacking move based on certain special-effects:
    #   - abilities
    #   - items
    #   - protect

    attacking_move = modify_attack_being_used(
        attacking_move,
        defending_move,
        attacking_pokemon,
        defending_pokemon,
        first_move,
        weather,
        terrain
    )

    attacking_move = ability_modify_attack_being_used(
        attacking_pokemon.ability,
        attacking_move,
        defending_move,
        attacking_pokemon,
        defending_pokemon,
        first_move,
        weather
    )

    attacking_move = item_modify_attack_being_used(
        attacking_pokemon.item,
        attacking_move,
        attacking_pokemon,
        defending_pokemon
    )

    attacking_move = ability_modify_attack_against(
        defending_pokemon.ability,
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

    if constants.CHARGE in attacking_move[constants.FLAGS] and attacking_move[constants.ID] not in attacking_pokemon.volatile_status:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = 0
        attacking_move[constants.HEAL] = None
        attacking_move[constants.VOLATILE_STATUS] = attacking_move[constants.ID]
        attacking_move[constants.TARGET] = constants.SELF
        attacking_move[constants.CATEGORY] = constants.STATUS

    if (
            constants.PROTECT in attacking_move[constants.FLAGS] and
            any(vs in constants.PROTECT_VOLATILE_STATUSES for vs in defending_pokemon.volatile_status) and
            not (attacking_pokemon.ability == 'unseenfist' and constants.CONTACT in attacking_move[constants.FLAGS])
    ):
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = False
        if constants.BANEFUL_BUNKER in defending_pokemon.volatile_status and constants.CONTACT in attacking_move[constants.FLAGS]:
            attacking_move[constants.ACCURACY] = True
            attacking_move[constants.CATEGORY] = constants.STATUS
            attacking_move[constants.STATUS] = constants.POISON
            attacking_move[constants.TARGET] = constants.SELF
            if constants.CRASH in attacking_move:
                attacking_move[constants.HEAL_TARGET] = constants.SELF
                attacking_move[constants.HEAL] = [-1*attacking_move[constants.CRASH][0], attacking_move[constants.CRASH][1]]
        elif constants.SPIKY_SHIELD in defending_pokemon.volatile_status and constants.CONTACT in attacking_move[constants.FLAGS]:
            attacking_move[constants.ACCURACY] = True
            attacking_move[constants.CATEGORY] = constants.STATUS
            attacking_move[constants.STATUS] = None
            attacking_move[constants.HEAL_TARGET] = constants.SELF
            attacking_move[constants.HEAL] = [-1, 8]
            if constants.CRASH in attacking_move:
                crash_percent = attacking_move[constants.CRASH][0] / attacking_move[constants.CRASH][1]
                damage_decimal = -1*(crash_percent + 1/8)
                attacking_move[constants.HEAL] = damage_decimal.as_integer_ratio()

    return attacking_move


def cannot_use_move(attacking_pokemon, attacking_move):
    return constants.TAUNT in attacking_pokemon.volatile_status and attacking_move[constants.CATEGORY] not in constants.DAMAGING_CATEGORIES


def get_state_instructions_from_move(mutator, attacking_move, defending_move, attacker, defender, first_move, instructions):
    instructions.frozen = False

    if constants.SWITCH_STRING in attacking_move:
        return [instruction_generator.get_instructions_from_switch(mutator, attacker, attacking_move[constants.SWITCH_STRING], instructions)]

    # if you are moving second, but you got phased on the first turn, your move will do nothing
    # this can happen if a move with equal priority to a phasing move (generally -6) is used by a slower pokemon and the faster pokemon uses a phasing move
    if not first_move and constants.DRAG in defending_move.get(constants.FLAGS, {}):
        return [instructions]

    mutator.apply(instructions.instructions)
    attacking_side = instruction_generator.get_side_from_state(mutator.state, attacker)
    defending_side = instruction_generator.get_side_from_state(mutator.state, defender)
    attacking_pokemon = attacking_side.active
    defending_pokemon = defending_side.active
    active_weather = mutator.state.weather

    if cannot_use_move(attacking_pokemon, attacking_move):
        attacking_move = lookup_move(constants.DO_NOTHING_MOVE)

    conditions = {
        constants.REFLECT: defending_side.side_conditions[constants.REFLECT],
        constants.LIGHT_SCREEN: defending_side.side_conditions[constants.LIGHT_SCREEN],
        constants.AURORA_VEIL: defending_side.side_conditions[constants.AURORA_VEIL],
        constants.WEATHER: active_weather,
        constants.TERRAIN: mutator.state.field
    }

    if attacking_pokemon.hp == 0:
        # if the attacker is dead, remove the 'flinched' volatile-status if it has it and exit early
        # this triggers if the pokemon moves second but the first attack knocked it out
        instructions = instruction_generator.get_instructions_from_flinched(mutator, attacker, instructions)
        mutator.reverse(instructions.instructions)
        return [instructions]

    attacking_move = update_attacking_move(
        attacking_pokemon,
        defending_pokemon,
        attacking_move,
        defending_move,
        first_move,
        mutator.state.weather,
        mutator.state.field
    )

    instructions = instruction_generator.get_instructions_from_flinched(mutator, attacker, instructions)

    ability_before_move_instructions = ability_before_move(
        attacking_pokemon.ability,
        mutator.state,
        attacker,
        attacking_move,
        attacking_pokemon,
        defending_pokemon
    )
    if ability_before_move_instructions is not None and not instructions.frozen:
        mutator.apply(ability_before_move_instructions)
        instructions.instructions += ability_before_move_instructions

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
        damage_amounts = _calculate_damage(attacking_pokemon, defending_pokemon, attacking_move, conditions=conditions, calc_type=config.damage_calc_type)

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

            # boosts from secondary, but to the defender (crunch)
            elif attacking_move_secondary and attacking_move_secondary.get(constants.BOOSTS) is not None:
                boosts = attacking_move_secondary[constants.BOOSTS]
                boosts_target = defender
                boosts_chance = attacking_move_secondary[constants.CHANCE]

        # boosts from secondary, but it is a guaranteed boost (dracometeor)
        elif attacking_move_self:
            if constants.BOOSTS in attacking_move_self:
                boosts = attacking_move_self[constants.BOOSTS]
                boosts_target = attacker
                boosts_chance = 100

        # guaranteed boosts from a damaging move (none in the moves JSON but items/abilities can cause this)
        elif constants.BOOSTS in attacking_move:
            boosts = attacking_move[constants.BOOSTS]
            boosts_target = attacker if attacking_move[constants.TARGET] in constants.MOVE_TARGET_SELF else defender
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

    all_instructions = instruction_generator.get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, attacking_move, defending_move, instructions)

    temp_instructions = []
    for instruction_set in all_instructions:
        temp_instructions += instruction_generator.get_instructions_from_move_special_effect(mutator, attacker, attacking_pokemon, defending_pokemon, attacking_move[constants.ID], instruction_set)
    all_instructions = temp_instructions

    if damage_amounts is not None:
        temp_instructions = []
        for instruction_set in all_instructions:
            amount_of_damage_rolls = len(damage_amounts)
            for dmg in damage_amounts:
                these_instructions = copy(instruction_set)
                these_instructions.update_percentage(1 / amount_of_damage_rolls)
                temp_instructions += instruction_generator.get_instructions_from_damage(mutator, defender, dmg, move_accuracy, attacking_move, these_instructions)
        all_instructions = temp_instructions

    if defending_pokemon.ability in constants.ABILITY_AFTER_MOVE:
        temp_instructions = []
        for instruction_set in all_instructions:
            temp_instructions += instruction_generator.get_instructions_from_defenders_ability_after_move(mutator, attacking_move, defending_pokemon.ability, attacking_pokemon, attacker, instruction_set)
        all_instructions = temp_instructions

    if side_condition is not None:
        temp_instructions = []
        for instruction_set in all_instructions:
            temp_instructions += instruction_generator.get_instructions_from_side_conditions(mutator, attacker, move_target, side_condition, instruction_set)
        all_instructions = temp_instructions

    if hazard_clearing_move is not None:
        temp_instructions = []
        for instruction_set in all_instructions:
            temp_instructions += instruction_generator.get_instructions_from_hazard_clearing_moves(mutator, attacker, attacking_move, instruction_set)
        all_instructions = temp_instructions

    if volatile_status is not None:
        temp_instructions = []
        for instruction_set in all_instructions:
            temp_instructions += instruction_generator.get_instructions_from_volatile_statuses(mutator, volatile_status, attacker, move_target, first_move, instruction_set)
        all_instructions = temp_instructions

    if move_status_effect is not None:
        temp_instructions = []
        for instruction_set in all_instructions:
            temp_instructions += instruction_generator.get_instructions_from_status_effects(mutator, move_status_target, move_status_effect, move_status_accuracy, instruction_set)
        all_instructions = temp_instructions

    if boosts is not None:
        temp_instructions = []
        for instruction_set in all_instructions:
            temp_instructions += instruction_generator.get_instructions_from_boosts(mutator, boosts_target, boosts, boosts_chance, instruction_set)
        all_instructions = temp_instructions

    if attacking_move[constants.ID] in constants.BOOST_RESET_MOVES:
        temp_instructions = []
        for instruction_set in all_instructions:
            temp_instructions += instruction_generator.get_instructions_from_boost_reset_moves(mutator, attacking_move, attacker, instruction_set)
        all_instructions = temp_instructions

    if attacking_move.get(constants.HEAL) is not None:
        temp_instructions = []
        for instruction_set in all_instructions:
            temp_instructions += instruction_generator.get_instructions_from_attacker_recovery(mutator, attacker, attacking_move, instruction_set)
        all_instructions = temp_instructions

    if flinch_accuracy is not None:
        temp_instructions = []
        for instruction_set in all_instructions:
            temp_instructions += instruction_generator.get_instructions_from_flinching_moves(defender, flinch_accuracy, first_move, instruction_set)
        all_instructions = temp_instructions

    if constants.DRAG in attacking_move[constants.FLAGS]:
        temp_instructions = []
        for instruction_set in all_instructions:
            temp_instructions += instruction_generator.get_instructions_from_drag(mutator, attacker, move_target, instruction_set)
        all_instructions = temp_instructions

    if switch_out_move_triggered(attacking_move, damage_amounts):
        temp_instructions = []
        for i in all_instructions:
            best_switch = get_best_switch_pokemon(mutator, i, attacker, attacking_side, defending_move, first_move)
            if best_switch is not None:
                temp_instructions.append(instruction_generator.get_instructions_from_switch(mutator, attacker, best_switch, i))
            else:
                temp_instructions.append(i)

        all_instructions = temp_instructions

    return all_instructions


def remove_duplicate_instructions(list_of_instructions):
    new_instructions = [list_of_instructions[0]]
    for instruction_1 in list_of_instructions[1:]:
        for instruction_2 in new_instructions:
            if instruction_1.has_same_instructions_as(instruction_2):
                instruction_2.percentage += instruction_1.percentage
                break
        else:
            new_instructions.append(instruction_1)

    return new_instructions


def end_of_turn_triggered(user_move, opponent_move):
    if user_move.startswith(constants.SWITCH_STRING + ' ') and opponent_move == constants.DO_NOTHING_MOVE:
        return False
    elif opponent_move.startswith(constants.SWITCH_STRING + ' ') and user_move == constants.DO_NOTHING_MOVE:
        return False

    return True


def get_all_state_instructions(mutator, user_move_string, opponent_move_string):
    user_move = lookup_move(user_move_string)
    opponent_move = lookup_move(opponent_move_string)

    bot_moves_first = user_moves_first(mutator.state, user_move, opponent_move)

    instructions = TransposeInstruction(1.0, [], False)

    all_instructions = []
    if bot_moves_first:
        instructions = get_state_instructions_from_move(mutator, user_move, opponent_move, constants.USER, constants.OPPONENT, True, instructions)
        for instruction in instructions:
            all_instructions += get_state_instructions_from_move(mutator, opponent_move, user_move, constants.OPPONENT, constants.USER, False, instruction)
    else:
        instructions = get_state_instructions_from_move(mutator, opponent_move, user_move, constants.OPPONENT, constants.USER, True, instructions)
        for instruction in instructions:
            all_instructions += get_state_instructions_from_move(mutator, user_move, opponent_move, constants.USER, constants.OPPONENT, False, instruction)

    if end_of_turn_triggered(user_move_string, opponent_move_string):
        temp_instructions = []
        for instruction_set in all_instructions:
            temp_instructions += instruction_generator.get_end_of_turn_instructions(mutator, instruction_set, user_move, opponent_move, bot_moves_first)
        all_instructions = temp_instructions

    all_instructions = remove_duplicate_instructions(all_instructions)

    return all_instructions
