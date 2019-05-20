import constants
from copy import copy
from config import logger
from showdown.calculate_damage import damage_multipication_array
from showdown.calculate_damage import pokemon_type_indicies


class InstructionGenerator:

    def __init__(self):
        self.possible_affected_strings = {
            constants.SELF: constants.OPPONENT,
            constants.OPPONENT: constants.SELF
        }
        self.same_side_strings = [
            constants.SELF,
            constants.ALLY_SIDE
        ]
        self.opposing_side_strings = [
            constants.NORMAL,
            constants.OPPONENT,
            constants.FOESIDE,
            constants.ALL_ADJACENT_FOES,
            constants.ALL_ADJACENT,
            constants.ALL,
        ]

    def get_state_from_volatile_status(self, mutator, volatile_status, attacker, affected_side, instruction):
        if instruction.frozen or not volatile_status:
            return [instruction]

        if affected_side in self.same_side_strings:
            affected_side = attacker
        elif affected_side in self.opposing_side_strings:
            affected_side = self.possible_affected_strings[attacker]
        else:
            logger.critical("Invalid affected_side: {}".format(affected_side))
            return [instruction]

        side = self.get_side_from_state(mutator.state, affected_side)
        mutator.apply(instruction.instructions)
        if volatile_status in side.active.volatile_status:
            mutator.reverse(instruction.instructions)
            return [instruction]

        if self._can_be_statused(side.active, volatile_status) and volatile_status not in side.active.volatile_status:
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

    def get_instructions_from_switch(self, mutator, attacker, switch_pokemon_name, instructions):
        if attacker not in self.possible_affected_strings:
            raise ValueError("attacker parameter must be one of: {}".format(', '.join(self.possible_affected_strings)))

        side = self.get_side_from_state(mutator.state, attacker)
        mutator.apply(instructions.instructions)
        instruction_additions = self.remove_volatile_status_and_boosts_instructions(side, attacker)

        for move in filter(lambda x: x[constants.DISABLED] is True and x[constants.CURRENT_PP], side.active.moves):
            instruction_additions.append(
                (
                    constants.MUTATOR_ENABLE_MOVE,
                    attacker,
                    move[constants.ID]
                )
            )

        if side.active.ability == 'regenerator' and side.active.hp:
            hp_missing = side.active.maxhp - side.active.hp
            instruction_additions.append(
                (
                    constants.MUTATOR_HEAL,
                    attacker,
                    int(min(1 / 3 * side.active.maxhp, hp_missing))
                )
            )

        instruction_additions.append(
            (
                constants.MUTATOR_SWITCH,
                attacker,
                side.active.id,
                switch_pokemon_name
            )
        )

        switch_pkmn = side.reserve[switch_pokemon_name]
        # account for stealth rock damage
        if side.side_conditions[constants.STEALTH_ROCK] == 1:
            multiplier = 1
            rock_type_index = pokemon_type_indicies['rock']
            for pkmn_type in switch_pkmn.types:
                multiplier *= damage_multipication_array[rock_type_index][pokemon_type_indicies[pkmn_type]]

            instruction_additions.append(
                (
                    constants.MUTATOR_DAMAGE,
                    attacker,
                    min(1 / 8 * multiplier * switch_pkmn.maxhp, switch_pkmn.hp)
                )
            )

        # account for spikes damage
        if side.side_conditions[constants.SPIKES] > 0 and switch_pkmn.is_grounded():
            spike_count = side.side_conditions[constants.SPIKES]
            instruction_additions.append(
                (
                    constants.MUTATOR_DAMAGE,
                    attacker,
                    min(1 / 8 * spike_count * switch_pkmn.maxhp, switch_pkmn.hp)
                )
            )

        # account for stickyweb speed drop
        if side.side_conditions[constants.STICKY_WEB] == 1 and switch_pkmn.is_grounded():
            instruction_additions.append(
                (
                    constants.MUTATOR_UNBOOST,
                    attacker,
                    constants.SPEED,
                    1
                )
            )

        # account for toxic spikes effect
        if side.side_conditions[constants.TOXIC_SPIKES] >= 1 and switch_pkmn.is_grounded():
            if not self._immune_to_status(switch_pkmn, constants.POISON):
                if side.side_conditions[constants.TOXIC_SPIKES] == 1:
                    instruction_additions.append(
                        (
                            constants.MUTATOR_APPLY_STATUS,
                            attacker,
                            constants.POISON
                        )
                    )
                elif side.side_conditions[constants.TOXIC_SPIKES] == 2:
                    instruction_additions.append(
                        (
                            constants.MUTATOR_APPLY_STATUS,
                            attacker,
                            constants.TOXIC
                        )
                    )
            elif 'poison' in switch_pkmn.types:
                instruction_additions.append(
                    (
                        constants.MUTATOR_SIDE_END,
                        attacker,
                        constants.TOXIC_SPIKES,
                        side.side_conditions[constants.TOXIC_SPIKES]
                    )
                )

        mutator.reverse(instructions.instructions)
        for i in instruction_additions:
            instructions.add_instruction(i)

        return [instructions]

    def get_instructions_from_flinched(self, mutator, attacker, instruction):
        """If the attacker has been flinched, freeze the state so that nothing happens"""
        if attacker not in self.possible_affected_strings:
            raise ValueError("attacker parameter must be one of: {}".format(', '.join(self.possible_affected_strings)))

        mutator.apply(instruction.instructions)

        side = self.get_side_from_state(mutator.state, attacker)
        if constants.FLINCH in side.active.volatile_status:
            remove_flinch_instruction = (
                                constants.MUTATOR_REMOVE_VOLATILE_STATUS,
                                attacker,
                                constants.FLINCH
                            )
            mutator.reverse(instruction.instructions)
            instruction.add_instruction(remove_flinch_instruction)
            instruction.frozen = True
            return [instruction]
        else:
            mutator.reverse(instruction.instructions)
            return [instruction]

    def get_instructions_from_statuses_that_freeze_the_state(self, mutator, attacker, defender, move, instruction):
        instructions = [instruction]
        attacker_side = self.get_side_from_state(mutator.state, attacker)
        defender_side = self.get_side_from_state(mutator.state, defender)

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
            instructions.append(still_asleep_instruction)

        elif constants.FROZEN == attacker_side.active.status:
            still_frozen_instruction = copy(instruction)
            still_frozen_instruction.update_percentage(1 - constants.THAW_PERCENT)
            still_frozen_instruction.frozen = True
            instruction.update_percentage(constants.THAW_PERCENT)
            instructions.append(still_frozen_instruction)

        if constants.POWDER in move[constants.FLAGS] and 'grass' in defender_side.active.types:
            instruction.frozen = True

        mutator.reverse(instruction.instructions)

        return instructions

    def get_states_from_damage(self, mutator, defender, damage, accuracy, drain, recoil, crash, instruction):
        """Given self.state, generate multiple states based on all of the possible damage combinations
           This versions assumes that all damage deals a constant amount
           The different states are based on whether or not the attack misses

           To make this deal with multiple potential damage rolls, change `damage` to a list and iterate over it
           """

        attacker = self.possible_affected_strings[defender]
        attacker_side = self.get_side_from_state(mutator.state, attacker)
        damage_side = self.get_side_from_state(mutator.state, defender)

        # `damage is None` means that the move does not deal damage
        # for example, will-o-wisp
        if instruction.frozen or damage is None:
            return [instruction]

        # `damage == 0` means that the move deals damage, but not in this situation
        # for example: using Return against a Ghost-type
        # the state must be frozen because any secondary effects must not take place
        if damage == 0:
            if crash:
                crash_percent = crash[0] / crash[1]
                crash_instruction = (
                    constants.MUTATOR_DAMAGE,
                    attacker,
                    int(crash_percent * attacker_side.active.maxhp)
                )
                instruction.add_instruction(crash_instruction)
            instruction.frozen = True
            return [instruction]

        if defender not in self.possible_affected_strings:
            raise ValueError("attacker parameter must be one of: {}".format(', '.join(self.possible_affected_strings)))

        instructions = []
        if accuracy is True:
            accuracy = 100
        percent_hit = accuracy / 100

        mutator.apply(instruction.instructions)

        instruction_additions = []
        move_missed_instruction = copy(instruction)
        if percent_hit > 0:
            if constants.SUBSTITUTE in damage_side.active.volatile_status:
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
                actual_damage = min(damage, damage_side.active.hp)
                instruction_additions.append(
                    (
                        constants.MUTATOR_DAMAGE,
                        defender,
                        actual_damage
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

            instructions.append(instruction)

        if percent_hit < 1:
            move_missed_instruction.frozen = True
            move_missed_instruction.update_percentage(1-percent_hit)
            if crash:
                crash_percent = crash[0] / crash[1]
                crash_instruction = (
                    constants.MUTATOR_DAMAGE,
                    attacker,
                    int(crash_percent * attacker_side.active.maxhp)
                )
                move_missed_instruction.add_instruction(crash_instruction)

            instructions.append(move_missed_instruction)

        mutator.reverse(instruction.instructions)
        for i in instruction_additions:
            instruction.add_instruction(i)

        return instructions

    def get_instructions_from_side_conditions(self, mutator, attacker_string, side_string, condition, instruction):
        if instruction.frozen:
            return [instruction]

        if attacker_string not in self.possible_affected_strings:
            raise ValueError("attacker parameter must be one of: {}".format(', '.join(self.possible_affected_strings)))

        if side_string in self.same_side_strings:
            side_string = attacker_string
        elif side_string in self.opposing_side_strings:
            side_string = self.possible_affected_strings[attacker_string]
        else:
            raise ValueError("Invalid Side String: {}".format(side_string))

        instruction_additions = []
        side = self.get_side_from_state(mutator.state, side_string)
        mutator.apply(instruction.instructions)
        if condition == constants.SPIKES:
            max_layers = 3
        elif condition == constants.TOXIC_SPIKES:
            max_layers = 2
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

    def get_instructions_from_hazard_clearing_moves(self, mutator, attacker_string, move, instruction):
        if instruction.frozen:
            return [instruction]

        if attacker_string not in self.possible_affected_strings:
            raise ValueError("attacker parameter must be one of: {}".format(', '.join(self.possible_affected_strings)))

        defender_string = self.possible_affected_strings[attacker_string]

        instruction_additions = []
        mutator.apply(instruction.instructions)

        attacker_side = self.get_side_from_state(mutator.state, attacker_string)
        defender_side = self.get_side_from_state(mutator.state, defender_string)

        if move[constants.ID] == 'defog':
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
            side = self.get_side_from_state(mutator.state, attacker_string)
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
        else:
            raise ValueError("{} is not a hazard clearing move".format(move[constants.ID]))

        mutator.reverse(instruction.instructions)
        for i in instruction_additions:
            instruction.add_instruction(i)

        return [instruction]

    def get_states_from_status_effects(self, mutator, defender, status, accuracy, instruction):
        """Returns the possible states from status effects"""
        if instruction.frozen or status is None:
            return [instruction]

        if defender not in self.possible_affected_strings:
            raise ValueError("attacker parameter must be one of: {}".format(', '.join(self.possible_affected_strings)))

        instructions = []
        if accuracy is True:
            accuracy = 100
        percent_hit = accuracy / 100

        mutator.apply(instruction.instructions)
        instruction_additions = []
        side = self.get_side_from_state(mutator.state, defender)

        if self._sleep_clause_activated(side, status):
            mutator.reverse(instruction.instructions)
            return [instruction]

        if self._immune_to_status(side.active, status):
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
            move_missed_instruction.update_percentage(1-percent_hit)
            instructions.append(move_missed_instruction)

        mutator.reverse(instruction.instructions)
        for i in instruction_additions:
            instruction.add_instruction(i)

        return instructions

    def get_states_from_boosts(self, mutator, side_string, boosts, accuracy, instruction):
        if instruction.frozen or not boosts:
            return [instruction]

        if side_string not in self.possible_affected_strings:
            raise ValueError("attacker parameter must be one of: {}. Value: {}".format(
                    ', '.join(self.possible_affected_strings),
                    side_string
                )
            )

        instructions = []
        if accuracy is True:
            accuracy = 100
        percent_hit = accuracy / 100

        mutator.apply(instruction.instructions)
        instruction_additions = []

        move_missed_instruction = copy(instruction)
        side = self.get_side_from_state(mutator.state, side_string)
        if percent_hit > 0:
            for k, v in boosts.items():
                pkmn_boost = self._get_boost_from_boost_string(side, k)
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
                    if new_boost < -1*constants.MAX_BOOSTS:
                        new_boost = -1*constants.MAX_BOOSTS
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
            move_missed_instruction.update_percentage(1-percent_hit)
            instructions.append(move_missed_instruction)

        mutator.reverse(instruction.instructions)
        for i in instruction_additions:
            instruction.add_instruction(i)

        return instructions

    def get_states_from_flinching_moves(self, defender, accuracy, first_move, instruction):
        if instruction.frozen or not first_move:
            return [instruction]

        if defender not in self.possible_affected_strings:
            raise ValueError("attacker parameter must be one of: {}".format(', '.join(self.possible_affected_strings)))

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
            instruction.update_percentage(1-percent_hit)
            instructions.append(instruction)

        return instructions

    def get_state_from_attacker_recovery(self, mutator, attacker_string, move, instruction):
        if instruction.frozen:
            return [instruction]

        target = move[constants.HEAL_TARGET]
        if target in self.opposing_side_strings:
            side_string = self.possible_affected_strings[attacker_string]
        else:
            side_string = attacker_string

        pkmn = self.get_side_from_state(mutator.state, side_string).active
        try:
            health_recovered = float(move[constants.HEAL][0] / move[constants.HEAL][1]) * pkmn.maxhp
        except KeyError:
            health_recovered = 0

        if health_recovered == 0:
            return [instruction]

        mutator.apply(instruction.instructions)

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

    def get_state_from_status_damage(self, mutator, attacker, instruction):
        if attacker not in self.possible_affected_strings:
            raise ValueError("attacker parameter must be one of: {}".format(', '.join(self.possible_affected_strings)))

        mutator.apply(instruction.instructions)
        defender = self.possible_affected_strings[attacker]
        side = self.get_side_from_state(mutator.state, attacker)
        defending_side = self.get_side_from_state(mutator.state, defender)
        pkmn = side.active
        defending_pkmn = defending_side.active

        instructions_to_add = []
        if constants.TOXIC == pkmn.status:
            instructions_to_add.append(
                (
                    constants.MUTATOR_SIDE_START,
                    attacker,
                    constants.TOXIC_COUNT,
                    1
                )
            )
            toxic_count = side.side_conditions[constants.TOXIC_COUNT]
            toxic_multiplier = (1 / 16) * toxic_count + (1 / 16)
            toxic_damage = max(1, int(min(pkmn.maxhp * toxic_multiplier, pkmn.hp)))
            instructions_to_add.append(
                (
                    constants.MUTATOR_DAMAGE,
                    attacker,
                    toxic_damage
                )
            )
        elif constants.BURN == pkmn.status:
            instructions_to_add.append(
                (
                    constants.MUTATOR_DAMAGE,
                    attacker,
                    max(1, int(min(pkmn.maxhp * 0.0625, pkmn.hp)))
                )
            )
        elif constants.POISON == pkmn.status:
            instructions_to_add.append(
                (
                    constants.MUTATOR_DAMAGE,
                    attacker,
                    max(1, int(min(pkmn.maxhp * 0.125, pkmn.hp)))
                )
            )
        if constants.LEECH_SEED in pkmn.volatile_status:
            damage_sapped = max(1, int(min(pkmn.maxhp * 0.125, pkmn.hp)))
            instructions_to_add.append(
                (
                    constants.MUTATOR_DAMAGE,
                    attacker,
                    damage_sapped
                )
            )
            damage_from_full = defending_pkmn.maxhp - defending_pkmn.hp
            instructions_to_add.append(
                (
                    constants.MUTATOR_HEAL,
                    defender,
                    min(damage_sapped, damage_from_full)
                )
            )

        mutator.reverse(instruction.instructions)
        for i in instructions_to_add:
            instruction.add_instruction(i)

        return [instruction]

    def get_state_from_drag(self, mutator, attacking_move, attacking_side_string, move_target, instruction):
        if constants.DRAG not in attacking_move[constants.FLAGS] or instruction.frozen:
            return [instruction]

        if move_target in self.same_side_strings:
            affected_side = self.get_side_from_state(mutator.state, attacking_side_string)
            affected_side_string = attacking_side_string
        elif move_target in self.opposing_side_strings:
            affected_side = self.get_side_from_state(mutator.state, self.possible_affected_strings[attacking_side_string])
            affected_side_string = self.possible_affected_strings[attacking_side_string]
        else:
            raise ValueError("Invalid value for move_target: {}".format(move_target))

        mutator.apply(instruction.instructions)
        new_instructions = self.remove_volatile_status_and_boosts_instructions(affected_side, affected_side_string)
        mutator.reverse(instruction.instructions)

        for i in new_instructions:
            instruction.add_instruction(i)

        return [instruction]

    @staticmethod
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

    @staticmethod
    def get_side_from_state(state, side_string):
        if side_string == constants.SELF:
            return state.self
        elif side_string == constants.OPPONENT:
            return state.opponent
        else:
            raise ValueError("Invalid value for `side`")

    @staticmethod
    def _get_boost_from_boost_string(side, boost_string):
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
        else:
            return 0

    @staticmethod
    def _can_be_statused(pkmn, volatile_status):
        if constants.SUBSTITUTE in pkmn.volatile_status:
            return False
        if volatile_status == constants.SUBSTITUTE and pkmn.hp < pkmn.maxhp * 0.25:
            return False

        return True

    @staticmethod
    def _sleep_clause_activated(side, status):
        if status == constants.SLEEP and constants.SLEEP in [p.status for p in side.reserve.values()]:
            return True
        return False

    @staticmethod
    def _immune_to_status(pkmn, status):
        if pkmn.status is not None:
            return True
        if constants.SUBSTITUTE in pkmn.volatile_status:
            return True
        if status in [constants.POISON, constants.TOXIC] and any(t in ['poison', 'steel'] for t in pkmn.types):
            return True
        if status == constants.BURN and 'fire' in pkmn.types:
            return True
        if status == constants.PARALYZED and 'ground' in pkmn.types:
            return True

        return False
