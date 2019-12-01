import constants


def poisonheal(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if attacking_pokemon.status in [constants.POISON, constants.TOXIC]:
        if attacking_pokemon.hp:
            return (
                constants.MUTATOR_HEAL,
                attacking_side,
                min(attacking_pokemon.maxhp - attacking_pokemon.hp, round(0.125 * attacking_pokemon.maxhp))
            )


def speedboost(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if attacking_pokemon.speed_boost < 6:
        return (
            constants.MUTATOR_BOOST,
            attacking_side,
            constants.SPEED,
            1
        )


def hydration(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if attacking_pokemon.status is not None and state.weather in [constants.RAIN, constants.HEAVY_RAIN]:
        return (
            constants.MUTATOR_REMOVE_STATUS,
            attacking_side,
            attacking_pokemon.status
        )


ability_lookup = {
    "hydration": hydration,
    "speedboost": speedboost,
    "poisonheal": poisonheal,
}


def ability_end_of_turn(ability_name, state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if attacking_pokemon.ability == 'neutralizinggas' or defending_pokemon.ability == 'neutralizinggas':
        return None
    ability_func = ability_lookup.get(ability_name)
    if ability_func is not None and attacking_pokemon.hp:
        return ability_func(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon)
    else:
        return None
