import importlib
import json
import asyncio
import concurrent.futures
from copy import deepcopy
import logging

from data.pkmn_sets import RandomBattleTeamDatasets, TeamDatasets
from data.pkmn_sets import SmogonSets
import constants
from config import FoulPlayConfig
from fp.battle import LastUsedMove, Pokemon
from fp.battle_bots.helpers import format_decision
from fp.battle_modifier import async_update_battle
from fp.helpers import normalize_name

from fp.websocket_client import PSWebsocketClient

logger = logging.getLogger(__name__)


def battle_is_finished(battle_tag, msg):
    return (
        msg.startswith(">{}".format(battle_tag))
        and (constants.WIN_STRING in msg or constants.TIE_STRING in msg)
        and constants.CHAT_STRING not in msg
    )


def extract_battle_factory_tier_from_msg(msg):
    start = msg.find("Battle Factory Tier: ") + len("Battle Factory Tier: ")
    end = msg.find("</b>", start)
    tier_name = msg[start:end]

    return normalize_name(tier_name)


async def async_pick_move(battle):
    battle_copy = deepcopy(battle)
    if battle_copy.request_json:
        battle_copy.user.update_from_request_json(battle_copy.request_json)

    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        best_move = await loop.run_in_executor(pool, battle_copy.find_best_move)
    battle.user.last_selected_move = LastUsedMove(
        battle.user.active.name, best_move.removesuffix("-tera"), battle.turn
    )
    return format_decision(battle_copy, best_move)


async def handle_team_preview(battle, ps_websocket_client):
    battle_copy = deepcopy(battle)
    battle_copy.user.active = Pokemon.get_dummy()
    battle_copy.opponent.active = Pokemon.get_dummy()
    battle_copy.team_preview = True

    best_move = await async_pick_move(battle_copy)

    # because we copied the battle before sending it in, we need to update the last selected move here
    pkmn_name = battle.user.reserve[int(best_move[0].split()[1]) - 1].name
    battle.user.last_selected_move = LastUsedMove(
        "teampreview", "switch {}".format(pkmn_name), battle.turn
    )

    size_of_team = len(battle.user.reserve) + 1
    team_list_indexes = list(range(1, size_of_team))
    choice_digit = int(best_move[0].split()[-1])

    team_list_indexes.remove(choice_digit)
    message = [
        "/team {}{}|{}".format(
            choice_digit, "".join(str(x) for x in team_list_indexes), battle.rqid
        )
    ]

    await ps_websocket_client.send_message(battle.battle_tag, message)


async def get_battle_tag_and_opponent(ps_websocket_client: PSWebsocketClient):
    while True:
        msg = await ps_websocket_client.receive_message()
        split_msg = msg.split("|")
        first_msg = split_msg[0]
        if "battle" in first_msg:
            battle_tag = first_msg.replace(">", "").strip()
            user_name = split_msg[-1].replace("☆", "").strip()
            opponent_name = (
                split_msg[4].replace(user_name, "").replace("vs.", "").strip()
            )
            return battle_tag, opponent_name


async def initialize_battle_with_tag(
    ps_websocket_client: PSWebsocketClient, set_request_json=True
):
    battle_module = importlib.import_module(
        "fp.battle_bots.{}.main".format(FoulPlayConfig.battle_bot_module)
    )

    battle_tag, opponent_name = await get_battle_tag_and_opponent(ps_websocket_client)

    if FoulPlayConfig.log_to_file:
        FoulPlayConfig.file_log_handler.do_rollover(
            "{}_{}.log".format(battle_tag, opponent_name)
        )

    while True:
        msg = await ps_websocket_client.receive_message()
        split_msg = msg.split("|")
        if split_msg[1].strip() == "request" and split_msg[2].strip():
            user_json = json.loads(split_msg[2].strip("'"))
            user_id = user_json[constants.SIDE][constants.ID]
            opponent_id = constants.ID_LOOKUP[user_id]
            battle = battle_module.BattleBot(battle_tag)
            battle.opponent.name = opponent_id
            battle.opponent.account_name = opponent_name

            if set_request_json:
                battle.request_json = user_json

            return battle, opponent_id, user_json


async def read_messages_until_first_pokemon_is_seen(
    ps_websocket_client, battle, opponent_id, user_json
):
    # keep reading messages until the opponent's first pokemon is seen
    # this is run when starting non team-preview battles
    while True:
        msg = await ps_websocket_client.receive_message()
        if constants.START_STRING in msg:
            split_msg = msg.split(constants.START_STRING)[-1].split("\n")
            for line in split_msg:
                if opponent_id in line and constants.SWITCH_STRING in line:
                    battle.start_non_team_preview_battle(user_json, line)

                # don't update the battle if the line contains a switch (this would be the bot's switch)
                # the first switch-in of randombattles will be handled by `start_non_team_preview_battle`
                elif battle.started and not line.startswith("|switch|"):
                    await async_update_battle(battle, line)

            return


