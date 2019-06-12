import constants


def drought(state, attacking_pokemon, defending_pokemon):
    if state.weather not in [constants.DESOLATE_LAND, constants.HEAVY_RAIN]:
        return (
            constants.MUTATOR_WEATHER_START,
            constants.SUN
        )
    return None


def drizzle(state, attacking_pokemon, defending_pokemon):
    if state.weather not in [constants.DESOLATE_LAND, constants.HEAVY_RAIN]:
        return (
            constants.MUTATOR_WEATHER_START,
            constants.RAIN
        )
    return None


ability_lookup = {
    "drought": drought,
    "drizzle": drizzle
}


def ability_on_switch_in(ability_name, state, attacking_pokemon, defending_pokemon):
    ability_func = ability_lookup.get(ability_name)
    if ability_func is not None:
        return ability_func(state, attacking_pokemon, defending_pokemon)
    else:
        return None
