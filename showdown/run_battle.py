import json
import asyncio
import concurrent.futures
import itertools
from collections import defaultdict
from copy import deepcopy

import constants
import config
from config import logger
from config import reset_logger
from showdown.evaluate import Scoring
from showdown.decide import pick_best_move
from showdown.search.select_best_move import get_move_combination_scores
from showdown.decide import pick_safest
from showdown.evaluate import evaluate
from showdown.state.battle import Battle
from showdown.state.pokemon import Pokemon
from showdown.state.battle_modifiers import update_battle
from showdown.search.state_mutator import StateMutator

from showdown.websocket_client import PSWebsocketClient


async def _handle_team_preview(battle: Battle, ps_websocket_client: PSWebsocketClient):
    battle_copy = deepcopy(battle)
    battle_copy.user.active = Pokemon.get_dummy()
    battle_copy.opponent.active = Pokemon.get_dummy()

    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        formatted_message = await loop.run_in_executor(
            pool, _find_best_move, battle_copy
        )
    size_of_team = len(battle.user.reserve) + 1
    team_list_indexes = list(range(1, size_of_team))
    choice_digit = int(formatted_message[0].split()[-1])

    team_list_indexes.remove(choice_digit)
    message = ["/team {}{}|{}".format(choice_digit, "".join(str(x) for x in team_list_indexes), battle.rqid)]
    battle.user.active = battle.user.reserve.pop(choice_digit - 1)

    await ps_websocket_client.send_message(battle.battle_tag, message)


async def get_battle_tag_and_opponent(ps_websocket_client: PSWebsocketClient):
    while True:
        msg = await ps_websocket_client.receive_message()
        split_msg = msg.split('|')
        first_msg = split_msg[0]
        if 'battle' in first_msg:
            battle_tag = first_msg.replace('>', '').strip()
            user_name = split_msg[-1].replace('☆', '').strip()
            opponent_name = split_msg[4].replace(user_name, '').replace('vs.', '').strip()
            return battle_tag, opponent_name


async def _initialize_battle_with_tag(ps_websocket_client: PSWebsocketClient):
    battle_tag, opponent_name = await get_battle_tag_and_opponent(ps_websocket_client)
    while True:
        msg = await ps_websocket_client.receive_message()
        split_msg = msg.split('|')
        if split_msg[1].strip() == 'request' and split_msg[2].strip():
            user_json = json.loads(split_msg[2].strip('\''))
            user_id = user_json[constants.SIDE][constants.ID]
            opponent_id = constants.ID_LOOKUP[user_id]
            battle = Battle(battle_tag)
            battle.opponent.name = opponent_id
            battle.opponent.account_name = opponent_name
            return battle, opponent_id, user_json


async def _start_random_battle(ps_websocket_client: PSWebsocketClient):
    battle, opponent_id, user_json = await _initialize_battle_with_tag(ps_websocket_client)
    battle.battle_type = constants.RANDOM_BATTLE
    reset_logger(logger, "{}-{}.log".format(battle.opponent.account_name, battle.battle_tag))
    while True:
        msg = await ps_websocket_client.receive_message()

        if constants.START_STRING in msg:
            msg = msg.split(constants.START_STRING)[-1]
            for line in msg.split('\n'):
                if opponent_id in line and constants.SWITCH_STRING in line:
                    battle.start_random_battle(user_json, line)
                    continue

                if battle.started:
                    await update_battle(battle, line)

            return battle


async def _start_standard_battle(ps_websocket_client: PSWebsocketClient, pokemon_battle_type):
    battle, opponent_id, user_json = await _initialize_battle_with_tag(ps_websocket_client)
    battle.battle_type = constants.STANDARD_BATTLE
    await ps_websocket_client.send_message(battle.battle_tag, [config.greeting_message])
    reset_logger(logger, "{}-{}.log".format(battle.opponent.account_name, battle.battle_tag))

    msg = ''
    while constants.START_TEAM_PREVIEW not in msg:
        msg = await ps_websocket_client.receive_message()

    preview_string_lines = msg.split(constants.START_TEAM_PREVIEW)[-1].split('\n')

    opponent_pokemon = []
    for line in preview_string_lines:
        if not line:
            continue

        split_line = line.split('|')
        if split_line[1] == constants.TEAM_PREVIEW_POKE and split_line[2].strip() == opponent_id:
            opponent_pokemon.append(split_line[3])

    battle.initialize_team_preview(user_json, opponent_pokemon, pokemon_battle_type)
    await _handle_team_preview(battle, ps_websocket_client)

    return battle


def find_winner(mutator, p1, p2):
    mutator = deepcopy(mutator)
    mutator.state.self.reserve = dict()
    mutator.state.self.active = p1
    mutator.state.opponent.reserve = dict()
    mutator.state.opponent.active = p2

    evaluation = evaluate(mutator.state)

    scores = get_move_combination_scores(mutator, depth=2)
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


def _find_best_move(battle: Battle):
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
    move_scores = get_move_combination_scores(mutator, depth=config.search_depth)
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


async def pokemon_battle(ps_websocket_client: PSWebsocketClient, pokemon_battle_type):
    if "random" in pokemon_battle_type:
        Scoring.POKEMON_ALIVE_STATIC = 30  # random battle benefits from a lower static score for an alive pkmn
        battle = await _start_random_battle(ps_websocket_client)
        await ps_websocket_client.send_message(battle.battle_tag, [config.greeting_message])
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            formatted_message = await loop.run_in_executor(
                pool, _find_best_move, battle
            )
        await ps_websocket_client.send_message(battle.battle_tag, formatted_message)
    else:
        battle = await _start_standard_battle(ps_websocket_client, pokemon_battle_type)

    await ps_websocket_client.send_message(battle.battle_tag, ['/timer on'])
    while True:
        msg = await ps_websocket_client.receive_message()
        if constants.WIN_STRING in msg and constants.CHAT_STRING not in msg:
            winner = msg.split(constants.WIN_STRING)[-1].split('\n')[0].strip()
            logger.debug("Winner: {}".format(winner))
            await ps_websocket_client.send_message(battle.battle_tag, [config.battle_ending_message])
            await ps_websocket_client.leave_battle(battle.battle_tag, save_replay=config.save_replay)
            return winner
        action_required = await update_battle(battle, msg)
        if action_required and not battle.wait:
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as pool:
                formatted_message = await loop.run_in_executor(
                    pool, _find_best_move, battle
                )
            if formatted_message is not None:
                await ps_websocket_client.send_message(battle.battle_tag, formatted_message)
