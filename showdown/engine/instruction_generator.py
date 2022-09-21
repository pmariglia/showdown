from copy import copy

import constants
import logging

from .damage_calculator import type_effectiveness_modifier
from .special_effects.abilities.on_switch_in import ability_on_switch_in
from .special_effects.items.on_switch_in import item_on_switch_in
from .special_effects.items.end_of_turn import item_end_of_turn
from .special_effects.abilities.end_of_turn import ability_end_of_turn
from .special_effects.moves.after_move import after_move
from .special_effects.moves import move_special_effect

logger = logging.getLogger(__name__)


opposite_side = {
    constants.USER: constants.OPPONENT,
    constants.OPPONENT: constants.USER
}


same_side_strings = [
    constants.SELF,
    constants.ALLY_SIDE
]


opposing_side_strings = [
    constants.NORMAL,
    constants.OPPONENT,
    constants.FOESIDE,
    constants.ALL_ADJACENT_FOES,
    constants.ALL_ADJACENT,
    constants.ALL,
]


accuracy_multiplier_lookup = {
    -6: 3/9,
    -5: 3/8,
    -4: 3/7,
    -3: 3/6,
    -2: 3/5,
    -1: 3/4,
    0: 3/3,
    1: 4/3,
    2: 5/3,
    3: 6/3,
    4: 7/3,
    5: 8/3,
    6: 9/3
}


def _get_beastboost_stat(pkmn):
    return max({
        constants.ATTACK: pkmn.attack,
        constants.DEFENSE: pkmn.defense,
        constants.SPECIAL_ATTACK: pkmn.special_attack,
        constants.SPECIAL_DEFENSE: pkmn.special_defense,
        constants.SPEED: pkmn.speed,
    }.items(), key=lambda x: x[1])[0]


def get_instructions_from_move_special_effect(mutator, attacking_side, attacking_pokemon, defending_pokemon, move_name, instructions):
    if instructions.frozen:
        return [instructions]

    try:
        special_logic_move_function = getattr(move_special_effect, move_name)
    except AttributeError:
        new_instructions = list()
    else:
        mutator.apply(instructions.instructions)
        new_instructions = special_logic_move_function(mutator, attacking_side, get_side_from_state(mutator.state, attacking_side), attacking_pokemon, defending_pokemon)
        new_instructions = new_instructions or list()
        mutator.reverse(instructions.instructions)

    for i in new_instructions:
        instructions.add_instruction(i)

    return [instructions]


def get_instructions_from_volatile_statuses(mutator, volatile_status, attacker, affected_side, first_move, instruction):
    if instruction.frozen or not volatile_status:
        return [instruction]

    if affected_side in same_side_strings:
        affected_side = attacker
    elif affected_side in opposing_side_strings:
        affected_side = opposite_side[attacker]
    else:
        logger.critical("Invalid affected_side: {}".format(affected_side))
        return [instruction]

    side = get_side_from_state(mutator.state, affected_side)
    mutator.apply(instruction.instructions)
    if volatile_status in side.active.volatile_status:
        mutator.reverse(instruction.instructions)
        return [instruction]

    if can_be_volatile_statused(side, volatile_status, first_move) and volatile_status not in side.active.volatile_status:
        apply_status_instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            affected_side,
            volatile_status
        )
        mutator.reverse(instruction.instructions)
        instruction.add_instruction(apply_status_instruction)
        if volatile_status == constants.SUBSTITUTE:
            instruction.add_instruction(
                (
                    constants.MUTATOR_DAMAGE,
                    affected_side,
                    side.active.maxhp * 0.25
                )
            )
    else:
        mutator.reverse(instruction.instructions)

    return [instruction]


