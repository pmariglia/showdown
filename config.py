import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Union

from environs import Env

import constants

env = Env()
env.read_env(path="env", recurse=False)


class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.module = "[{}]".format(record.module)
        record.levelname = "[{}]".format(record.levelname)
        return "{} {}".format(record.levelname.ljust(10), record.msg)


class CustomRotatingFileHandler(RotatingFileHandler):
    def __init__(self, file_name, **kwargs):
        self.base_dir = "logs"
        if not os.path.exists(self.base_dir):
            os.mkdir(self.base_dir)

        super().__init__("{}/{}".format(self.base_dir, file_name), **kwargs)

    def do_rollover(self, new_file_name):
        self.baseFilename = "{}/{}".format(self.base_dir, new_file_name)
        self.doRollover()


def init_logging(level, log_to_file):
    websockets_logger = logging.getLogger("websockets")
    websockets_logger.setLevel(logging.INFO)
    requests_logger = logging.getLogger("urllib3")
    requests_logger.setLevel(logging.INFO)

    # Gets the root logger to set handlers/formatters
    logger = logging.getLogger()
    logger.setLevel(level)
    if log_to_file:
        log_handler = CustomRotatingFileHandler("init.log")
    else:
        log_handler = logging.StreamHandler(sys.stdout)

    ShowdownConfig.log_handler = log_handler
    log_handler.setFormatter(CustomFormatter())
    logger.addHandler(log_handler)


class _ShowdownConfig:
    battle_bot_module: str
    websocket_uri: str
    username: str
    password: str
    bot_mode: str
    pokemon_mode: str
    run_count: int
    team: str
    user_to_challenge: str
    save_replay: bool
    room_name: str
    damage_calc_type: str
    log_level: str
    log_to_file: bool
    log_handler: Union[CustomRotatingFileHandler, logging.StreamHandler]

    def configure(self):
        self.battle_bot_module = env("BATTLE_BOT")
        self.websocket_uri = env("WEBSOCKET_URI")
        self.username = env("PS_USERNAME")
        self.password = env("PS_PASSWORD")
        self.bot_mode = env("BOT_MODE")
        self.pokemon_mode = env("POKEMON_MODE")

        self.run_count = env.int("RUN_COUNT", 1)
        self.team = env("TEAM_NAME", None)
        self.user_to_challenge = env("USER_TO_CHALLENGE", None)

        self.save_replay = env.bool("SAVE_REPLAY", False)
        self.room_name = env("ROOM_NAME", None)
        self.damage_calc_type = env("DAMAGE_CALC_TYPE", "average")

        self.log_level = env("LOG_LEVEL", "DEBUG")
        self.log_to_file = env.bool("LOG_TO_FILE", False)

        self.validate_config()

    def validate_config(self):
        assert self.bot_mode in constants.BOT_MODES

        if self.bot_mode == constants.CHALLENGE_USER:
            assert self.user_to_challenge is not None, (
                "If bot_mode is `CHALLENGE_USER, you must declare USER_TO_CHALLENGE"
            )


ShowdownConfig = _ShowdownConfig()
