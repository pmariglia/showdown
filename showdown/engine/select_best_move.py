import constants

import config
from config import logger

from showdown.evaluate import evaluate
from showdown.decide import pick_safest
from showdown.decide import pick_move_in_equilibrium_from_multiple_score_lookups
from showdown.helpers import battle_is_over

from .objects import StateMutator
from .find_state_instructions import get_all_state_instructions


WON_BATTLE = 100


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
        possible_moves = [s[constants.ID] for s in side.active.moves]

    possible_switches = get_possible_switches(side)

    return possible_moves + possible_switches


def get_all_options(mutator: StateMutator):
    force_switch = mutator.state.force_switch or mutator.state.self.active.hp <= 0
    wait = mutator.state.wait or mutator.state.opponent.active.hp <= 0

    # double faint or team preview
    if force_switch and wait:
        mutator.state.self.trapped = False
        mutator.state.force_switch = False
        mutator.state.wait = False
        user_options = get_user_options(mutator.state.self, force_switch) or [constants.DO_NOTHING_MOVE]
        opponent_options = get_opponent_options(mutator.state.opponent) or [constants.DO_NOTHING_MOVE]
        return user_options, opponent_options

    if force_switch:
        opponent_options = [constants.DO_NOTHING_MOVE]
        mutator.state.force_switch = False
        mutator.state.self.trapped = False
        wait = False
    else:
        opponent_options = get_opponent_options(mutator.state.opponent)

    if wait:
        user_options = [constants.DO_NOTHING_MOVE]
    else:
        user_options = get_user_options(mutator.state.self, force_switch)

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


def get_payoff_matrix(mutator, depth=2, forced_options=None, prune=None):
    """
    :param mutator: a StateMutator object representing the state of the battle
    :param depth: the remaining depth before the state is evaluated
    :param forced_options: options that can be forced instead of using `get_all_options`
    :param prune: specify whether or not to prune the tree
    :return: a dictionary representing the potential move combinations and their associated scores
    """
    if prune is None:
        prune = config.decision_method == constants.PICK_SAFEST

    winner = battle_is_over(mutator.state)
    if winner:
        return {(constants.DO_NOTHING_MOVE, constants.DO_NOTHING_MOVE): evaluate(mutator.state) + WON_BATTLE*depth*winner}

    depth -= 1
    if forced_options:
        user_options, opponent_options = forced_options
    else:
        user_options, opponent_options = get_all_options(mutator)

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
                    safest = pick_safest(get_payoff_matrix(mutator, depth, prune=prune))
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


def prefix_opponent_move(score_lookup, prefix):
    new_score_lookup = dict()
    for k, v in score_lookup.items():
        bot_move, opponent_move = k
        new_opponent_move = "{}_{}".format(opponent_move, prefix)
        new_score_lookup[(bot_move, new_opponent_move)] = v

    return new_score_lookup


def find_best_move_safest(battles):
    all_scores = dict()
    for i, b in enumerate(battles):
        state = b.to_object()
        mutator = StateMutator(state)
        logger.debug("Attempting to find best move from: {}".format(mutator.state))
        scores = get_payoff_matrix(mutator, depth=config.search_depth, prune=True)
        prefixed_scores = prefix_opponent_move(scores, str(i))
        all_scores = {**all_scores, **prefixed_scores}

    decision, payoff = pick_safest(all_scores)
    bot_choice = decision[0]
    logger.debug("Safest: {}, {}".format(bot_choice, payoff))
    return bot_choice


def find_best_move_nash(battles):
    list_of_payoffs = list()
    for b in battles:
        state = b.to_object()
        mutator = StateMutator(state)
        logger.debug("Attempting to find best move from: {}".format(mutator.state))
        scores = get_payoff_matrix(mutator, depth=config.search_depth)
        list_of_payoffs.append(scores)

    return pick_move_in_equilibrium_from_multiple_score_lookups(list_of_payoffs)


def find_best_move(battle):
    if config.decision_method == constants.PICK_SAFEST:
        battles = battle.prepare_battles(join_moves_together=True)
        return find_best_move_safest(battles)
    elif config.decision_method == constants.PICK_NASH_EQUILIBRIUM:
        battles = battle.prepare_battles()
        if len(battles) > 7:
            logger.debug("Not enough is known about the opponent's active pokemon - falling back to safest decision making")
            battles = battle.prepare_battles(join_moves_together=True)
            return find_best_move_safest(battles)
        else:
            return find_best_move_nash(battles)
    else:
        raise ValueError("Invalid decision method: {}".format(config.decision_method))
