import logging
import sys
from environs import Env

import constants

env = Env()
env.read_env(path="env", recurse=False)


class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.module = "[{}]".format(record.module)
        record.levelname = "[{}]".format(record.levelname)
        return "{} {}".format(record.levelname.ljust(10), record.msg)


def init_logging(level):
    websockets_logger = logging.getLogger("websockets")
    websockets_logger.setLevel(logging.INFO)
    requests_logger = logging.getLogger("urllib3")
    requests_logger.setLevel(logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(level)
    default_formatter = CustomFormatter()
    default_handler = logging.StreamHandler(sys.stdout)
    default_handler.setFormatter(default_formatter)
    logger.addHandler(default_handler)


init_logging(env("LOG_LEVEL", "DEBUG"))


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

        self.validate_config()

    def validate_config(self):
        assert self.bot_mode in constants.BOT_MODES

        if self.bot_mode == constants.CHALLENGE_USER:
            assert self.user_to_challenge is not None, (
                "If bot_mode is `CHALLENGE_USER, you must declare USER_TO_CHALLENGE"
            )


ShowdownConfig = _ShowdownConfig()
