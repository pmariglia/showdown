import os
import sys
import logging

damage_calc_type = 'average'
search_depth = 2

save_replay = False
log_to_file = False
logging_directory = "{}/{}".format(os.getcwd(), "logs/")
if not os.path.exists(logging_directory):
    os.makedirs(logging_directory)


def reset_logger(lgr, new_file_name):
    if not log_to_file:
        return
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