def get_instructions_from_switch(mutator, attacker, switch_pokemon_name, instructions):
    if attacker not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}".format(', '.join(opposite_side)))

    attacking_side = get_side_from_state(mutator.state, attacker)
    defending_side = get_side_from_state(mutator.state, opposite_side[attacker])
    mutator.apply(instructions.instructions)
    instruction_additions = remove_volatile_status_and_boosts_instructions(attacking_side, attacker)
    mutator.apply(instruction_additions)

    for move in filter(lambda x: x[constants.DISABLED] is True and x[constants.CURRENT_PP], attacking_side.active.moves):
        remove_disabled_instruction = (
            constants.MUTATOR_ENABLE_MOVE,
            attacker,
            move[constants.ID]
        )
        mutator.apply_one(remove_disabled_instruction)
        instruction_additions.append(remove_disabled_instruction)

    if attacking_side.active.ability == 'regenerator' and attacking_side.active.hp:
        hp_missing = attacking_side.active.maxhp - attacking_side.active.hp
        regenerator_instruction = (
            constants.MUTATOR_HEAL,
            attacker,
            int(min(1 / 3 * attacking_side.active.maxhp, hp_missing))
        )
        mutator.apply_one(regenerator_instruction)
        instruction_additions.append(regenerator_instruction)
    elif attacking_side.active.ability == 'naturalcure' and attacking_side.active.status is not None:
        naturalcure_instruction = (
            constants.MUTATOR_REMOVE_STATUS,
            attacker,
            attacking_side.active.status
        )
        mutator.apply_one(naturalcure_instruction)
        instruction_additions.append(naturalcure_instruction)

    switch_instruction = (
        constants.MUTATOR_SWITCH,
        attacker,
        attacking_side.active.id,
        switch_pokemon_name
    )
    mutator.apply_one(switch_instruction)
    instruction_additions.append(switch_instruction)

    switch_pkmn = attacking_side.active
    if switch_pkmn.item != 'heavydutyboots':

        # account for stealth rock damage
        if attacking_side.side_conditions[constants.STEALTH_ROCK] == 1:
            multiplier = type_effectiveness_modifier('rock', switch_pkmn.types)
            stealth_rock_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                min(1 / 8 * multiplier * switch_pkmn.maxhp, switch_pkmn.hp)
            )
            mutator.apply_one(stealth_rock_instruction)
            instruction_additions.append(stealth_rock_instruction)

        # account for spikes damage
        if attacking_side.side_conditions[constants.SPIKES] > 0 and switch_pkmn.is_grounded():
            spike_count = attacking_side.side_conditions[constants.SPIKES]
            spikes_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                min(1 / 8 * spike_count * switch_pkmn.maxhp, switch_pkmn.hp)
            )
            mutator.apply_one(spikes_instruction)
            instruction_additions.append(spikes_instruction)

        # account for stickyweb speed drop
        if attacking_side.side_conditions[constants.STICKY_WEB] == 1 and switch_pkmn.is_grounded() and switch_pkmn.ability not in constants.IMMUNE_TO_STAT_LOWERING_ABILITIES:
            sticky_web_instruction = (
                constants.MUTATOR_UNBOOST,
                attacker,
                constants.SPEED,
                1
            )
            mutator.apply_one(sticky_web_instruction)
            instruction_additions.append(sticky_web_instruction)

        # account for toxic spikes effect
        if attacking_side.side_conditions[constants.TOXIC_SPIKES] >= 1 and switch_pkmn.is_grounded():
            toxic_spike_instruction = None
            if not immune_to_status(mutator.state, switch_pkmn, switch_pkmn, constants.POISON):
                if attacking_side.side_conditions[constants.TOXIC_SPIKES] == 1:
                    toxic_spike_instruction = (
                        constants.MUTATOR_APPLY_STATUS,
                        attacker,
                        constants.POISON
                    )
                elif attacking_side.side_conditions[constants.TOXIC_SPIKES] == 2:
                    toxic_spike_instruction = (
                        constants.MUTATOR_APPLY_STATUS,
                        attacker,
                        constants.TOXIC
                    )
            elif 'poison' in switch_pkmn.types:
                toxic_spike_instruction = (
                    constants.MUTATOR_SIDE_END,
                    attacker,
                    constants.TOXIC_SPIKES,
                    attacking_side.side_conditions[constants.TOXIC_SPIKES]
                )
            if toxic_spike_instruction is not None:
                mutator.apply_one(toxic_spike_instruction)
                instruction_additions.append(toxic_spike_instruction)

    # account for switch-in abilities
    ability_switch_in_instructions = ability_on_switch_in(
        switch_pkmn.ability,
        mutator.state,
        attacker,
        attacking_side.active,
        opposite_side[attacker],
        defending_side.active
    )
    if ability_switch_in_instructions is not None:
        for i in ability_switch_in_instructions:
            mutator.apply_one(i)
            instruction_additions.append(i)

    # account for switch-in items
    item_switch_in_instructions = item_on_switch_in(
        switch_pkmn.item,
        mutator.state,
        attacker,
        attacking_side.active,
        opposite_side[attacker],
        defending_side.active
    )
    if item_switch_in_instructions is not None:
        for i in item_switch_in_instructions:
            mutator.apply_one(i)
            instruction_additions.append(i)

    mutator.reverse(instruction_additions)
    mutator.reverse(instructions.instructions)
    for i in instruction_additions:
        instructions.add_instruction(i)

    return instructions


def get_instructions_from_flinched(mutator, attacker, instruction):
    """If the attacker has been flinched, freeze the state so that nothing happens"""
    if attacker not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}".format(', '.join(opposite_side)))

    side = get_side_from_state(mutator.state, attacker)
    if constants.FLINCH in side.active.volatile_status:
        remove_flinch_instruction = (
            constants.MUTATOR_REMOVE_VOLATILE_STATUS,
            attacker,
            constants.FLINCH
        )
        mutator.apply_one(remove_flinch_instruction)
        instruction.add_instruction(remove_flinch_instruction)
        instruction.frozen = True
        return instruction
    else:
        return instruction


def get_instructions_from_statuses_that_freeze_the_state(mutator, attacker, defender, move, opponent_move, instruction):
    instructions = [instruction]
    attacker_side = get_side_from_state(mutator.state, attacker)
    defender_side = get_side_from_state(mutator.state, defender)

    mutator.apply(instruction.instructions)

    if constants.PARALYZED == attacker_side.active.status:
        fully_paralyzed_instruction = copy(instruction)
        fully_paralyzed_instruction.update_percentage(constants.FULLY_PARALYZED_PERCENT)
        fully_paralyzed_instruction.frozen = True
        instruction.update_percentage(1 - constants.FULLY_PARALYZED_PERCENT)
        instructions.append(fully_paralyzed_instruction)

    elif constants.SLEEP == attacker_side.active.status:
        still_asleep_instruction = copy(instruction)
        still_asleep_instruction.update_percentage(1 - constants.WAKE_UP_PERCENT)
        still_asleep_instruction.frozen = True
        instruction.update_percentage(constants.WAKE_UP_PERCENT)
        instruction.add_instruction(
            (
                constants.MUTATOR_REMOVE_STATUS,
                attacker,
                constants.SLEEP
            )
        )
        instructions.append(still_asleep_instruction)

    elif constants.FROZEN == attacker_side.active.status:
        still_frozen_instruction = copy(instruction)
        instruction.add_instruction(
            (
                constants.MUTATOR_REMOVE_STATUS,
                attacker,
                constants.FROZEN
            )
        )
        if move[constants.ID] not in constants.THAW_IF_USES and opponent_move.get(constants.ID) not in constants.THAW_IF_HIT_BY and opponent_move.get(constants.TYPE) != 'fire':
            still_frozen_instruction.update_percentage(1 - constants.THAW_PERCENT)
            still_frozen_instruction.frozen = True
            instruction.update_percentage(constants.THAW_PERCENT)
            instructions.append(still_frozen_instruction)

    if constants.POWDER in move[constants.FLAGS] and ('grass' in defender_side.active.types or defender_side.active.ability == 'overcoat'):
        instruction.frozen = True

    if move[constants.TYPE] == 'electric' and 'ground' in defender_side.active.types:
        instruction.frozen = True

    mutator.reverse(instruction.instructions)

    return instructions


