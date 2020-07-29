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


def solarpower(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather in [constants.SUN, constants.DESOLATE_LAND]:
        return (
                constants.MUTATOR_DAMAGE,
                attacking_side,
                min(attacking_pokemon.hp, round(0.125 * attacking_pokemon.maxhp))
            )


def raindish(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather == constants.RAIN or state.weather == constants.HEAVY_RAIN:
        return (
            constants.MUTATOR_HEAL,
            attacking_side,
            min(attacking_pokemon.maxhp - attacking_pokemon.hp, round(0.0625 * attacking_pokemon.maxhp))
        )


def dryskin(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather == constants.RAIN or state.weather == constants.HEAVY_RAIN:
        return (
            constants.MUTATOR_HEAL,
            attacking_side,
            min(attacking_pokemon.maxhp - attacking_pokemon.hp, round(0.125 * attacking_pokemon.maxhp))
        )
    elif state.weather == constants.SUN or state.weather == constants.DESOLATE_LAND:
        return (
            constants.MUTATOR_DAMAGE,
            attacking_side,
            min(attacking_pokemon.hp, round(0.125 * attacking_pokemon.maxhp))
        )


def icebody(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather == constants.HAIL:
        return (
            constants.MUTATOR_HEAL,
            attacking_side,
            min(attacking_pokemon.maxhp - attacking_pokemon.hp, round(0.0625 * attacking_pokemon.maxhp))
        )


def ability_end_of_turn(ability_name, state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if attacking_pokemon.ability == 'neutralizinggas' or defending_pokemon.ability == 'neutralizinggas' or not attacking_pokemon.hp:
        return None
    try:
        return globals()[ability_name](state, attacking_side, attacking_pokemon, defending_side, defending_pokemon)
    except KeyError:
        pass
