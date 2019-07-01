from functools import lru_cache

import constants
from . import scoring
from data import all_move_json
from showdown.calculate_damage import is_super_effective


@lru_cache(maxsize=None)
def evaluate_matchup(user_pkmn, opponent_pkmn):
    score = 0

    if user_pkmn.hp <= 0 or opponent_pkmn.hp <= 0:
        return score

    if user_pkmn.speed > opponent_pkmn.speed:
        score += scoring.FASTER_POKEMON_IN_MATCHUP
    elif user_pkmn.speed < opponent_pkmn.speed:
        score -= scoring.FASTER_POKEMON_IN_MATCHUP

    # positive bonus for the bot's type being super effective against the opponent
    for user_type in user_pkmn.types:
        if is_super_effective(user_type, opponent_pkmn.types):
            score += scoring.WEAK_TO_OPPONENT_TYPE

    # negative bonus for the opponent's type being super effective against the bot's
    for opponent_type in opponent_pkmn.types:
        if is_super_effective(opponent_type, user_pkmn.types):
            score -= scoring.WEAK_TO_OPPONENT_TYPE

    # bonus for super effective damaging moves (only the bot's moves are looked at)
    # extra for being faster as well
    for user_move in user_pkmn.moves:
        move = all_move_json[user_move[constants.ID]]
        if move[constants.CATEGORY] in constants.DAMAGING_CATEGORIES and is_super_effective(move[constants.TYPE], opponent_pkmn.types):
            score += scoring.SUPER_EFFECTIVE_DAMAGING_MOVE
            if user_pkmn.speed > opponent_pkmn.speed:
                score += scoring.FASTER_POKEMON_WITH_SUPER_EFFECTIVE_DAMAGING_MOVE

    return score