def get_instructions_from_damage(mutator, defender, damage, accuracy, attacking_move, instruction):
    attacker = opposite_side[defender]
    attacker_side = get_side_from_state(mutator.state, attacker)
    damage_side = get_side_from_state(mutator.state, defender)

    # `damage is None` means that the move does not deal damage
    # for example, will-o-wisp
    if instruction.frozen or damage is None:
        return [instruction]

    crash = attacking_move.get(constants.CRASH)
    recoil = attacking_move.get(constants.RECOIL)
    drain = attacking_move.get(constants.DRAIN)
    move_flags = attacking_move.get(constants.FLAGS, {})

    mutator.apply(instruction.instructions)

    if accuracy is True:
        accuracy = 100
    else:
        accuracy = min(100, accuracy * accuracy_multiplier_lookup[attacker_side.active.accuracy_boost] / accuracy_multiplier_lookup[damage_side.active.evasion_boost])
    percent_hit = accuracy / 100

    # `damage == 0` means that the move deals damage, but not in this situation
    # for example: using Return against a Ghost-type
    # the state must be frozen because any secondary effects must not take place
    if damage == 0:
        if crash:
            crash_percent = crash[0] / crash[1]
            crash_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                min(int(crash_percent * attacker_side.active.maxhp), attacker_side.active.hp)
            )
            mutator.reverse(instruction.instructions)
            instruction.add_instruction(crash_instruction)
        else:
            mutator.reverse(instruction.instructions)
        instruction.frozen = True
        return [instruction]

    if defender not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}".format(', '.join(opposite_side)))

    instructions = []
    instruction_additions = []
    move_missed_instruction = copy(instruction)
    hit_sub = False
    if percent_hit > 0:
        if constants.SUBSTITUTE in damage_side.active.volatile_status and constants.SOUND not in move_flags and attacker_side.active.ability != 'infiltrator':
            hit_sub = True
            if damage >= damage_side.active.maxhp * 0.25:
                actual_damage = damage_side.active.maxhp * 0.25
                instruction_additions.append(
                    (
                        constants.MUTATOR_REMOVE_VOLATILE_STATUS,
                        defender,
                        constants.SUBSTITUTE
                    )
                )
            else:
                actual_damage = damage
        else:
            # dont drop hp below 0 (min() statement), and dont overheal (max() statement)
            actual_damage = max(min(damage, damage_side.active.hp), -1*(damage_side.active.maxhp - damage_side.active.hp))

            if damage_side.active.ability == 'sturdy' and damage_side.active.hp == damage_side.active.maxhp:
                actual_damage -= 1

            instruction_additions.append(
                (
                    constants.MUTATOR_DAMAGE,
                    defender,
                    actual_damage
                )
            )

            if attacker_side.active.ability == "beastboost" and actual_damage == damage_side.active.hp:
                beastboost_stat = _get_beastboost_stat(attacker_side.active)
                if get_boost_from_boost_string(attacker_side, beastboost_stat) < 6:
                    instruction_additions.append(
                        (
                            constants.MUTATOR_BOOST,
                            attacker,
                            beastboost_stat,
                            1
                        )
                    )

        instruction.update_percentage(percent_hit)

        if damage_side.active.hp <= 0:
            instruction.frozen = True

        if drain:
            drain_percent = drain[0] / drain[1]
            drain_instruction = (
                constants.MUTATOR_HEAL,
                attacker,
                min(int(drain_percent * actual_damage), int(attacker_side.active.maxhp - attacker_side.active.hp))
            )
            instruction_additions.append(drain_instruction)
        if recoil:
            recoil_percent = recoil[0] / recoil[1]
            recoil_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                min(int(recoil_percent * actual_damage), int(attacker_side.active.hp))
            )
            instruction_additions.append(recoil_instruction)

        after_move_instructions = after_move(
            attacking_move[constants.ID],
            mutator.state,
            attacker,
            defender,
            attacker_side,
            damage_side,
            True,
            hit_sub
        )
        instruction_additions += after_move_instructions

        instructions.append(instruction)

    if percent_hit < 1:
        move_missed_instruction.frozen = True
        move_missed_instruction.update_percentage(1 - percent_hit)
        if crash:
            crash_percent = crash[0] / crash[1]
            crash_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                min(int(crash_percent * attacker_side.active.maxhp), attacker_side.active.hp)
            )
            move_missed_instruction.add_instruction(crash_instruction)

        if attacker_side.active.item == 'blunderpolicy':
            blunder_policy_increase_speed_instruction = (
                constants.MUTATOR_BOOST,
                attacker,
                constants.SPEED,
                2
            )
            move_missed_instruction.add_instruction(blunder_policy_increase_speed_instruction)

        after_move_instructions = after_move(
            attacking_move[constants.ID],
            mutator.state,
            attacker,
            defender,
            attacker_side,
            damage_side,
            False,
            False
        )
        for i in after_move_instructions:
            move_missed_instruction.add_instruction(i)

        instructions.append(move_missed_instruction)

    mutator.reverse(instruction.instructions)
    for i in instruction_additions:
        instruction.add_instruction(i)

    return instructions


