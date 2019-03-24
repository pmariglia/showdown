import os
import json
from .team_converter import json_to_packed

TEAM_JSON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "team_jsons")


def load_team(name):
    if name is None:
        return 'null'

    file_path = os.path.join(TEAM_JSON_DIR, "{}.json".format(name))
    with open(file_path, 'r') as f:
        team_json = json.load(f)

    return json_to_packed(team_json)
