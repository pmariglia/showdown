import constants


class StateMutator:

    def __init__(self, state):
        self.state = state
        self.apply_instructions = {
            constants.MUTATOR_SWITCH: self.switch,
            constants.MUTATOR_APPLY_VOLATILE_STATUS: self.apply_volatile_status,
            constants.MUTATOR_REMOVE_VOLATILE_STATUS: self.remove_volatile_status,
            constants.MUTATOR_DAMAGE: self.damage,
            constants.MUTATOR_HEAL: self.heal,
            constants.MUTATOR_BOOST: self.boost,
            constants.MUTATOR_UNBOOST: self.unboost,
            constants.MUTATOR_APPLY_STATUS: self.apply_status,
            constants.MUTATOR_REMOVE_STATUS: self.remove_status,
            constants.MUTATOR_SIDE_START: self.side_start,
            constants.MUTATOR_SIDE_END: self.side_end,
            constants.MUTATOR_DISABLE_MOVE: self.disable_move,
            constants.MUTATOR_ENABLE_MOVE: self.enable_move,
        }
        self.reverse_instructions = {
            constants.MUTATOR_SWITCH: self.reverse_switch,
            constants.MUTATOR_APPLY_VOLATILE_STATUS: self.remove_volatile_status,
            constants.MUTATOR_REMOVE_VOLATILE_STATUS: self.apply_volatile_status,
            constants.MUTATOR_DAMAGE: self.heal,
            constants.MUTATOR_HEAL: self.damage,
            constants.MUTATOR_BOOST: self.unboost,
            constants.MUTATOR_UNBOOST: self.boost,
            constants.MUTATOR_APPLY_STATUS: self.remove_status,
            constants.MUTATOR_REMOVE_STATUS: self.apply_status,
            constants.MUTATOR_SIDE_START: self.reverse_side_start,
            constants.MUTATOR_SIDE_END: self.reverse_side_end,
            constants.MUTATOR_DISABLE_MOVE: self.enable_move,
            constants.MUTATOR_ENABLE_MOVE: self.disable_move,
        }

    def apply(self, instructions):
        for instruction in instructions:
            method = self.apply_instructions[instruction[0]]
            method(*instruction[1:])

    def reverse(self, instructions):
        for instruction in reversed(instructions):
            method = self.reverse_instructions[instruction[0]]
            method(*instruction[1:])

    def _get_side(self, side):
        if side == constants.SELF:
            return self.state.self
        elif side == constants.OPPONENT:
            return self.state.opponent
        else:
            raise ValueError("Invalid value for `side`")

    def disable_move(self, side, move_name):
        side = self._get_side(side)
        try:
            move = next(filter(lambda x: x[constants.ID] == move_name, side.active.moves))
        except StopIteration:
            raise ValueError("{} not in pokemon's moves: {}".format(move_name, side.active.moves))

        move[constants.DISABLED] = True

    def enable_move(self, side, move_name):
        side = self._get_side(side)
        try:
            move = next(filter(lambda x: x[constants.ID] == move_name, side.active.moves))
        except StopIteration:
            raise ValueError("{} not in pokemon's moves: {}".format(move_name, side.active.moves))

        move[constants.DISABLED] = False

    def switch(self, side, _, switch_pokemon_name):
        # the second parameter to this function is the current active pokemon
        # this value must be here for reversing purposes
        side = self._get_side(side)

        side.reserve[side.active.id] = side.active
        side.active = side.reserve.pop(switch_pokemon_name)

    def reverse_switch(self, side, previous_active, current_active):
        self.switch(side, current_active, previous_active)

    def apply_volatile_status(self, side, volatile_status):
        side = self._get_side(side)
        side.active.volatile_status.add(volatile_status)

    def remove_volatile_status(self, side, volatile_status):
        side = self._get_side(side)
        side.active.volatile_status.remove(volatile_status)

    def damage(self, side, amount):
        side = self._get_side(side)
        side.active.hp -= amount

    def heal(self, side, amount):
        side = self._get_side(side)
        side.active.hp += amount

    def boost(self, side, stat, amount):
        side = self._get_side(side)
        if stat == constants.ATTACK:
            side.active.attack_boost += amount
        elif stat == constants.DEFENSE:
            side.active.defense_boost += amount
        elif stat == constants.SPECIAL_ATTACK:
            side.active.special_attack_boost += amount
        elif stat == constants.SPECIAL_DEFENSE:
            side.active.special_defense_boost += amount
        elif stat == constants.SPEED:
            side.active.speed_boost += amount
        elif stat == constants.ACCURACY:
            side.active.accuracy_boost += amount
        elif stat == constants.EVASION:
            side.active.evasion_boost += amount
        else:
            raise ValueError("Invalid stat: {}".format(stat))

    def unboost(self, side, stat, amount):
        self.boost(side, stat, -1*amount)

    def apply_status(self, side, status):
        side = self._get_side(side)
        side.active.status = status

    def remove_status(self, side, _):
        # the second parameter of this function is the status being removed
        # this value must be here for reverse purposes
        self.apply_status(side, None)

    def side_start(self, side, effect, amount):
        side = self._get_side(side)
        side.side_conditions[effect] += amount

    def reverse_side_start(self, side, effect, amount):
        side = self._get_side(side)
        side.side_conditions[effect] -= amount

    def side_end(self, side, effect, _):
        # the third parameter of this function is the amount being removed
        # this value must be here for reverse purposes
        side = self._get_side(side)
        side.side_conditions[effect] = 0

    def reverse_side_end(self, side, effect, amount):
        self.side_start(side, effect, amount)
