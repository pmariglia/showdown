import os
import sys
import logging

import constants

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
greeting_message = 'you\'re playing a bot'
battle_ending_message_win = 'lol you just lost to a bot'
battle_ending_message_lose = 'gg wp, I\'m a bot by the way'

use_relative_weights = False
damage_calc_type = 'average'
search_depth = 2

save_replay = False
log_to_file = False
logging_directory = "{}/{}".format(os.getcwd(), "logs/")


def reset_logger(lgr, new_file_name):
    if not log_to_file:
        return
    if not os.path.exists(logging_directory):
        os.makedirs(logging_directory)
    handlers = lgr.handlers[:]  # don't iterate over a list and delete elements within it
    for old_handler in handlers:
        old_handler.close()
        lgr.removeHandler(old_handler)
    new_formatter = logging.Formatter('%(levelname)s: %(message)s')
    new_handler = logging.FileHandler(os.path.join(logging_directory, new_file_name), encoding='utf-8')
    new_handler.setFormatter(new_formatter)
    lgr.addHandler(new_handler)


websockets_logger = logging.getLogger("websockets")
websockets_logger.setLevel(logging.INFO)

logger = logging.getLogger()
default_formatter = logging.Formatter('%(levelname)s: %(message)s')
default_handler = logging.StreamHandler(sys.stdout)
default_handler.setFormatter(default_formatter)
logger.addHandler(default_handler)
