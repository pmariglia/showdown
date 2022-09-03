import constants


def sandstream(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather not in constants.IRREVERSIBLE_WEATHER and state.weather != constants.SAND:
        return [(
            constants.MUTATOR_WEATHER_START,
            constants.SAND,
            state.weather
        )]
    return None


def snowwarning(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather not in constants.IRREVERSIBLE_WEATHER and state.weather != constants.HAIL:
        return [(
            constants.MUTATOR_WEATHER_START,
            constants.HAIL,
            state.weather
        )]
    return None


def drought(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather not in constants.IRREVERSIBLE_WEATHER and state.weather != constants.SUN:
        return [(
            constants.MUTATOR_WEATHER_START,
            constants.SUN,
            state.weather
        )]
    return None


def drizzle(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.weather not in constants.IRREVERSIBLE_WEATHER and state.weather != constants.RAIN:
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
    if state.field != constants.ELECTRIC_TERRAIN:
        return [(
            constants.MUTATOR_FIELD_START,
            constants.ELECTRIC_TERRAIN,
            state.field
        )]


def psychicsurge(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.field != constants.PSYCHIC_TERRAIN:
        return [(
            constants.MUTATOR_FIELD_START,
            constants.PSYCHIC_TERRAIN,
            state.field
        )]


def grassysurge(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.field != constants.GRASSY_TERRAIN:
        return [(
            constants.MUTATOR_FIELD_START,
            constants.GRASSY_TERRAIN,
            state.field
        )]


def mistysurge(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.field != constants.MISTY_TERRAIN:
        return [(
            constants.MUTATOR_FIELD_START,
            constants.MISTY_TERRAIN,
            state.field
        )]


def intimidate(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if defending_pokemon.ability in ['fullmetalbody', 'clearbody', 'hypercutter', 'whitesmoke', 'innerfocus', 'oblivious', 'owntempo', 'scrappy']:
        return None

    # I shouldn't be doing this here but w/e sue me
    if defending_pokemon.ability == 'defiant':
        return [(
            constants.MUTATOR_BOOST,
            defending_side,
            constants.ATTACK,
            min(6-defending_pokemon.attack_boost, 1) #stop boosting when it reaches 6
        )]

    # same as above, shouldn't be done here
    if defending_pokemon.ability == 'rattled':
        return [(
            constants.MUTATOR_UNBOOST,
            defending_side,
            constants.ATTACK,
            1
        ), (
            constants.MUTATOR_BOOST,
            defending_side,
            constants.SPEED,
            min(6-defending_pokemon.speed_boost, 1) #stop boosting when it reaches 6
        )]

    if defending_pokemon.ability == 'competitive':
        return [(
            constants.MUTATOR_UNBOOST,
            defending_side,
            constants.ATTACK,
            1
        ), (
            constants.MUTATOR_BOOST,
            defending_side,
            constants.SPECIAL_ATTACK,
            min(6-defending_pokemon.special_attack_boost, 2) #stop boosting when it reaches 6
        )]

    if defending_pokemon.attack_boost == -6:
        return None

    return [(
        constants.MUTATOR_UNBOOST,
        defending_side,
        constants.ATTACK,
        min(1, 6+defending_pokemon.attack_boost)
    )]


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
        if state.user.side_conditions[side_condition]:
            instructions.append(
                (constants.MUTATOR_SIDE_END, constants.USER, side_condition, state.user.side_conditions[side_condition]),
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
