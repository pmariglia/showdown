import math
import random
from collections import defaultdict

from config import logger


def remove_guaranteed_opponent_moves(score_lookup):
    """This method removes enemy moves from the score-lookup that do not give the bot a choice.
       For example - if the bot has 1 pokemon left, the opponent is faster, and can kill your active pokemon with move X
       then move X for the opponent will be removed from the score_lookup

       The bot behaves much better when it cannot see these types of decisions"""
    move_combinations = list(score_lookup.keys())
    if len(set(k[0] for k in move_combinations)) == 1:
        return score_lookup
    elif len(set(k[1] for k in move_combinations)) == 1:
        return score_lookup

    # find the opponent's moves where the bot has a choice
    opponent_move_scores = dict()
    opponent_decisions = set()
    for k, score in score_lookup.items():
        opponent_move = k[1]
        if opponent_move not in opponent_move_scores:
            opponent_move_scores[opponent_move] = score
        elif opponent_move in opponent_move_scores and score != opponent_move_scores[opponent_move] and not math.isnan(score):
            opponent_decisions.add(opponent_move)

    # re-create score_lookup with only the opponent's move acquired above
    new_opponent_decisions = dict()
    for k, v in score_lookup.items():
        if k[1] in opponent_decisions:
            new_opponent_decisions[k] = v

    return new_opponent_decisions


def pick_safest(score_lookup):
    score_lookup = remove_guaranteed_opponent_moves(score_lookup)
    worst_case = defaultdict(lambda: (tuple(), float('inf')))
    for move_pair, result in score_lookup.items():
        if worst_case[move_pair[0]][1] > result:
            worst_case[move_pair[0]] = move_pair, result

    safest = max(worst_case, key=lambda x: worst_case[x][1])
    return worst_case[safest]


def decide_from_best_averages(score_lookup, limit=10):
    move_averages = defaultdict(lambda: [])
    for move_tuple, score in score_lookup.items():
        move_averages[move_tuple[0]].append(score)

    for move, scores in move_averages.items():
        move_averages[move] = sum(scores) / len(scores)

    sorted_moves = sorted(move_averages.items(), key=lambda x: x[1], reverse=True)

    possible_moves = [sorted_moves[0][0]]
    best_move_score = sorted_moves[0][1]
    logger.debug("Good option: {}: {}".format(possible_moves[0], best_move_score))

    for move, score in sorted_moves[1:]:
        if best_move_score - score > limit:
            break
        logger.debug("Good option: {}: {}".format(move, score))
        possible_moves.append(move)

    return possible_moves


def decide_from_safest(score_lookup):
    safest = pick_safest(score_lookup)
    logger.debug("Safest: {}, {}".format(safest[0][0], safest[1]))
    return safest[0][0]


def decide_random_from_average_and_safest(score_lookup):
    modified_score_lookup = remove_guaranteed_opponent_moves(score_lookup)
    if not modified_score_lookup:
        modified_score_lookup = score_lookup
    options = decide_from_best_averages(modified_score_lookup)
    safest = decide_from_safest(modified_score_lookup)
    for _ in range(len(options)):
        options.append(safest)
    return random.choice(options)
