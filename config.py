import sys
import logging

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
greeting_message = 'hf'
battle_ending_message = 'gg'
room_name = None

use_relative_weights = False
damage_calc_type = 'average'
search_depth = 2

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
