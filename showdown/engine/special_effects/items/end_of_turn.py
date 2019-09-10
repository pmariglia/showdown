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


item_lookup = {
    "leftovers": leftovers,
    "blacksludge": blacksludge,
}


def item_end_of_turn(item_name, state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    item_func = item_lookup.get(item_name)
    if item_func is not None and attacking_pokemon.hp:
        return item_func(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon)
    else:
        return None
