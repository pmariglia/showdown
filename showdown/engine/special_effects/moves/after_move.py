import constants


def knockoff(state, attacker, defender, attacking_side, defending_side, move_hit, hit_sub):
    if move_hit and defending_side.active.item_can_be_removed():
        return [
            (constants.MUTATOR_CHANGE_ITEM, defender, None, defending_side.active.item)
        ]


def phantomforce(state, attacker, defender, attacking_side, defending_side, move_hit, hit_sub):
    if "phantomforce" in attacking_side.active.volatile_status:
        return [
            (constants.MUTATOR_REMOVE_VOLATILE_STATUS, attacker, "phantomforce")
        ]


def fly(state, attacker, defender, attacking_side, defending_side, move_hit, hit_sub):
    if "fly" in attacking_side.active.volatile_status:
        return [
            (constants.MUTATOR_REMOVE_VOLATILE_STATUS, attacker, "fly")
        ]


def bounce(state, attacker, defender, attacking_side, defending_side, move_hit, hit_sub):
    if "bounce" in attacking_side.active.volatile_status:
        return [
            (constants.MUTATOR_REMOVE_VOLATILE_STATUS, attacker, "bounce")
        ]


def dig(state, attacker, defender, attacking_side, defending_side, move_hit, hit_sub):
    if "dig" in attacking_side.active.volatile_status:
        return [
            (constants.MUTATOR_REMOVE_VOLATILE_STATUS, attacker, "dig")
        ]


def dive(state, attacker, defender, attacking_side, defending_side, move_hit, hit_sub):
    if "dive" in attacking_side.active.volatile_status:
        return [
            (constants.MUTATOR_REMOVE_VOLATILE_STATUS, attacker, "dive")
        ]


def shadowforce(state, attacker, defender, attacking_side, defending_side, move_hit, hit_sub):
    if "shadowforce" in attacking_side.active.volatile_status:
        return [
            (constants.MUTATOR_REMOVE_VOLATILE_STATUS, attacker, "shadowforce")
        ]


def doubleshock(state, attacker, defender, attacking_side, defending_side, move_hit, hit_sub):
    if "electric" in attacking_side.active.types:
        new_types = attacking_side.active.types.copy()
        new_types[new_types.index("electric")] = "typeless"
        return [
            (constants.MUTATOR_CHANGE_TYPE, attacker, attacking_side.active.types, new_types)
        ]


def after_move(move_name, state, attacker, defender, attacking_side, defending_side, move_hit, hit_sub):
    try:
        after_move_instructions = globals()[move_name](state, attacker, defender, attacking_side, defending_side, move_hit, hit_sub)
        return after_move_instructions or []
    except KeyError:
        return []