def get_instructions_from_defenders_ability_after_move(mutator, move, ability_name, attacking_pokemon, attacker_string, instruction):
    all_instructions = [instruction]
    if instruction.frozen:
        return all_instructions

    if attacker_string not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}".format(', '.join(opposite_side)))

    if (
        ability_name == "static"
        and constants.CONTACT in move[constants.FLAGS]
        and attacking_pokemon.item != "protectivepads"
    ):
        return get_instructions_from_status_effects(
            mutator,
            attacker_string,
            constants.PARALYZED,
            30,
            instruction
        )
    elif (
        ability_name == "flamebody"
        and constants.CONTACT in move[constants.FLAGS]
        and attacking_pokemon.item != "protectivepads"
    ):
        return get_instructions_from_status_effects(
            mutator,
            attacker_string,
            constants.BURN,
            30,
            instruction
        )

    return all_instructions


def get_instructions_from_side_conditions(mutator, attacker_string, side_string, condition, instruction):
    if instruction.frozen:
        return [instruction]

    if attacker_string not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}".format(', '.join(opposite_side)))

    if side_string in same_side_strings:
        side_string = attacker_string
    elif side_string in opposing_side_strings:
        side_string = opposite_side[attacker_string]
    else:
        raise ValueError("Invalid Side String: {}".format(side_string))

    instruction_additions = []
    side = get_side_from_state(mutator.state, side_string)
    mutator.apply(instruction.instructions)

    if condition == constants.WISH:
        if side.wish[0] == 0:
            instruction_additions.append(
                (
                    constants.MUTATOR_WISH_START,
                    side_string,
                    side.active.maxhp / 2,
                    side.wish[1]
                )
            )

    else:
        if condition == constants.SPIKES:
            max_layers = 3
        elif condition == constants.TOXIC_SPIKES:
            max_layers = 2
        elif condition == constants.AURORA_VEIL:
            max_layers = 1 if mutator.state.weather == constants.HAIL else 0
        else:
            max_layers = 1

        if side.side_conditions[condition] < max_layers:
            instruction_additions.append(
                (
                    constants.MUTATOR_SIDE_START,
                    side_string,
                    condition,
                    1
                )
            )

    mutator.reverse(instruction.instructions)
    for i in instruction_additions:
        instruction.add_instruction(i)

    return [instruction]


def get_instructions_from_hazard_clearing_moves(mutator, attacker_string, move, instruction):
    if instruction.frozen:
        return [instruction]

    if attacker_string not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}".format(', '.join(opposite_side)))

    defender_string = opposite_side[attacker_string]

    instruction_additions = []
    mutator.apply(instruction.instructions)

    attacker_side = get_side_from_state(mutator.state, attacker_string)
    defender_side = get_side_from_state(mutator.state, defender_string)

    if move[constants.ID] == 'defog':
        if mutator.state.field is not None:
            instruction_additions.append(
                (
                    constants.MUTATOR_FIELD_END,
                    mutator.state.field
                )
            )
        for side_condition, amount in attacker_side.side_conditions.items():
            if amount > 0 and side_condition in constants.DEFOG_CLEARS:
                instruction_additions.append(
                    (
                        constants.MUTATOR_SIDE_END,
                        attacker_string,
                        side_condition,
                        amount
                    )
                )
        for side_condition, amount in defender_side.side_conditions.items():
            if amount > 0 and side_condition in constants.DEFOG_CLEARS:
                instruction_additions.append(
                    (
                        constants.MUTATOR_SIDE_END,
                        defender_string,
                        side_condition,
                        amount
                    )
                )

    # ghost-type misses are dealt with by freezing the state. i.e. this elif will not be reached if the move missed
    elif move[constants.ID] == 'rapidspin':
        side = get_side_from_state(mutator.state, attacker_string)
        for side_condition, amount in side.side_conditions.items():
            if amount > 0 and side_condition in constants.RAPID_SPIN_CLEARS:
                instruction_additions.append(
                    (
                        constants.MUTATOR_SIDE_END,
                        attacker_string,
                        side_condition,
                        amount
                    )
                )
    elif move[constants.ID] == constants.COURT_CHANGE:
        sides = [
            (constants.USER, mutator.state.user),
            (constants.OPPONENT, mutator.state.opponent)
        ]
        for side_name, side_object in sides:
            for side_condition in side_object.side_conditions:
                if side_object.side_conditions[side_condition] and side_condition in constants.COURT_CHANGE_SWAPS:
                    instruction_additions.append(
                        (
                            constants.MUTATOR_SIDE_END,
                            side_name,
                            side_condition,
                            side_object.side_conditions[side_condition]
                        )
                    )
                    instruction_additions.append(
                        (
                            constants.MUTATOR_SIDE_START,
                            opposite_side[side_name],
                            side_condition,
                            side_object.side_conditions[side_condition]
                        )
                    )

    else:
        raise ValueError("{} is not a hazard clearing move".format(move[constants.ID]))

    mutator.reverse(instruction.instructions)
    for i in instruction_additions:
        instruction.add_instruction(i)

    return [instruction]


