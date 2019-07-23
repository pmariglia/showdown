import constants


def sandstream(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather not in [constants.DESOLATE_LAND, constants.HEAVY_RAIN]:
        return (
            constants.MUTATOR_WEATHER_START,
            constants.SAND,
            state.weather
        )
    return None


def snowwarning(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather not in [constants.DESOLATE_LAND, constants.HEAVY_RAIN]:
        return (
            constants.MUTATOR_WEATHER_START,
            constants.HAIL,
            state.weather
        )
    return None


def drought(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather not in [constants.DESOLATE_LAND, constants.HEAVY_RAIN]:
        return (
            constants.MUTATOR_WEATHER_START,
            constants.SUN,
            state.weather
        )
    return None


def drizzle(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather not in [constants.DESOLATE_LAND, constants.HEAVY_RAIN]:
        return (
            constants.MUTATOR_WEATHER_START,
            constants.RAIN,
            state.weather
        )
    return None


def desolateland(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    return (
        constants.MUTATOR_WEATHER_START,
        constants.DESOLATE_LAND,
        state.weather
    )


def primordialsea(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    return (
        constants.MUTATOR_WEATHER_START,
        constants.HEAVY_RAIN,
        state.weather
    )


def intimidate(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if defending_pokemon.ability not in ['fullmetalbody', 'clearbody', 'hypercutter', 'whitesmoke'] and defending_pokemon.attack_boost > -6:
        return (
            constants.MUTATOR_UNBOOST,
            defending_side,
            constants.ATTACK,
            1
        )
    return None


ability_lookup = {
    "sandstream": sandstream,
    "snowwarning": snowwarning,
    "drought": drought,
    "drizzle": drizzle,
    "desolateland": desolateland,
    "primordialsea": primordialsea,
    'intimidate': intimidate
}


def ability_on_switch_in(ability_name, state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    ability_func = ability_lookup.get(ability_name)
    if ability_func is not None:
        return ability_func(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon)
    else:
        return None
