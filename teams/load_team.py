import os
from .team_converter import export_to_packed

TEAM_JSON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "teams")


def load_team(name):
    if name is None:
        return 'null'

    file_path = os.path.join(TEAM_JSON_DIR, "{}".format(name))
    with open(file_path, 'r') as f:
        team_json = f.read()

    return export_to_packed(team_json)
