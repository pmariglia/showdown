import random
import subprocess
import logging
from collections import defaultdict

import numpy as np
import pandas as pd
from nashpy import Game

import config
from showdown.battle import Battle
from showdown.engine.select_best_move import remove_guaranteed_opponent_moves
from showdown.engine.objects import StateMutator
from showdown.engine.select_best_move import pick_safest
from showdown.engine.select_best_move import get_payoff_matrix

from ..safest.main import pick_safest_move_from_battles
from ..helpers import format_decision


logger = logging.getLogger(__name__)


NFG_FORMAT_BASE = """NFG 1 R ""
{ "Player 1" "Player 2" } { %s %s }

"""


class CouldNotFindEquilibriumError(Exception):
    pass


def format_string_for_options(num_rows, num_cols):
    return NFG_FORMAT_BASE % (num_rows, num_cols)


def append_items_to_string(matrix, string):
    item_to_add = "%s %s"
    this_string = ""
    for row in np.transpose(matrix):
        for value in row:
            this_string += "%s %s " % (value, value*-1)
    return item_to_add % (string, this_string)


def convert_from_list(my_list, num_rows):
    my_list = [float(i) for i in my_list]
    return [my_list[:num_rows], my_list[num_rows:]]


def find_best_nash_equilibrium(equilibria, df):
    game = Game(df)

    score = float('-inf')
    best_eq = None
    for eq in equilibria:
        outcome = game[eq][0]
        if outcome > score:
            score = outcome
            best_eq = eq
    return best_eq, score


def find_all_equilibria(matrix):
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

    return np.array(equilibria, dtype=object)


def find_nash_equilibrium(score_lookup):
    modified_score_lookup = remove_guaranteed_opponent_moves(score_lookup)
    if not modified_score_lookup:
        modified_score_lookup = score_lookup

    df = pd.Series(modified_score_lookup).unstack()

    equilibria = find_all_equilibria(df)
    best_eq, score = find_best_nash_equilibrium(equilibria, df)
    bot_percentages = best_eq[0]
    opponent_percentages = best_eq[1]

    bot_choices = df.index
    opponent_choices = df.columns

    return bot_choices, opponent_choices, bot_percentages, opponent_percentages, score


def log_nash_equilibria(bot_choices, opponent_choices, bot_percentages, opponent_percentages, payoff):
    bot_options = []
    for i, percentage in enumerate(bot_percentages):
        if percentage:
            bot_options.append((bot_choices[i], percentage))

    opponent_options = []
    for i, percentage in enumerate(opponent_percentages):
        if percentage:
            opponent_options.append((opponent_choices[i], percentage))


def get_weighted_choices_from_multiple_score_lookups(score_lookups):
    bot_choice_percentages = defaultdict(lambda: 0)
    number_of_score_lookups = len(score_lookups)
    for sl in score_lookups:
        eq = find_nash_equilibrium(sl)
        log_nash_equilibria(*eq)
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
        return random.choice([pick_safest(sl, remove_guaranteed=True)[0][0] for sl in score_lookups])

    s = sum([wc[1] for wc in weighted_choices])
    bot_choices = [wc[0] for wc in weighted_choices]
    bot_percentages = [wc[1] / s for wc in weighted_choices]

    choice = random.choices(bot_choices, weights=bot_percentages)[0]

    logger.debug("Choices: {}".format([w for w in weighted_choices if w[1]]))
    logger.debug("Choice: {}".format(choice))

    return choice


class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)

    def find_best_move(self):
        battles = self.prepare_battles()
        if len(battles) > 7:
            logger.debug("Not enough is known about the opponent's active pokemon - falling back to safest decision making")
            battles = self.prepare_battles(join_moves_together=True)
            decision = pick_safest_move_from_battles(battles)
        else:
            list_of_payoffs = list()
            for b in battles:
                state = b.create_state()
                mutator = StateMutator(state)
                logger.debug("Attempting to find best move from: {}".format(mutator.state))
                user_options, opponent_options = b.get_all_options()
                scores = get_payoff_matrix(mutator, user_options, opponent_options, prune=False)
                list_of_payoffs.append(scores)

            decision = pick_move_in_equilibrium_from_multiple_score_lookups(list_of_payoffs)

        return format_decision(self, decision)
