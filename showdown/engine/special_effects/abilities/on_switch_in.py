import constants


def sandstream(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather not in constants.IRREVERSIBLE_WEATHER:
        return [(
            constants.MUTATOR_WEATHER_START,
            constants.SAND,
            state.weather
        )]
    return None


def snowwarning(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather not in constants.IRREVERSIBLE_WEATHER:
        return [(
            constants.MUTATOR_WEATHER_START,
            constants.HAIL,
            state.weather
        )]
    return None


def drought(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather not in constants.IRREVERSIBLE_WEATHER:
        return [(
            constants.MUTATOR_WEATHER_START,
            constants.SUN,
            state.weather
        )]
    return None


def drizzle(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather not in constants.IRREVERSIBLE_WEATHER:
        return [(
            constants.MUTATOR_WEATHER_START,
            constants.RAIN,
            state.weather
        )]
    return None


def desolateland(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    return [(
        constants.MUTATOR_WEATHER_START,
        constants.DESOLATE_LAND,
        state.weather
    )]


def primordialsea(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    return [(
        constants.MUTATOR_WEATHER_START,
        constants.HEAVY_RAIN,
        state.weather
    )]


def electricsurge(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    return [(
        constants.MUTATOR_FIELD_START,
        constants.ELECTRIC_TERRAIN,
        state.field
    )]


def psychicsurge(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    return [(
        constants.MUTATOR_FIELD_START,
        constants.PSYCHIC_TERRAIN,
        state.field
    )]


def grassysurge(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    return [(
        constants.MUTATOR_FIELD_START,
        constants.GRASSY_TERRAIN,
        state.field
    )]


def mistysurge(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    return [(
        constants.MUTATOR_FIELD_START,
        constants.MISTY_TERRAIN,
        state.field
    )]


def intimidate(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if (
            defending_pokemon.ability not in ['fullmetalbody', 'clearbody', 'hypercutter', 'whitesmoke', 'defiant', 'innerfocus', 'oblivious', 'owntempo', 'scrappy'] and
            defending_pokemon.attack_boost > -6
    ):
        return [(
            constants.MUTATOR_UNBOOST,
            defending_side,
            constants.ATTACK,
            1
        )]
    # I shouldn't be doing this here but w/e sue me
    elif defending_pokemon.ability == 'defiant' and defending_pokemon.attack_boost < 6:
        return [(
            constants.MUTATOR_BOOST,
            defending_side,
            constants.ATTACK,
            1
        )]
    return None


def dauntlessshield(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    return [(
        constants.MUTATOR_BOOST,
        attacking_side,
        constants.DEFENSE,
        1
    )]


def intrepidsword(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    return [(
        constants.MUTATOR_BOOST,
        attacking_side,
        constants.ATTACK,
        1
    )]


def screencleaner(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    instructions = list()
    for side_condition in [constants.REFLECT, constants.LIGHT_SCREEN, constants.AURORA_VEIL]:
        if state.self.side_conditions[side_condition]:
            instructions.append(
                (constants.MUTATOR_SIDE_END, constants.SELF, side_condition, state.self.side_conditions[side_condition]),
            )
        if state.opponent.side_conditions[side_condition]:
            instructions.append(
                (constants.MUTATOR_SIDE_END, constants.OPPONENT, side_condition, state.opponent.side_conditions[side_condition]),
            )
    return instructions or None


ability_lookup = {
    "screencleaner": screencleaner,
    "intrepidsword": intrepidsword,
    "dauntlessshield": dauntlessshield,
    "mistysurge": mistysurge,
    "grassysurge": grassysurge,
    "psychicsurge": psychicsurge,
    "electricsurge": electricsurge,
    "sandstream": sandstream,
    "snowwarning": snowwarning,
    "drought": drought,
    "drizzle": drizzle,
    "desolateland": desolateland,
    "primordialsea": primordialsea,
    'intimidate': intimidate
}


def ability_on_switch_in(ability_name, state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if attacking_pokemon.ability == 'neutralizinggas' or defending_pokemon.ability == 'neutralizinggas':
        return None
    ability_func = ability_lookup.get(ability_name)
    if ability_func is not None:
        return ability_func(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon)
    else:
        return None
