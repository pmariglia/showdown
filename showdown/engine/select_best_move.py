import math
from collections import defaultdict

import constants
from showdown.engine.evaluate import evaluate
from showdown.helpers import battle_is_over

from .find_state_instructions import get_all_state_instructions


WON_BATTLE = 100


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


def get_possible_switches(side):
    switches = []
    for pkmn_name, pkmn in side.reserve.items():
        if pkmn.hp > 0:
            switches.append("{} {}".format(constants.SWITCH_STRING, pkmn_name))
    return switches


def get_user_options(side, force_switch):
    if force_switch:
        possible_moves = []
    else:
        possible_moves = [m[constants.ID] for m in side.active.moves if not m[constants.DISABLED]]

    if side.trapped:
        possible_switches = []
    else:
        possible_switches = get_possible_switches(side)

    return possible_moves + possible_switches


def get_opponent_options(side):
    if side.active.hp <= 0:
        possible_moves = []
    else:
        possible_moves = [m[constants.ID] for m in side.active.moves if not m[constants.DISABLED]]

    possible_switches = get_possible_switches(side)

    return possible_moves + possible_switches


def get_all_options(state):
    force_switch = state.force_switch or state.self.active.hp <= 0
    wait = state.wait or state.opponent.active.hp <= 0

    # double faint or team preview
    if force_switch and wait:
        state.self.trapped = False
        state.force_switch = False
        state.wait = False
        user_options = get_user_options(state.self, force_switch) or [constants.DO_NOTHING_MOVE]
        opponent_options = get_opponent_options(state.opponent) or [constants.DO_NOTHING_MOVE]
        return user_options, opponent_options

    if force_switch:
        opponent_options = [constants.DO_NOTHING_MOVE]
        state.force_switch = False
        state.self.trapped = False
        wait = False
    else:
        opponent_options = get_opponent_options(state.opponent)

    if wait:
        user_options = [constants.DO_NOTHING_MOVE]
    else:
        user_options = get_user_options(state.self, force_switch)

    if not user_options:
        user_options = [constants.DO_NOTHING_MOVE]

    if not opponent_options:
        opponent_options = [constants.DO_NOTHING_MOVE]

    return user_options, opponent_options


def move_item_to_front_of_list(l, item):
    all_indicies = list(range(len(l)))
    this_index = l.index(item)
    all_indicies.remove(this_index)
    all_indicies.insert(0, this_index)
    return [l[i] for i in all_indicies]


def get_payoff_matrix(mutator, user_options, opponent_options, depth=2, prune=True):
    """
    :param mutator: a StateMutator object representing the state of the battle
    :param user_options: options for the bot
    :param opponent_options: options for the opponent
    :param depth: the remaining depth before the state is evaluated
    :param prune: specify whether or not to prune the tree
    :return: a dictionary representing the potential move combinations and their associated scores
    """

    winner = battle_is_over(mutator.state)
    if winner:
        return {(constants.DO_NOTHING_MOVE, constants.DO_NOTHING_MOVE): evaluate(mutator.state) + WON_BATTLE*depth*winner}

    depth -= 1

    # if the battle is not over, but the opponent has no moves - we want to return the user options as moves
    # this is a special case in a random battle where the opponent's pokemon has fainted, but the opponent still
    # has reserves left that are unseen
    if opponent_options == [constants.DO_NOTHING_MOVE] and mutator.state.opponent.active.hp == 0:
        return {(user_option, constants.DO_NOTHING_MOVE): evaluate(mutator.state) for user_option in user_options}

    state_scores = dict()

    best_score = float('-inf')
    for i, user_move in enumerate(user_options):
        worst_score_for_this_row = float('inf')
        skip = False

        # opponent_options can change during the loop
        # using opponent_options[:] makes a copy when iterating to ensure no funny-business
        for j, opponent_move in enumerate(opponent_options[:]):
            if skip:
                state_scores[(user_move, opponent_move)] = float('nan')
                continue

            score = 0
            state_instructions = get_all_state_instructions(mutator, user_move, opponent_move)
            if depth == 0:
                for instructions in state_instructions:
                    mutator.apply(instructions.instructions)
                    t_score = evaluate(mutator.state)
                    score += (t_score * instructions.percentage)
                    mutator.reverse(instructions.instructions)

            else:
                for instructions in state_instructions:
                    this_percentage = instructions.percentage
                    mutator.apply(instructions.instructions)
                    next_turn_user_options, next_turn_opponent_options = get_all_options(mutator.state)
                    safest = pick_safest(get_payoff_matrix(mutator, next_turn_user_options, next_turn_opponent_options, depth=depth, prune=prune))
                    score += safest[1] * this_percentage
                    mutator.reverse(instructions.instructions)

            state_scores[(user_move, opponent_move)] = score

            if score < worst_score_for_this_row:
                worst_score_for_this_row = score

            if prune and score < best_score:
                skip = True

                # MOST of the time in pokemon, an opponent's move that causes a prune will cause a prune elsewhere
                # move this item to the front of the list to prune faster
                opponent_options = move_item_to_front_of_list(opponent_options, opponent_move)

        if worst_score_for_this_row > best_score:
            best_score = worst_score_for_this_row

    return state_scores
