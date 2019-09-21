import math
import random
import subprocess
from collections import defaultdict

import config
from config import logger

NFG_FORMAT_BASE = """NFG 1 R ""
{ "Player 1" "Player 2" } { %s %s }

"""


class CouldNotFindEquilibriumError(Exception):
    pass


def format_string_for_options(num_rows, num_cols):
    return NFG_FORMAT_BASE % (num_rows, num_cols)


def append_items_to_string(matrix, string):
    import numpy as np

    item_to_add = "%s %s"
    this_string = ""
    for row in np.transpose(matrix):
        for value in row:
            this_string += "%s %s " % (value, value*-1)
    return item_to_add % (string, this_string)


def convert_from_list(l, num_rows):
    l = [float(i) for i in l]
    return [l[:num_rows], l[num_rows:]]


def find_all_equilibria(matrix):
    import numpy as np
    matrix = matrix.round(0)

    matrix = np.array(matrix)

    num_rows = len(matrix)
    num_cols = len(matrix[0])

    string = format_string_for_options(num_rows, num_cols)
    string = append_items_to_string(matrix, string).encode()

    cmd = [config.gambit_exe_path, '-q', '-d', '2']

    # sometimes this call fails and stdout is empty - repeating until completion seems to have fixed the issue
    stdout = ''
    stderr = ''
    attempted = 0
    while not stdout:
        # for unknown and seemingly random reasons this subprocess communication sometimes fails
        # retrying with the exact same input value does not fail
        # if an STDOUT value is not obtained in 5 tries, raise an error
        if attempted > 5:
            raise CouldNotFindEquilibriumError(stderr)
        sp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        stdout, stderr = sp.communicate(string)
        stdout = stdout.decode('utf-8').replace('\r', '')
        attempted += 1

    lines = stdout.split('\n')

    equilibria = []
    for line in lines:
        if line.startswith("NE"):
            ne = line[3:].split(',')
            ne = convert_from_list(ne, num_rows)
            equilibria.append(ne)

    return np.array(equilibria)


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
    modified_score_lookup = remove_guaranteed_opponent_moves(score_lookup)
    if not modified_score_lookup:
        modified_score_lookup = score_lookup
    worst_case = defaultdict(lambda: (tuple(), float('inf')))
    for move_pair, result in modified_score_lookup.items():
        if worst_case[move_pair[0]][1] > result:
            worst_case[move_pair[0]] = move_pair, result

    safest = max(worst_case, key=lambda x: worst_case[x][1])
    return worst_case[safest]


def _find_best_nash_equilibrium(equilibria, df):
    from nashpy import Game
    game = Game(df)

    score = float('-inf')
    best_eq = None
    for eq in equilibria:
        outcome = game[eq][0]
        if outcome > score:
            score = outcome
            best_eq = eq
    return best_eq, score


def find_nash_equilibrium(score_lookup):
    import pandas as pd
    modified_score_lookup = remove_guaranteed_opponent_moves(score_lookup)
    if not modified_score_lookup:
        modified_score_lookup = score_lookup

    df = pd.Series(modified_score_lookup).unstack()

    equilibria = find_all_equilibria(df)
    best_eq, score = _find_best_nash_equilibrium(equilibria, df)
    bot_percentages = best_eq[0]
    opponent_percentages = best_eq[1]

    bot_choices = df.index
    opponent_choices = df.columns

    return bot_choices, opponent_choices, bot_percentages, opponent_percentages, score


def _log_nash_equilibria(bot_choices, opponent_choices, bot_percentages, opponent_percentages, payoff):
    bot_options = []
    for i, percentage in enumerate(bot_percentages):
        if percentage:
            bot_options.append((bot_choices[i], percentage))

    opponent_options = []
    for i, percentage in enumerate(opponent_percentages):
        if percentage:
            opponent_options.append((opponent_choices[i], percentage))

    logger.debug("Bot options: {}".format(bot_options))
    logger.debug("Opponent options: {}".format(opponent_options))
    logger.debug("Payoff: {}".format(payoff))


def get_weighted_choices_from_multiple_score_lookups(score_lookups):
    bot_choice_percentages = defaultdict(lambda: 0)
    number_of_score_lookups = len(score_lookups)
    for sl in score_lookups:
        eq = find_nash_equilibrium(sl)
        _log_nash_equilibria(*eq)
        for i, bot_choice in enumerate(eq[0]):
            bot_choice_percentages[bot_choice] += eq[2][i]/number_of_score_lookups

    return list(bot_choice_percentages.items())


def pick_move_in_equilibrium_from_multiple_score_lookups(score_lookups):
    # This is the WRONG way to find a Nash Equilibrium from different potential games
    # ... but it is a simple way that works (with crappy results)
    #
    # The games should be modelled properly based on incomplete information (see Harsanyi Transform),
    # however that would require the bot to keep track of what it has revealed to the opponent
    try:
        weighted_choices = get_weighted_choices_from_multiple_score_lookups(score_lookups)
    except CouldNotFindEquilibriumError as e:
        logger.warning("Problem finding equilibria: {}".format(e))
        return random.choice([pick_safest(sl)[0][0] for sl in score_lookups])

    s = sum([wc[1] for wc in weighted_choices])
    bot_choices = [wc[0] for wc in weighted_choices]
    bot_percentages = [wc[1] / s for wc in weighted_choices]

    choice = random.choices(bot_choices, weights=bot_percentages)[0]

    logger.debug("Final Weights: {}".format([w for w in weighted_choices if w[1]]))
    logger.debug("Choice: {}".format(choice))

    return choice
