import constants
from config import logger
from data import all_move_sets
from .find_state_instructions import get_all_state_instructions
from showdown.helpers import battle_is_over
from showdown.evaluate_state import evaluate
from showdown.decide.decide import pick_safest
from showdown.search.state_mutator import StateMutator


def get_move_set(pkmn_name):
    try:
        return set(all_move_sets[pkmn_name.lower()])
    except KeyError:
        logger.warning("{} does not have a move lookup".format(pkmn_name.lower()))
        return [constants.DO_NOTHING_MOVE]


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
        possible_moves = set(s[constants.ID] for s in side.active.moves)
        if len(possible_moves) < 4:
            possible_moves = possible_moves.union(get_move_set(side.active.id))
        possible_moves = sorted(list(possible_moves))

    possible_switches = get_possible_switches(side)

    return possible_moves + possible_switches


def get_all_options(mutator: StateMutator):
    force_switch = mutator.state.force_switch or mutator.state.self.active.hp <= 0
    wait = mutator.state.wait or mutator.state.opponent.active.hp <= 0

    if force_switch and wait:
        user_options = get_user_options(mutator.state.self, force_switch)
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
        logger.debug("Could not find a user move, defaulting to splash")
        user_options = [constants.DO_NOTHING_MOVE]

    if not opponent_options:
        logger.debug("Could not find an opponent move, defaulting to splash")
        opponent_options = [constants.DO_NOTHING_MOVE]

    return user_options, opponent_options


def get_move_combination_scores(mutator, depth=2, previous_moves=tuple(), previous_instructions=()):
    """
    :param mutator: a StateMutator object representing the state of the battle
    :param depth: the remaining depth before the state is evaluated
    :param previous_moves: any previous moves that happened prior to this call
    :param previous_instructions: any previous instructions that were applied to the state before this call
    :return: a dictionary representing the potential move combinations and their associated scores
    """
    depth -= 1
    if battle_is_over(mutator.state):
        return {(constants.DO_NOTHING_MOVE, constants.DO_NOTHING_MOVE): evaluate(mutator.state)}

    user_options, opponent_options = get_all_options(mutator)

    # if the battle is not over, but the opponent has no moves - we want to return the user options as moves
    # this is a special case in a random battle where the opponent's pokemon has fainted, but the opponent still
    # has reserves left that are unseen
    if opponent_options == [constants.DO_NOTHING_MOVE] and mutator.state.opponent.active.hp == 0:
        return {(user_option, constants.DO_NOTHING_MOVE): evaluate(mutator.state) for user_option in user_options}

    state_scores = dict()
    for i, user_move in enumerate(user_options):
        for j, opponent_move in enumerate(opponent_options):
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
                    safest = pick_safest(get_move_combination_scores(
                        mutator, depth, previous_moves=previous_moves + (user_move, opponent_move),
                        previous_instructions=previous_instructions + tuple(instructions.instructions))
                    )
                    score += safest[1] * this_percentage
                    mutator.reverse(instructions.instructions)

            state_scores[(user_move, opponent_move)] = score

    return state_scores
