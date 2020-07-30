import constants


def knockoff(state, attacker, defender, attacking_side, defending_side, move_hit, hit_sub):
    if move_hit and defending_side.active.item_can_be_removed():
        return [
            (constants.MUTATOR_CHANGE_ITEM, defender, None, defending_side.active.item)
        ]


def after_move(move_name, state, attacker, defender, attacking_side, defending_side, move_hit, hit_sub):
    try:
        after_move_instructions = globals()[move_name](state, attacker, defender, attacking_side, defending_side, move_hit, hit_sub)
        return after_move_instructions or []
    except KeyError:
        return []
