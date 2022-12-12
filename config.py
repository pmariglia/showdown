import logging
import sys

battle_bot_module = None
websocket_uri = None
username = None
password = None
bot_mode = None
team_name = None
pokemon_mode = None
run_count = None
user_to_challenge = None
gambit_exe_path = ""
greeting_message = 'I\'m one of the top percentage bots out there, now hold this L.'
battle_ending_message = 'Yeah this game was a waste either way it ended smfh'
room_name = None

use_relative_weights = False
damage_calc_type = 'min'
search_depth = 2
dynamic_search_depth = False

save_replay = False


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



class _ShowdownConfig:
    def __init__(self):
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
