from environs import Env
import asyncio
import constants
import config
from config import logger

from data.mods.apply_mods import apply_mods

from teams import load_team
from showdown.run_battle import pokemon_battle
from websocket_communication import PSWebsocketClient

import json
from data import all_move_json
from data import pokedex
from copy import deepcopy


async def showdown():
    env = Env()
    env.read_env()
    config.log_to_file = env.bool("LOG_TO_FILE", config.log_to_file)
    config.save_replay = env.bool("SAVE_REPLAY", config.save_replay)
    logger.setLevel(env("LOG_LEVEL", "DEBUG"))
    websocket_uri = env("WEBSOCKET_URI", "sim.smogon.com:8000")
    username = env("PS_USERNAME")
    password = env("PS_PASSWORD", "")
    bot_mode = env("BOT_MODE")
    team_name = env("TEAM_NAME", None)
    pokemon_mode = env("POKEMON_MODE", constants.DEFAULT_MODE)
    run_count = int(env("RUN_COUNT", 1))

    apply_mods(pokemon_mode)
    original_pokedex = deepcopy(pokedex)
    original_move_json = deepcopy(all_move_json)

    if bot_mode not in constants.BOT_MODES:
        raise ValueError("{} is not a valid bot mode".format(bot_mode))

    ps_websocket_client = await PSWebsocketClient.create(username, password, websocket_uri)
    await ps_websocket_client.login()

    team = load_team(team_name)

    battles_run = 0
    wins = 0
    losses = 0
    while True:
        if bot_mode == constants.CHALLENGE_USER:
            user_to_challenge = env("USER_TO_CHALLENGE")
            await ps_websocket_client.challenge_user(user_to_challenge, pokemon_mode, team)
        elif bot_mode == constants.ACCEPT_CHALLENGE:
            await ps_websocket_client.accept_challenge(pokemon_mode, team)
        elif bot_mode == constants.SEARCH_LADDER:
            await ps_websocket_client.search_for_match(pokemon_mode, team)
        else:
            raise ValueError("Invalid Bot Mode")

        winner = await pokemon_battle(ps_websocket_client, pokemon_mode)

        if winner == username:
            wins += 1
        else:
            losses += 1

        logger.info("\nW: {}\nL: {}\n".format(wins, losses))

        if original_move_json != all_move_json:
            logger.critical("Move JSON changed!\nDumping modified version to `modified_moves.json`")
            with open("modified_moves.json", 'w') as f:
                json.dump(all_move_json, f, indent=4)
            exit(1)
        else:
            logger.debug("Move JSON unmodified!")

        if original_pokedex != pokedex:
            logger.critical("Pokedex JSON changed!\nDumping modified version to `modified_pokedex.json`")
            with open("modified_pokedex.json", 'w') as f:
                json.dump(pokedex, f, indent=4)
            exit(1)
        else:
            logger.debug("Pokedex JSON unmodified!")

        battles_run += 1
        if battles_run >= run_count:
            break


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(showdown())