def get_instructions_from_status_effects(mutator, defender, status, accuracy, instruction):
    """Returns the possible states from status effects"""
    if instruction.frozen or status is None:
        return [instruction]

    if defender not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}".format(', '.join(opposite_side)))

    instructions = []
    if accuracy is True:
        accuracy = 100
    percent_hit = accuracy / 100

    mutator.apply(instruction.instructions)
    instruction_additions = []
    defending_side = get_side_from_state(mutator.state, defender)
    attacking_side = get_side_from_state(mutator.state, opposite_side[defender])

    if sleep_clause_activated(defending_side, status):
        mutator.reverse(instruction.instructions)
        return [instruction]

    if immune_to_status(mutator.state, defending_side.active, attacking_side.active, status):
        mutator.reverse(instruction.instructions)
        return [instruction]

    move_missed_instruction = copy(instruction)
    if percent_hit > 0:
        move_hit_instruction = (
            constants.MUTATOR_APPLY_STATUS,
            defender,
            status
        )

        instruction_additions.append(move_hit_instruction)
        instruction.update_percentage(percent_hit)
        instructions.append(instruction)

    if percent_hit < 1:
        move_missed_instruction.frozen = True
        move_missed_instruction.update_percentage(1 - percent_hit)
        if attacking_side.active.item == 'blunderpolicy':
            blunder_policy_increase_speed_instruction = (
                constants.MUTATOR_BOOST,
                opposite_side[defender],
                constants.SPEED,
                2
            )
            move_missed_instruction.add_instruction(blunder_policy_increase_speed_instruction)
        instructions.append(move_missed_instruction)

    mutator.reverse(instruction.instructions)
    for i in instruction_additions:
        instruction.add_instruction(i)

    return instructions


def get_instructions_from_boosts(mutator, side_string, boosts, accuracy, instruction):
    if instruction.frozen or not boosts:
        return [instruction]

    if side_string not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}. Value: {}".format(
            ', '.join(opposite_side),
            side_string
        )
        )

    instructions = []
    if accuracy is True:
        accuracy = 100
    percent_hit = accuracy / 100

    mutator.apply(instruction.instructions)
    side = get_side_from_state(mutator.state, side_string)
    if side.active.ability in constants.IMMUNE_TO_STAT_LOWERING_ABILITIES:
        mutator.reverse(instruction.instructions)
        return [instruction]

    instruction_additions = []
    move_missed_instruction = copy(instruction)
    if percent_hit > 0:
        for k, v in boosts.items():
            pkmn_boost = get_boost_from_boost_string(side, k)
            if v > 0:
                new_boost = pkmn_boost + v
                if new_boost > constants.MAX_BOOSTS:
                    new_boost = constants.MAX_BOOSTS
                boost_instruction = (
                    constants.MUTATOR_BOOST,
                    side_string,
                    k,
                    new_boost - pkmn_boost
                )
            else:
                new_boost = pkmn_boost + v
                if new_boost < -1 * constants.MAX_BOOSTS:
                    new_boost = -1 * constants.MAX_BOOSTS
                boost_instruction = (
                    constants.MUTATOR_BOOST,
                    side_string,
                    k,
                    new_boost - pkmn_boost
                )
            instruction_additions.append(boost_instruction)

        instruction.update_percentage(percent_hit)
        instructions.append(instruction)

    if percent_hit < 1:
        move_missed_instruction.update_percentage(1 - percent_hit)
        instructions.append(move_missed_instruction)

    mutator.reverse(instruction.instructions)
    for i in instruction_additions:
        instruction.add_instruction(i)

    return instructions


def get_instructions_from_flinching_moves(defender, accuracy, first_move, instruction):
    if instruction.frozen or not first_move:
        return [instruction]

    if defender not in opposite_side:
        raise ValueError("attacker parameter must be one of: {}".format(', '.join(opposite_side)))

    instructions = []
    if accuracy is True:
        accuracy = 100
    percent_hit = accuracy / 100

    if percent_hit > 0:
        flinched_instruction = copy(instruction)
        flinch_mutator_instruction = (
            constants.MUTATOR_APPLY_VOLATILE_STATUS,
            defender,
            constants.FLINCH
        )
        flinched_instruction.add_instruction(flinch_mutator_instruction)
        flinched_instruction.update_percentage(percent_hit)
        instructions.append(flinched_instruction)

    if percent_hit < 1:
        instruction.update_percentage(1 - percent_hit)
        instructions.append(instruction)

    return instructions


def get_instructions_from_attacker_recovery(mutator, attacker_string, move, instruction):
    if instruction.frozen:
        return [instruction]

    mutator.apply(instruction.instructions)

    target = move[constants.HEAL_TARGET]
    if target in opposing_side_strings:
        side_string = opposite_side[attacker_string]
    else:
        side_string = attacker_string

    pkmn = get_side_from_state(mutator.state, side_string).active
    try:
        health_recovered = float(move[constants.HEAL][0] / move[constants.HEAL][1]) * pkmn.maxhp
    except KeyError:
        health_recovered = 0

    if health_recovered == 0:
        mutator.reverse(instruction.instructions)
        return [instruction]

    final_health = pkmn.hp + health_recovered
    if final_health > pkmn.maxhp:
        health_recovered -= (final_health - pkmn.maxhp)
    elif final_health < 0:
        health_recovered -= final_health

    heal_instruction = (
        constants.MUTATOR_HEAL,
        side_string,
        health_recovered
    )

    mutator.reverse(instruction.instructions)

    if health_recovered:
        instruction.add_instruction(heal_instruction)

    return [instruction]


