from data import all_move_json
from showdown.helpers import normalize_name
import constants


class Move:
    def __init__(self, name):
        name = normalize_name(name)
        move_json = all_move_json[name]
        self.name = name
        self.max_pp = int(move_json.get(constants.PP) * 1.6)

        self.disabled = False
        self.can_z = False
        self.current_pp = self.max_pp

    def to_dict(self):
        return {
            "id": self.name,
            "disabled": self.disabled,
            "current_pp": self.current_pp
        }

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return "{}".format(self.name)
