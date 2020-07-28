import constants


def knockoff(state, attacker, defender, attacking_side, defending_side, move_hit, hit_sub):
    # .endswith("mega|primal") is a hack but w/e sue me
    if defending_side.active.item is not None and move_hit and not hit_sub and not defending_side.active.id.endswith("mega") and not defending_side.active.id.endswith("primal"):
        return [
            (constants.MUTATOR_CHANGE_ITEM, defender, None, defending_side.active.item)
        ]


def after_move(move_name, state, attacker, defender, attacking_side, defending_side, move_hit, hit_sub):
    try:
        after_move_instructions = globals()[move_name](state, attacker, defender, attacking_side, defending_side, move_hit, hit_sub)
        return after_move_instructions or []
    except KeyError:
        return []
