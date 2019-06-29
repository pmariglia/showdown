from functools import lru_cache

from . import scoring
from .evaluate_pokemon import evaluate_pokemon
from .evaluate_matchup import evaluate_matchup

pkmn_cache = dict()


@lru_cache(maxsize=None)
def evaluate(state):
    score = 0

    number_of_opponent_reserve_revealed = len(state.opponent.reserve) + 1
    bot_alive_reserve_count = len([p.hp for p in state.self.reserve.values() if p.hp > 0])
    opponent_alive_reserves_count = len([p for p in state.opponent.reserve.values() if p.hp > 0]) + (6-number_of_opponent_reserve_revealed)

    # evaluate the bot's pokemon
    score += evaluate_pokemon(state.self.active)
    for pkmn in state.self.reserve.values():
        try:
            score += pkmn_cache[(pkmn.id, pkmn.hp, pkmn.maxhp, pkmn.status)]
        except KeyError:
            this_pkmn_score = evaluate_pokemon(pkmn)
            pkmn_cache[(pkmn.id, pkmn.hp, pkmn.maxhp, pkmn.status)] = this_pkmn_score
            score += this_pkmn_score

    # evaluate the opponent's visible pokemon
    score -= evaluate_pokemon(state.opponent.active)
    for pkmn in state.opponent.reserve.values():
        try:
            score -= pkmn_cache[(pkmn.id, pkmn.hp, pkmn.maxhp, pkmn.status)]
        except KeyError:
            this_pkmn_score = evaluate_pokemon(pkmn)
            pkmn_cache[(pkmn.id, pkmn.hp, pkmn.maxhp, pkmn.status)] = this_pkmn_score
            score -= this_pkmn_score

    # evaluate the side-conditions for the bot
    for condition, count in state.self.side_conditions.items():
        if condition in scoring.STATIC_SCORED_SIDE_CONDITIONS:
            score += count * scoring.STATIC_SCORED_SIDE_CONDITIONS[condition]
        elif condition in scoring.POKEMON_COUNT_SCORED_SIDE_CONDITIONS:
            score += count * scoring.POKEMON_COUNT_SCORED_SIDE_CONDITIONS[condition] * bot_alive_reserve_count

    # evaluate the side-conditions for the opponent
    for condition, count in state.opponent.side_conditions.items():
        if condition in scoring.STATIC_SCORED_SIDE_CONDITIONS:
            score -= count * scoring.STATIC_SCORED_SIDE_CONDITIONS[condition]
        elif condition in scoring.POKEMON_COUNT_SCORED_SIDE_CONDITIONS:
            score -= count * scoring.POKEMON_COUNT_SCORED_SIDE_CONDITIONS[condition] * opponent_alive_reserves_count

    score += evaluate_matchup(state.self.active, state.opponent.active)

    return int(score)