def get_end_of_turn_instructions(mutator, instruction, bot_move, opponent_move, bot_moves_first):
    # determine which goes first
    if bot_moves_first:
        sides = [constants.USER, constants.OPPONENT]
    else:
        sides = [constants.OPPONENT, constants.USER]

    mutator.apply(instruction.instructions)

    # weather damage - sand and hail
    for attacker in sides:
        side = get_side_from_state(mutator.state, attacker)
        pkmn = side.active

        if pkmn.ability == 'magicguard' or not pkmn.hp:
            continue

        if mutator.state.weather == constants.SAND and not any(t in pkmn.types for t in ['steel', 'rock', 'ground']):
            sand_damage_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                max(0, int(min(pkmn.maxhp * 0.0625, pkmn.hp)))
            )
            mutator.apply_one(sand_damage_instruction)
            instruction.add_instruction(sand_damage_instruction)

        elif mutator.state.weather == constants.HAIL and 'ice' not in pkmn.types and pkmn.ability != 'icebody':
            ice_damage_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                max(0, int(min(pkmn.maxhp * 0.0625, pkmn.hp)))
            )
            mutator.apply_one(ice_damage_instruction)
            instruction.add_instruction(ice_damage_instruction)

    # futuresight
    for attacker in sides:
        side = get_side_from_state(mutator.state, attacker)
        if side.future_sight[0] == 1:
            from showdown.engine.damage_calculator import calculate_futuresight_damage
            damage_dealt = calculate_futuresight_damage(
                mutator.state,
                attacker,
                side.future_sight[1]
            )[0]
            if damage_dealt:
                futuresight_damage_instruction = (
                    constants.MUTATOR_DAMAGE,
                    opposite_side[attacker],
                    damage_dealt
                )
                mutator.apply_one(futuresight_damage_instruction)
                instruction.add_instruction(futuresight_damage_instruction)
        if side.future_sight[0] > 0:
            futuresight_decrement_instruction = (
                constants.MUTATOR_FUTURESIGHT_DECREMENT,
                attacker,
            )
            mutator.apply_one(futuresight_decrement_instruction)
            instruction.add_instruction(futuresight_decrement_instruction)

    # wish
    for attacker in sides:
        side = get_side_from_state(mutator.state, attacker)
        if side.wish[0] == 1 and 0 < side.active.hp < side.active.maxhp:
            wish_heal_instruction = (
                constants.MUTATOR_HEAL,
                attacker,
                min(side.wish[1], side.active.maxhp - side.active.hp)
            )
            mutator.apply_one(wish_heal_instruction)
            instruction.add_instruction(wish_heal_instruction)
        if side.wish[0] > 0:
            wish_decrement_instruction = (
                constants.MUTATOR_WISH_DECREMENT,
                attacker
            )
            mutator.apply_one(wish_decrement_instruction)
            instruction.add_instruction(wish_decrement_instruction)

    # item and ability - they can add one instruction each
    for attacker in sides:
        defender = opposite_side[attacker]
        side = get_side_from_state(mutator.state, attacker)
        defending_side = get_side_from_state(mutator.state, defender)
        pkmn = side.active
        defending_pkmn = defending_side.active

        item_instruction = item_end_of_turn(side.active.item, mutator.state, attacker, pkmn, defender, defending_pkmn)
        if item_instruction is not None:
            mutator.apply_one(item_instruction)
            instruction.add_instruction(item_instruction)

        ability_instruction = ability_end_of_turn(side.active.ability, mutator.state, attacker, pkmn, defender, defending_pkmn)
        if ability_instruction is not None:
            mutator.apply_one(ability_instruction)
            instruction.add_instruction(ability_instruction)

    # poison, toxic, and burn damage
    for attacker in sides:
        side = get_side_from_state(mutator.state, attacker)
        pkmn = side.active

        if pkmn.ability == 'magicguard' or not pkmn.hp:
            continue

        if constants.TOXIC == pkmn.status and pkmn.ability != 'poisonheal':
            toxic_count = side.side_conditions[constants.TOXIC_COUNT]
            toxic_multiplier = (1 / 16) * toxic_count + (1 / 16)
            toxic_damage = max(0, int(min(pkmn.maxhp * toxic_multiplier, pkmn.hp)))

            toxic_damage_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                toxic_damage
            )
            toxic_count_instruction = (
                constants.MUTATOR_SIDE_START,
                attacker,
                constants.TOXIC_COUNT,
                1
            )
            mutator.apply_one(toxic_damage_instruction)
            mutator.apply_one(toxic_count_instruction)

            instruction.add_instruction(toxic_damage_instruction)
            instruction.add_instruction(toxic_count_instruction)

        elif constants.BURN == pkmn.status:
            burn_damage_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                max(0, int(min(pkmn.maxhp * 0.0625, pkmn.hp)))
            )
            mutator.apply_one(burn_damage_instruction)
            instruction.add_instruction(burn_damage_instruction)

        elif constants.POISON == pkmn.status and pkmn.ability != 'poisonheal':
            poison_damage_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                max(0, int(min(pkmn.maxhp * 0.125, pkmn.hp)))
            )
            mutator.apply_one(poison_damage_instruction)
            instruction.add_instruction(poison_damage_instruction)

    # leechseed sap damage
    for attacker in sides:
        defender = opposite_side[attacker]
        side = get_side_from_state(mutator.state, attacker)
        defending_side = get_side_from_state(mutator.state, defender)
        pkmn = side.active
        defending_pkmn = defending_side.active

        if pkmn.ability == 'magicguard' or not pkmn.hp or not defending_pkmn.hp:
            continue

        if constants.LEECH_SEED in pkmn.volatile_status:
            # damage taken
            damage_sapped = max(0, int(min(pkmn.maxhp * 0.125, pkmn.hp)))
            sap_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                damage_sapped
            )

            # heal amount
            damage_from_full = defending_pkmn.maxhp - defending_pkmn.hp
            heal_instruction = (
                constants.MUTATOR_HEAL,
                defender,
                min(damage_sapped, damage_from_full)
            )

            mutator.apply_one(sap_instruction)
            mutator.apply_one(heal_instruction)
            instruction.add_instruction(sap_instruction)
            instruction.add_instruction(heal_instruction)

    # volatile-statuses
    for attacker in sides:
        side = get_side_from_state(mutator.state, attacker)
        pkmn = side.active

        if any(vs in constants.PROTECT_VOLATILE_STATUSES for vs in pkmn.volatile_status):
            if constants.PROTECT in pkmn.volatile_status:
                volatile_status_to_remove = constants.PROTECT
            elif constants.BANEFUL_BUNKER in pkmn.volatile_status:
                volatile_status_to_remove = constants.BANEFUL_BUNKER
            elif constants.SPIKY_SHIELD in pkmn.volatile_status:
                volatile_status_to_remove = constants.SPIKY_SHIELD
            else:
                # should never happen
                raise Exception("Pokemon has volatile status that is not caught here: {}".format(pkmn.volatile_status))

            remove_protect_volatile_status_instruction = (
                constants.MUTATOR_REMOVE_VOLATILE_STATUS,
                attacker,
                volatile_status_to_remove
            )
            start_protect_side_condition_instruction = (
                    constants.MUTATOR_SIDE_START,
                    attacker,
                    constants.PROTECT,
                    1
            )
            mutator.apply_one(remove_protect_volatile_status_instruction)
            mutator.apply_one(start_protect_side_condition_instruction)
            instruction.add_instruction(remove_protect_volatile_status_instruction)
            instruction.add_instruction(start_protect_side_condition_instruction)

        elif side.side_conditions[constants.PROTECT]:
            end_protect_side_condition_instruction = (
                constants.MUTATOR_SIDE_END,
                attacker,
                constants.PROTECT,
                side.side_conditions[constants.PROTECT]
            )
            mutator.apply_one(end_protect_side_condition_instruction)
            instruction.add_instruction(end_protect_side_condition_instruction)

        if constants.ROOST in pkmn.volatile_status:
            remove_roost_instruction = (
                constants.MUTATOR_REMOVE_VOLATILE_STATUS,
                attacker,
                constants.ROOST,
            )
            mutator.apply_one(remove_roost_instruction)
            instruction.add_instruction(remove_roost_instruction)

        if constants.PARTIALLY_TRAPPED in pkmn.volatile_status:
            damage_taken = max(0, int(min(pkmn.maxhp * 0.125, pkmn.hp)))
            partially_trapped_damage_instruction = (
                constants.MUTATOR_DAMAGE,
                attacker,
                damage_taken
            )
            mutator.apply_one(partially_trapped_damage_instruction)
            instruction.add_instruction(partially_trapped_damage_instruction)

    # disable not used moves if choice-item is held
    for attacker in sides:
        side = get_side_from_state(mutator.state, attacker)
        pkmn = side.active

        if attacker == constants.USER:
            move = bot_move
            other_move = opponent_move
        else:
            move = opponent_move
            other_move = bot_move

        try:
            locking_move = move[constants.SELF][constants.VOLATILE_STATUS] == constants.LOCKED_MOVE
        except KeyError:
            locking_move = False

        if (
            constants.SWITCH_STRING not in move and
            constants.DRAG not in other_move.get(constants.FLAGS, {}) and
            move[constants.ID] not in constants.SWITCH_OUT_MOVES and
            (pkmn.item in constants.CHOICE_ITEMS or locking_move or pkmn.ability == 'gorillatactics')
        ):
            move_used = move[constants.ID]
            for m in filter(lambda x: x[constants.ID] != move_used and not x[constants.DISABLED], pkmn.moves):
                disable_instruction = (
                    constants.MUTATOR_DISABLE_MOVE,
                    attacker,
                    m[constants.ID]
                )
                mutator.apply_one(disable_instruction)
                instruction.add_instruction(disable_instruction)

    mutator.reverse(instruction.instructions)

    return [instruction]


