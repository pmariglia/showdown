import constants
from data import effectiveness


class Scoring:
    POKEMON_ALIVE_STATIC = 75
    POKEMON_HP = 100  # 100 points for 100% hp, 0 points for 0% hp. This is in addition to being alive
    POKEMON_HIDDEN = 10
    POKEMON_BOOSTS = {
        constants.ATTACK: 15,
        constants.DEFENSE: 15,
        constants.SPECIAL_ATTACK: 15,
        constants.SPECIAL_DEFENSE: 15,
        constants.SPEED: 25,
        constants.ACCURACY: 3,
        constants.EVASION: 3
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

    POKEMON_STATIC_STATUSES = {
        constants.FROZEN: -40,
        constants.SLEEP: -25,
        constants.PARALYZED: -25,
        constants.TOXIC: -30,
        constants.POISON: -10,
        None: 0
    }

    MATCHUP_BONUS = 20

    @staticmethod
    def BURN(burn_multiplier):
        return -25*burn_multiplier

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
        constants.STEALTH_ROCK: -10,
        constants.SPIKES: -7,
        constants.TOXIC_SPIKES: -7,
    }


def evaluate_pokemon(pkmn):
    score = 0
    if pkmn.hp <= 0:
        return score

    score += Scoring.POKEMON_ALIVE_STATIC
    score += Scoring.POKEMON_HP * (float(pkmn.hp) / pkmn.maxhp)

    # boosts have diminishing returns
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.attack_boost] * Scoring.POKEMON_BOOSTS[constants.ATTACK]
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.defense_boost] * Scoring.POKEMON_BOOSTS[constants.DEFENSE]
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.special_attack_boost] * Scoring.POKEMON_BOOSTS[constants.SPECIAL_ATTACK]
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.special_defense_boost] * Scoring.POKEMON_BOOSTS[constants.SPECIAL_DEFENSE]
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.speed_boost] * Scoring.POKEMON_BOOSTS[constants.SPEED]
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.accuracy_boost] * Scoring.POKEMON_BOOSTS[constants.ACCURACY]
    score += Scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.evasion_boost] * Scoring.POKEMON_BOOSTS[constants.EVASION]

    try:
        score += Scoring.POKEMON_STATIC_STATUSES[pkmn.status]
    except KeyError:
        # KeyError only happens when the status is BURN
        score += Scoring.BURN(pkmn.burn_multiplier)

    for vol_stat in pkmn.volatile_status:
        try:
            score += Scoring.POKEMON_VOLATILE_STATUSES[vol_stat]
        except KeyError:
            pass

    return round(score)


def evaluate(state):
    score = 0

    number_of_opponent_reserve_revealed = len(state.opponent.reserve) + 1
    bot_alive_reserve_count = len([p.hp for p in state.user.reserve.values() if p.hp > 0])
    opponent_alive_reserves_count = len([p for p in state.opponent.reserve.values() if p.hp > 0]) + (6-number_of_opponent_reserve_revealed)

    # evaluate the bot's pokemon
    score += evaluate_pokemon(state.user.active)
    for pkmn in state.user.reserve.values():
        this_pkmn_score = evaluate_pokemon(pkmn)
        score += this_pkmn_score

    # evaluate the opponent's visible pokemon
    score -= evaluate_pokemon(state.opponent.active)
    for pkmn in state.opponent.reserve.values():
        this_pkmn_score = evaluate_pokemon(pkmn)
        score -= this_pkmn_score

    # evaluate the side-conditions for the bot
    for condition, count in state.user.side_conditions.items():
        if condition in Scoring.STATIC_SCORED_SIDE_CONDITIONS:
            score += count * Scoring.STATIC_SCORED_SIDE_CONDITIONS[condition]
        elif condition in Scoring.POKEMON_COUNT_SCORED_SIDE_CONDITIONS:
            score += count * Scoring.POKEMON_COUNT_SCORED_SIDE_CONDITIONS[condition] * bot_alive_reserve_count

    # evaluate the side-conditions for the opponent
    for condition, count in state.opponent.side_conditions.items():
        if condition in Scoring.STATIC_SCORED_SIDE_CONDITIONS:
            score -= count * Scoring.STATIC_SCORED_SIDE_CONDITIONS[condition]
        elif condition in Scoring.POKEMON_COUNT_SCORED_SIDE_CONDITIONS:
            score -= count * Scoring.POKEMON_COUNT_SCORED_SIDE_CONDITIONS[condition] * opponent_alive_reserves_count

    try:
        matchup_score = Scoring.MATCHUP_BONUS * effectiveness[state.user.active.id][state.opponent.active.id]
        matchup_score -= Scoring.MATCHUP_BONUS * effectiveness[state.opponent.active.id][state.user.active.id]
        score += matchup_score
    except KeyError:
        pass

    return int(score)
