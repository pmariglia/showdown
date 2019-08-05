import constants

WON_BATTLE = 100

POKEMON_ALIVE_STATIC = 75
POKEMON_HP = 100  # 100 points for 100% hp, 0 points for 0% hp. This is in addition to being alive
POKEMON_HIDDEN = 10
POKEMON_BOOSTS = {
    constants.ATTACK: 15,
    constants.DEFENSE: 15,
    constants.SPECIAL_ATTACK: 15,
    constants.SPECIAL_DEFENSE: 15,
    constants.SPEED: 25,
    constants.ACCURACY: 1,
    constants.EVASION: 1
}

POKEMON_BOOST_DIMINISHING_RETURNS = {
    -6: -3.3,
    -5: -3.15,
    -4: -3,
    -3: -2.5,
    -2: -2,
    -1: -1,
    0: 0,
    1: 1,
    2: 2,
    3: 2.5,
    4: 3,
    5: 3.15,
    6: 3.30,
}

POKEMON_STATUSES = {
    constants.BURN: -20,
    constants.FROZEN: -50,
    constants.SLEEP: -25,
    constants.PARALYZED: -25,
    constants.TOXIC: -30,
    constants.POISON: -10,
    None: 0
}
POKEMON_VOLATILE_STATUSES = {
    constants.LEECH_SEED: -30,
    constants.SUBSTITUTE: 40,
    constants.CONFUSION: -20
}

STATIC_SCORED_SIDE_CONDITIONS = {
    constants.REFLECT: 20,
    constants.STICKY_WEB: -25,
    constants.LIGHT_SCREEN: 20,
    constants.AURORA_VEIL: 40,
    constants.SAFEGUARD: 5,
    constants.TAILWIND: 7,
}

POKEMON_COUNT_SCORED_SIDE_CONDITIONS = {
    constants.STEALTH_ROCK: -15,
    constants.SPIKES: -7,
    constants.TOXIC_SPIKES: -7,
}

WEAK_TO_OPPONENT_TYPE = 5
FASTER_POKEMON_IN_MATCHUP = 10
SUPER_EFFECTIVE_DAMAGING_MOVE = 5
FASTER_POKEMON_WITH_SUPER_EFFECTIVE_DAMAGING_MOVE = 3
