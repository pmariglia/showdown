import math
from dataclasses import dataclass

import numpy as np

import sim.constants as constants
import re

import sim.helpers
from sim.data import all_move_json


natures = {
    'lonely': {
        'plus': constants.StatEnum.ATTACK,
        'minus': constants.StatEnum.DEFENSE
    },
    'adamant': {
        'plus': constants.StatEnum.ATTACK,
        'minus': constants.StatEnum.SPECIAL_ATTACK
    },
    'naughty': {
        'plus': constants.StatEnum.ATTACK,
        'minus': constants.StatEnum.SPECIAL_DEFENSE
    },
    'brave': {
        'plus': constants.StatEnum.ATTACK,
        'minus': constants.StatEnum.SPEED
    },
    'bold': {
        'plus': constants.StatEnum.DEFENSE,
        'minus': constants.StatEnum.ATTACK
    },
    'impish': {
        'plus': constants.StatEnum.DEFENSE,
        'minus': constants.StatEnum.SPECIAL_ATTACK
    },
    'lax': {
        'plus': constants.StatEnum.DEFENSE,
        'minus': constants.StatEnum.SPECIAL_DEFENSE
    },
    'relaxed': {
        'plus': constants.StatEnum.DEFENSE,
        'minus': constants.StatEnum.SPEED
    },
    'modest': {
        'plus': constants.StatEnum.SPECIAL_ATTACK,
        'minus': constants.StatEnum.ATTACK
    },
    'mild': {
        'plus': constants.StatEnum.SPECIAL_ATTACK,
        'minus': constants.StatEnum.DEFENSE
    },
    'rash': {
        'plus': constants.StatEnum.SPECIAL_ATTACK,
        'minus': constants.StatEnum.SPECIAL_DEFENSE
    },
    'quiet': {
        'plus': constants.StatEnum.SPECIAL_ATTACK,
        'minus': constants.StatEnum.SPEED
    },
    'calm': {
        'plus': constants.StatEnum.SPECIAL_DEFENSE,
        'minus': constants.StatEnum.ATTACK
    },
    'gentle': {
        'plus': constants.StatEnum.SPECIAL_DEFENSE,
        'minus': constants.StatEnum.DEFENSE
    },
    'careful': {
        'plus': constants.StatEnum.SPECIAL_DEFENSE,
        'minus': constants.StatEnum.SPECIAL_ATTACK
    },
    'sassy': {
        'plus': constants.StatEnum.SPECIAL_DEFENSE,
        'minus': constants.StatEnum.SPEED
    },
    'timid': {
        'plus': constants.StatEnum.SPEED,
        'minus': constants.StatEnum.ATTACK
    },
    'hasty': {
        'plus': constants.StatEnum.SPEED,
        'minus': constants.StatEnum.DEFENSE
    },
    'jolly': {
        'plus': constants.StatEnum.SPEED,
        'minus': constants.StatEnum.SPECIAL_ATTACK
    },
    'naive': {
        'plus': constants.StatEnum.SPEED,
        'minus': constants.StatEnum.SPECIAL_DEFENSE
    },
}


class StatTable:
    __slots__ = ('stats', 'index')
    lb = 0
    ub = 8
    dtype = float
    min_value = 0
    max_value = np.inf
    default_val = None

    def __init__(self, stats):
        self.index = self.lb
        if stats is None:
            self.stats = np.zeros(8)
            return
        if isinstance(stats, StatTable):
            self.stats = stats.stats
        else:
            self.stats = np.zeros(len(constants.StatEnum), dtype=self.dtype)
            self.stats[self.lb:self.ub] = stats

    def __getitem__(self, key: constants.StatEnum):
        return self.stats[key]

    def __setitem__(self, key: constants.StatEnum, value):
        self.stats[key] = value

    def __mul__(self, other):
        if isinstance(other, StatTable):
            temp = StatTable(self.stats * other.stats)
            temp.clamp()
            return temp

    def __add__(self, other):
        if isinstance(other, StatTable):
            test = type(self)(None)
            test.stats = self.stats + other.stats
            test.clamp()
            return test

    def __neg__(self):
        to_return = type(self)(None)
        to_return.stats = -self.stats
        return to_return

    def __sub__(self, other):
        if isinstance(other, StatTable):
            return self + (-other)

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < self.ub:
            return_pair = constants.StatEnum(self.index), self.stats[self.index]
            self.index += 1
            return return_pair
        else:
            self.index = self.lb
            raise StopIteration

    def __repr__(self):
        return str({constants.StatEnum(i).name: self.stats[i] for i in range(self.lb, self.ub)
                    if self.stats[i] != self.default_val})

    def clamp(self):
        self.stats = np.fmax(self.min_value, np.fmin(self.stats, self.max_value))

    def to_dict(self):
        return {k: v for k, v in self if v != self.default_val}

    def __eq__(self, other):
        if isinstance(other, StatTable):
            return (self.stats == other.stats).all()
        return False

    @classmethod
    def from_dict(cls, temp):
        to_return = cls(None)
        if isinstance(temp, tuple | list):
            to_return[cls.lb:cls.ub] = temp
            return to_return
        if temp is None:
            return to_return
        for k, v in temp.items():
            if not isinstance(k, constants.StatEnum):
                k = constants.STAT_AND_ABBR_LOOKUP[k]
            to_return[k] = v
        return to_return


