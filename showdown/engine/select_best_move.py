import constants
import itertools
from collections import defaultdict
from copy import deepcopy

import config
from config import logger

from showdown.decide import pick_best_move
from showdown.evaluate import evaluate
from showdown.decide import pick_safest
from showdown.helpers import battle_is_over

from .state_mutator import StateMutator
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


def get_payoff_matrix(mutator, depth=2, forced_options=None):
    """
    :param mutator: a StateMutator object representing the state of the battle
    :param depth: the remaining depth before the state is evaluated
    :param forced_options: options that can be forced instead of using `get_all_options`
    :return: a dictionary representing the potential move combinations and their associated scores
    """
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
                    safest = pick_safest(get_payoff_matrix(mutator, depth))
                    score += safest[1] * this_percentage
                    mutator.reverse(instructions.instructions)

            state_scores[(user_move, opponent_move)] = score

            if score < worst_score_for_this_row:
                worst_score_for_this_row = score

            if config.decision_method == constants.PICK_SAFEST and score < best_score:
                skip = True

                # MOST of the time in pokemon, an opponent's move that causes a prune will cause a prune elsewhere
                # move this item to the front of the list to prune faster
                opponent_options = move_item_to_front_of_list(opponent_options, opponent_move)

        if worst_score_for_this_row > best_score:
            best_score = worst_score_for_this_row

    return state_scores


def find_winner(mutator, p1, p2):
    mutator = deepcopy(mutator)
    mutator.state.self.reserve = dict()
    mutator.state.self.active = p1
    mutator.state.opponent.reserve = dict()
    mutator.state.opponent.active = p2

    evaluation = evaluate(mutator.state)

    scores = get_payoff_matrix(mutator, depth=2)
    safest = pick_safest(scores)

    return safest[1] > evaluation


def set_multipliers(side, multipliers):
    for mon, v in multipliers.items():
        if mon == side.active.id:
            side.active.scoring_multiplier = v
        else:
            side.reserve[mon].scoring_multiplier = v


def get_new_mutator_with_relative_pokemon_worth(mutator):
    mutator_copy = deepcopy(mutator)
    bot_pkmn = [mutator_copy.state.self.active] + list(filter(lambda x: x.hp > 0, mutator_copy.state.self.reserve.values()))
    opponent_pkmn = [mutator_copy.state.opponent.active] + list(filter(lambda x: x.hp > 0, mutator_copy.state.opponent.reserve.values()))

    pairings = list(itertools.product(bot_pkmn, opponent_pkmn))
    one_v_one_outcomes = dict()
    bot_pkmn_wins = defaultdict(lambda: 0)
    opponent_pkmn_wins = defaultdict(lambda: 0)
    for pair in pairings:
        bot_wins = find_winner(mutator_copy, *pair)
        one_v_one_outcomes[(pair[0].id, pair[1].id)] = bot_wins
        if bot_wins:
            bot_pkmn_wins[pair[0].id] += 1
        else:
            opponent_pkmn_wins[pair[1].id] += 1

    bot_pkmn_multipliers = defaultdict(lambda: 1.0)
    opponent_pkmn_multipliers = defaultdict(lambda: 1.0)
    for pair in pairings:
        if one_v_one_outcomes[(pair[0].id, pair[1].id)]:
            bot_pkmn_multipliers[pair[0].id] = round(bot_pkmn_multipliers[pair[0].id] + 0.1 * opponent_pkmn_wins[pair[1].id], 1)
        else:
            opponent_pkmn_multipliers[pair[1].id] = round(opponent_pkmn_multipliers[pair[1].id] + 0.1 * bot_pkmn_wins[pair[0].id], 1)

    bot_pkmn_multipliers_average = sum(bot_pkmn_multipliers.values()) / len(bot_pkmn_multipliers) if bot_pkmn_multipliers else {}
    bot_pkmn_multipliers = {k: v / bot_pkmn_multipliers_average for k, v in bot_pkmn_multipliers.items()}

    opponent_pkmn_multipliers_average = sum(opponent_pkmn_multipliers.values()) / len(opponent_pkmn_multipliers) if opponent_pkmn_multipliers else {}
    opponent_pkmn_multipliers = {k: v / opponent_pkmn_multipliers_average for k, v in opponent_pkmn_multipliers.items()}

    logger.debug("Bot pkmn multipliers: {}".format(dict(bot_pkmn_multipliers)))
    logger.debug("Opponent pkmn multipliers: {}".format(dict(opponent_pkmn_multipliers)))

    set_multipliers(mutator_copy.state.self, bot_pkmn_multipliers)
    set_multipliers(mutator_copy.state.opponent, opponent_pkmn_multipliers)

    return mutator_copy


def find_best_move(battle):
    battle = deepcopy(battle)
    if battle.battle_type == constants.RANDOM_BATTLE:
        battle.prepare_random_battle()
    else:
        battle.prepare_standard_battle()

    state = battle.to_object()
    mutator = StateMutator(state)

    if config.use_relative_weights:
        logger.debug("Analyzing state...")
        mutator = get_new_mutator_with_relative_pokemon_worth(mutator)

    logger.debug("Attempting to find best move from: {}".format(mutator.state))
    move_scores = get_payoff_matrix(mutator, depth=config.search_depth)
    logger.debug("Score lookups produced: {}".format(move_scores))

    decision = pick_best_move(move_scores, config.decision_method)

    logger.debug("Decision: {}".format(decision))

    if decision.startswith(constants.SWITCH_STRING) and decision != "switcheroo":
        switch_pokemon = decision.split("switch ")[-1]
        for pkmn in battle.user.reserve:
            if pkmn.name == switch_pokemon:
                message = "/switch {}".format(pkmn.index)
                break
        else:
            raise ValueError("Tried to switch to: {}".format(switch_pokemon))
    else:
        message = "/choose move {}".format(decision)
        if battle.user.active.can_mega_evo:
            message = "{} {}".format(message, constants.MEGA)
        elif battle.user.active.can_ultra_burst:
            message = "{} {}".format(message, constants.ULTRA_BURST)

        if battle.user.active.get_move(decision).can_z:
            message = "{} {}".format(message, constants.ZMOVE)

    return [message, str(battle.rqid)]
