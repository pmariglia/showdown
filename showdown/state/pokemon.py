from collections import defaultdict

import constants
from showdown.state.move import Move
from showdown.helpers import normalize_name
from showdown.helpers import calculate_stats
from data import pokedex
from config import logger


class Pokemon:

    def __init__(self, name: str, level: int):
        self.name = normalize_name(name)
        self.base_name = self.name
        self.level = level

        self.base_stats = pokedex[self.name][constants.BASESTATS]
        self.stats = calculate_stats(self.base_stats, self.level)

        self.max_hp = self.stats.pop(constants.HITPOINTS)
        self.hp = self.max_hp
        if self.name == 'shedinja':
            self.max_hp = 1
            self.hp = 1

        self.ability = normalize_name(pokedex[self.name][constants.MOST_LIKELY_ABILITY])
        self.types = pokedex[self.name][constants.TYPES]
        self.item = 'unknown'

        self.fainted = False
        self.moves = []
        self.status = None
        self.volatile_statuses = []
        self.boosts = defaultdict(lambda: 0)
        self.can_mega_evo = False
        self.can_ultra_burst = True

    @classmethod
    def from_switch_string(cls, switch_string):
        details = switch_string.split(',')
        name = details[0]
        try:
            level = int(details[1].replace('L', '').strip())
        except (IndexError, ValueError):
            level = 100
        return Pokemon(name, level)

    def set_spread(self, nature, evs):
        hp_percent = self.hp / self.max_hp
        self.stats = calculate_stats(self.base_stats, self.level, evs=evs, nature=nature)
        self.max_hp = self.stats.pop(constants.HITPOINTS)
        self.hp = self.max_hp * hp_percent

    def add_move(self, move_name: str):
        if normalize_name(move_name) in [m.name for m in self.moves]:
            return
        try:
            self.moves.append(Move(move_name))
        except KeyError:
            logger.warning("{} is not a known move".format(move_name))

    def get_move(self, move_name: str):
        for m in self.moves:
            if m.name == normalize_name(move_name):
                return m
        raise ValueError("{} does not have the move {}".format(self.name, move_name))

    def to_dict(self):
        return {
            constants.FAINTED: self.fainted,
            constants.ID: self.name,
            constants.LEVEL: self.level,
            constants.HITPOINTS: self.hp,
            constants.MAXHP: self.max_hp,
            constants.ABILITY: self.ability,
            constants.ITEM: self.item,
            constants.BASESTATS: self.base_stats,
            constants.STATS: self.stats,
            constants.BOOSTS: self.boosts,
            constants.STATUS: self.status,
            constants.VOLATILE_STATUS: set(self.volatile_statuses),
            constants.MOVES: [m.to_dict() for m in self.moves],
            constants.TYPES: self.types,
            constants.CAN_MEGA_EVO: self.can_mega_evo
        }

    def __eq__(self, other):
        return self.name == other.name and self.level == other.level

    def __repr__(self):
        return "{}, level {}".format(self.name, self.level)
