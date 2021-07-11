import random
import os
from .team_converter import export_to_packed

TEAM_JSON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "teams")


def load_team(name):
    if name is None:
        return 'null'

    path = os.path.join(TEAM_JSON_DIR, "{}".format(name))
    if os.path.isdir(path):
        team_file_names = list()
        for f in os.listdir(path):
            full_path = os.path.join(path, f)
            if os.path.isfile(full_path) and not f.startswith('.'):
                team_file_names.append(full_path)
        file_path = random.choice(team_file_names)

    elif os.path.isfile(path):
        file_path = path
    else:
        raise ValueError("Path must be file or dir: {}".format(name))

    with open(file_path, 'r') as f:
        team_json = f.read()

    return export_to_packed(team_json)
