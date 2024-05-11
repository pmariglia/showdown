import constants


def leftovers(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if attacking_pokemon.hp < attacking_pokemon.maxhp:
        return (
            constants.MUTATOR_HEAL,
            attacking_side,
            min(attacking_pokemon.maxhp - attacking_pokemon.hp, round(0.0625 * attacking_pokemon.maxhp))
        )
    return None


def blacksludge(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if 'poison' in attacking_pokemon.types:
        return leftovers(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon)
    else:
        return (
            constants.MUTATOR_DAMAGE,
            attacking_side,
            min(attacking_pokemon.hp, round(0.0625 * attacking_pokemon.maxhp))
        )


def flameorb(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if attacking_pokemon.status is None and 'fire' not in attacking_pokemon.types:
        return (
            constants.MUTATOR_APPLY_STATUS,
            attacking_side,
            constants.BURN
        )


def toxicorb(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if attacking_pokemon.status is None and 'poison' not in attacking_pokemon.types:
        return (
            constants.MUTATOR_APPLY_STATUS,
            attacking_side,
            constants.TOXIC
        )


def item_end_of_turn(item_name, state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if attacking_pokemon.hp:
        try:
            return globals()[item_name](state, attacking_side, attacking_pokemon, defending_side, defending_pokemon)
        except KeyError:
            pass