class EVS(StatTable):
    lb = 0
    ub = 6
    dtype = int
    max_value = 255
    min_value = 0
    default_val = 85

    def __init__(self, stats=(85,) * 6):
        super().__init__(stats)

    def __add__(self, other):
        to_return = super().__add__(other)
        to_return.stats = np.fmax(self.min_value, np.fmin(to_return.stats, self.max_value))



class IVS(StatTable):
    ub = 6
    lb = 0
    dtype = int
    max_value = 31
    min_value = 0
    default_val = 31

    def __init__(self, stats=(31,) * 6):
        super().__init__(stats)


class BaseStats(StatTable):
    ub = 6
    lb = 0
    default_val = 100
    dtype = int

    def __init__(self, stats=(100,) * 6):
        super().__init__(stats)


class Boosts(StatTable):
    ub = 8
    lb = 1
    dtype = int
    max_value = 6
    min_value = -6
    default_val = 0

    def __init__(self, stats=(0,)*7):
        super().__init__(stats)

    def clear(self):
        self.stats = np.zeros(8)


class Stats(StatTable):
    ub = 6
    lb = 0

    def __init__(self, stats):
        super().__init__(stats)

    @classmethod
    def create_stats(cls, base_stats, evs, ivs, nature, level):
        stats = calculate_stats(base_stats, level, ivs, evs, nature)
        return Stats(stats[0:6])

    def __eq__(self, other):
        if isinstance(other, Stats):
            return (self.stats[1:6] == other.stats[1:6]).all()

    def clamp(self):
        super().clamp()
        self.stats = np.floor(self.stats)


@dataclass
class Move:
    id: str
    current_pp: int
    max_pp: int
    disabled: bool

    @classmethod
    def from_dict(cls, data):
        to_return = Move('', 0, 0, False)
        to_return.id = data[constants.ID]
        to_return.max_pp = data.get(constants.PP, int(1.6 * all_move_json[to_return.id][constants.PP]))
        to_return.current_pp = data.get(constants.CURRENT_PP, to_return.max_pp)
        to_return.disabled = data.get(constants.DISABLED, False)
        return to_return

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.id
        return self.id == other.id


def get_pokemon_info_from_condition(condition_string: str):
    if constants.FNT in condition_string:
        return 0, 0, None

    split_string = condition_string.split("/")
    hp = int(split_string[0])
    if any(s in condition_string for s in constants.NON_VOLATILE_STATUSES):
        maxhp, status = split_string[1].split(' ')
        maxhp = int(maxhp)
        return hp, maxhp, status
    else:
        maxhp = int(split_string[1])
        return hp, maxhp, None


regex = re.compile('[^a-z?]')


def normalize_name(name):
    return regex.sub('', name.casefold())


def set_makes_sense(nature, spread, item, ability, moves):
    if item in constants.CHOICE_ITEMS and any(all_move_json[m.name][
                                                  constants.CATEGORY] not in constants.DAMAGING_CATEGORIES and m.name != 'trick' for m in moves):
        return False
    return True


def spreads_are_alike(s1, s2):
    if s1[0] != s2[0]:
        return False

    s1 = [int(v) for v in s1[1].split(',')]
    s2 = [int(v) for v in s2[1].split(',')]

    diff = [abs(i-j) for i, j in zip(s1, s2)]

    # 24 is arbitrarily chosen as the threshold for EVs to be "alike"
    return all(v < 24 for v in diff)


def remove_duplicate_spreads(list_of_spreads):
    new_spreads = list()

    for s1 in list_of_spreads:
        if not any(spreads_are_alike(s1, s2) for s2 in new_spreads):
            new_spreads.append(s1)

    return new_spreads


def update_stats_from_nature(stats, nature):
    try:
        stats[natures[nature]['plus']] *= 1.1
        stats[natures[nature]['minus']] /= 1.1
        stats = np.floor(stats)
    except KeyError:
        pass

    return stats


def common_pkmn_stat_calc(stat: int, iv: int, ev: int, level: int):
    return math.floor(((2 * stat + iv + math.floor(ev / 4)) * level) / 100)


def common_pkmn_stat_calc_np(stat, iv, ev, level):
    return np.floor(((2 * stat.stats + iv.stats + np.floor(ev.stats / 4)) * level) / 100)


def calculate_stats(base_stats, level, ivs, evs, nature='serious'):
    new_stats = common_pkmn_stat_calc_np(base_stats, ivs, evs, level)
    new_stats[0] += level + 10
    new_stats[1:6] += 5
    new_stats = update_stats_from_nature(new_stats, nature)
    return sim.helpers.Stats(new_stats[:6])