def get_instructions_from_drag(mutator, attacking_side_string, move_target, instruction):
    if instruction.frozen:
        return [instruction]

    new_instructions = []

    if move_target in same_side_strings:
        affected_side = get_side_from_state(mutator.state, attacking_side_string)
        affected_side_string = attacking_side_string
    elif move_target in opposing_side_strings:
        affected_side = get_side_from_state(mutator.state, opposite_side[attacking_side_string])
        affected_side_string = opposite_side[attacking_side_string]
    else:
        raise ValueError("Invalid value for move_target: {}".format(move_target))

    mutator.apply(instruction.instructions)
    alive_reserves = [s.id for s in affected_side.reserve.values() if s.hp > 0]
    num_reserve_alive = len(alive_reserves)
    mutator.reverse(instruction.instructions)
    if num_reserve_alive == 0:
        return [instruction]

    for pkmn_name in alive_reserves:
        new_instruction = get_instructions_from_switch(mutator, affected_side_string, pkmn_name, copy(instruction))
        new_instruction.update_percentage(1 / num_reserve_alive)
        new_instructions.append(new_instruction)

    return new_instructions


def get_instructions_from_boost_reset_moves(mutator, attacking_move, attacking_side_string, instruction):
    if instruction.frozen:
        return [instruction]

    attacking_side = get_side_from_state(mutator.state, attacking_side_string)
    defending_side_string = opposite_side[attacking_side_string]
    defending_side = get_side_from_state(mutator.state, defending_side_string)

    mutator.apply(instruction.instructions)
    new_instructions = []
    if attacking_move[constants.TARGET] in constants.MOVE_TARGET_SELF:
        new_instructions += remove_volatile_status_and_boosts_instructions(attacking_side, attacking_side_string)
    if attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
        new_instructions += remove_volatile_status_and_boosts_instructions(defending_side, defending_side_string)
    mutator.reverse(instruction.instructions)

    for new_instruction in new_instructions:
        instruction.add_instruction(new_instruction)

    return [instruction]


