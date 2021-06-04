import sys
import logging

battle_bot_module = nash_equilibrium
websocket_uri = sim.smogon.com:8000
username = blanko AIv2
password = Jasmine456
bot_mode = SEARCH_LADDER
team_name = gen8/ou/uu
pokemon_mode = gen8uu
run_count = 20
user_to_challenge = None
gambit_exe_path = ""
greeting_message = ' '
battle_ending_message = ' '
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