async def start_random_battle(
    ps_websocket_client: PSWebsocketClient, pokemon_battle_type
):
    battle, opponent_id, user_json = await initialize_battle_with_tag(
        ps_websocket_client
    )
    battle.battle_type = constants.RANDOM_BATTLE
    battle.generation = pokemon_battle_type[:4]
    RandomBattleTeamDatasets.initialize(battle.generation)

    await read_messages_until_first_pokemon_is_seen(
        ps_websocket_client, battle, opponent_id, user_json
    )

    # first move needs to be picked here
    best_move = await async_pick_move(battle)
    await ps_websocket_client.send_message(battle.battle_tag, best_move)

    return battle


async def start_standard_battle(
    ps_websocket_client: PSWebsocketClient, pokemon_battle_type
):
    battle, opponent_id, user_json = await initialize_battle_with_tag(
        ps_websocket_client, set_request_json=False
    )
    if "battlefactory" in pokemon_battle_type:
        battle.battle_type = constants.BATTLE_FACTORY
    else:
        battle.battle_type = constants.STANDARD_BATTLE
    battle.generation = pokemon_battle_type[:4]

    if battle.generation in constants.NO_TEAM_PREVIEW_GENS:
        await read_messages_until_first_pokemon_is_seen(
            ps_websocket_client, battle, opponent_id, user_json
        )
        unique_pkmn_names = set(
            [p.name for p in (battle.opponent.reserve + battle.user.reserve)]
            + [battle.user.active.name, battle.opponent.active.name]
        )
        SmogonSets.initialize(pokemon_battle_type, unique_pkmn_names)
        TeamDatasets.initialize(pokemon_battle_type, unique_pkmn_names)

        # first move needs to be picked here
        best_move = await async_pick_move(battle)
        await ps_websocket_client.send_message(battle.battle_tag, best_move)

    else:
        msg = ""
        while constants.START_TEAM_PREVIEW not in msg:
            msg = await ps_websocket_client.receive_message()

        preview_string_lines = msg.split(constants.START_TEAM_PREVIEW)[-1].split("\n")

        opponent_pokemon = []
        for line in preview_string_lines:
            if not line:
                continue

            split_line = line.split("|")
            if (
                split_line[1] == constants.TEAM_PREVIEW_POKE
                and split_line[2].strip() == opponent_id
            ):
                opponent_pokemon.append(split_line[3])

        battle.initialize_team_preview(user_json, opponent_pokemon, pokemon_battle_type)
        battle.during_team_preview()

        unique_pkmn_names = set(
            p.name for p in battle.opponent.reserve + battle.user.reserve
        )

        if battle.battle_type == constants.BATTLE_FACTORY:
            tier_name = extract_battle_factory_tier_from_msg(msg)
            logger.info("Battle Factory Tier: {}".format(tier_name))
            TeamDatasets.initialize(
                pokemon_battle_type,
                unique_pkmn_names,
                battle_factory_tier_name=tier_name,
            )
        else:
            SmogonSets.initialize(pokemon_battle_type, unique_pkmn_names)
            TeamDatasets.initialize(pokemon_battle_type, unique_pkmn_names)

        await handle_team_preview(battle, ps_websocket_client)

    return battle


async def start_battle(ps_websocket_client, pokemon_battle_type):
    if "random" in pokemon_battle_type:
        battle = await start_random_battle(ps_websocket_client, pokemon_battle_type)
    else:
        battle = await start_standard_battle(ps_websocket_client, pokemon_battle_type)

    await ps_websocket_client.send_message(battle.battle_tag, ["hf"])
    await ps_websocket_client.send_message(battle.battle_tag, ["/timer on"])

    return battle


async def pokemon_battle(ps_websocket_client, pokemon_battle_type):
    battle = await start_battle(ps_websocket_client, pokemon_battle_type)
    while True:
        msg = await ps_websocket_client.receive_message()
        if battle_is_finished(battle.battle_tag, msg):
            if constants.WIN_STRING in msg:
                winner = msg.split(constants.WIN_STRING)[-1].split("\n")[0].strip()
            else:
                winner = None
            logger.info("Winner: {}".format(winner))
            await ps_websocket_client.send_message(battle.battle_tag, ["gg"])
            await ps_websocket_client.leave_battle(
                battle.battle_tag, save_replay=FoulPlayConfig.save_replay
            )
            return winner
        else:
            action_required = await async_update_battle(battle, msg)
            if action_required and not battle.wait:
                best_move = await async_pick_move(battle)
                await ps_websocket_client.send_message(battle.battle_tag, best_move)