def remove_volatile_status_and_boosts_instructions(side, side_string):
    instruction_additions = []
    for v_status in side.active.volatile_status:
        instruction_additions.append(
            (
                constants.MUTATOR_REMOVE_VOLATILE_STATUS,
                side_string,
                v_status
            )
        )
    if side.side_conditions[constants.TOXIC_COUNT]:
        instruction_additions.append(
            (
                constants.MUTATOR_SIDE_END,
                side_string,
                constants.TOXIC_COUNT,
                side.side_conditions[constants.TOXIC_COUNT]
            ))
    if side.active.attack_boost:
        instruction_additions.append(
            (
                constants.MUTATOR_UNBOOST,
                side_string,
                constants.ATTACK,
                side.active.attack_boost
            ))
    if side.active.defense_boost:
        instruction_additions.append(
            (
                constants.MUTATOR_UNBOOST,
                side_string,
                constants.DEFENSE,
                side.active.defense_boost
            ))
    if side.active.special_attack_boost:
        instruction_additions.append(
            (
                constants.MUTATOR_UNBOOST,
                side_string,
                constants.SPECIAL_ATTACK,
                side.active.special_attack_boost
            ))
    if side.active.special_defense_boost:
        instruction_additions.append(
            (
                constants.MUTATOR_UNBOOST,
                side_string,
                constants.SPECIAL_DEFENSE,
                side.active.special_defense_boost
            ))
    if side.active.speed_boost:
        instruction_additions.append(
            (
                constants.MUTATOR_UNBOOST,
                side_string,
                constants.SPEED,
                side.active.speed_boost
            ))

    return instruction_additions


def get_side_from_state(state, side_string):
    if side_string == constants.USER:
        return state.user
    elif side_string == constants.OPPONENT:
        return state.opponent
    else:
        raise ValueError("Invalid value for `side`")


def get_boost_from_boost_string(side, boost_string):
    if boost_string == constants.ATTACK:
        return side.active.attack_boost
    elif boost_string == constants.DEFENSE:
        return side.active.defense_boost
    elif boost_string == constants.SPECIAL_ATTACK:
        return side.active.special_attack_boost
    elif boost_string == constants.SPECIAL_DEFENSE:
        return side.active.special_defense_boost
    elif boost_string == constants.SPEED:
        return side.active.speed_boost
    elif boost_string == constants.ACCURACY:
        return side.active.accuracy_boost
    elif boost_string == constants.EVASION:
        return side.active.evasion_boost
    raise ValueError("{} is not a valid boost".format(boost_string))


def can_be_volatile_statused(side, volatile_status, first_move):
    if volatile_status in constants.PROTECT_VOLATILE_STATUSES:
        if side.side_conditions[constants.PROTECT]:
            return False
        elif first_move:
            return True
        else:
            return False
    if constants.SUBSTITUTE in side.active.volatile_status:
        return False
    if volatile_status == constants.SUBSTITUTE and side.active.hp < side.active.maxhp * 0.25:
        return False

    return True


def sleep_clause_activated(side, status):
    return status == constants.SLEEP and constants.SLEEP in [p.status for p in side.reserve.values()]


def immune_to_status(state, defending_pkmn, attacking_pkmn, status):
    # General status immunity
    if defending_pkmn.status is not None or defending_pkmn.hp <= 0:
        return True
    if constants.SUBSTITUTE in defending_pkmn.volatile_status and attacking_pkmn.ability != 'infiltrator':
        return True
    if defending_pkmn.ability == 'shieldsdown' and ((defending_pkmn.hp / defending_pkmn.maxhp) > 0.5):
        return True
    if defending_pkmn.ability == 'comatose':
        return True
    if state.field == constants.MISTY_TERRAIN and defending_pkmn.is_grounded():
        return True

    # Specific status immunity
    return (
        status == constants.FROZEN and is_immune_to_freeze(state, defending_pkmn) or
        status == constants.BURN and is_immune_to_burn(defending_pkmn) or
        status == constants.SLEEP and is_immune_to_sleep(state, defending_pkmn) or
        status == constants.PARALYZED and is_immune_to_paralysis(defending_pkmn) or
        status in [constants.POISON, constants.TOXIC] and is_immune_to_poison(attacking_pkmn, defending_pkmn)
    )


def is_immune_to_freeze(state, pkmn):
    return (
        'ice' in pkmn.types or 
        pkmn.ability in constants.IMMUNE_TO_FROZEN_ABILITIES or 
        state.weather == constants.DESOLATE_LAND
    )


def is_immune_to_burn(pkmn):
    return (
        'fire' in pkmn.types or
        pkmn.ability in constants.IMMUNE_TO_BURN_ABILITIES
    )


def is_immune_to_sleep(state, pkmn):
    return (
        pkmn.ability in constants.IMMUNE_TO_SLEEP_ABILITIES or
        state.field == constants.ELECTRIC_TERRAIN and pkmn.is_grounded()
    )


def is_immune_to_poison(attacking, defending):
    return (
        any(t in ['poison', 'steel'] for t in defending.types) and not attacking.ability == 'corrosion'  or
        defending.ability in constants.IMMUNE_TO_POISON_ABILITIES
    )


def is_immune_to_paralysis(pkmn):
    return (
        'electric' in pkmn.types or 
        pkmn.ability in constants.IMMUNE_TO_PARALYSIS_ABILITIES
    )
