import math
import constants

from data import all_move_json


natures = {
    'lonely': {
        'plus': constants.ATTACK,
        'minus': constants.DEFENSE
    },
    'adamant': {
        'plus': constants.ATTACK,
        'minus': constants.SPECIAL_ATTACK
    },
    'naughty': {
        'plus': constants.ATTACK,
        'minus': constants.SPECIAL_DEFENSE
    },
    'brave': {
        'plus': constants.ATTACK,
        'minus': constants.SPEED
    },
    'bold': {
        'plus': constants.DEFENSE,
        'minus': constants.ATTACK
    },
    'impish': {
        'plus': constants.DEFENSE,
        'minus': constants.SPECIAL_ATTACK
    },
    'lax': {
        'plus': constants.DEFENSE,
        'minus': constants.SPECIAL_DEFENSE
    },
    'relaxed': {
        'plus': constants.DEFENSE,
        'minus': constants.SPEED
    },
    'modest': {
        'plus': constants.SPECIAL_ATTACK,
        'minus': constants.ATTACK
    },
    'mild': {
        'plus': constants.SPECIAL_ATTACK,
        'minus': constants.DEFENSE
    },
    'rash': {
        'plus': constants.SPECIAL_ATTACK,
        'minus': constants.SPECIAL_DEFENSE
    },
    'quiet': {
        'plus': constants.SPECIAL_ATTACK,
        'minus': constants.SPEED
    },
    'calm': {
        'plus': constants.SPECIAL_DEFENSE,
        'minus': constants.ATTACK
    },
    'gentle': {
        'plus': constants.SPECIAL_DEFENSE,
        'minus': constants.DEFENSE
    },
    'careful': {
        'plus': constants.SPECIAL_DEFENSE,
        'minus': constants.SPECIAL_ATTACK
    },
    'sassy': {
        'plus': constants.SPECIAL_DEFENSE,
        'minus': constants.SPEED
    },
    'timid': {
        'plus': constants.SPEED,
        'minus': constants.ATTACK
    },
    'hasty': {
        'plus': constants.SPEED,
        'minus': constants.DEFENSE
    },
    'jolly': {
        'plus': constants.SPEED,
        'minus': constants.SPECIAL_ATTACK
    },
    'naive': {
        'plus': constants.SPEED,
        'minus': constants.SPECIAL_DEFENSE
    },
}


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


def normalize_name(name):
    return name\
        .replace(" ", "")\
        .replace("-", "")\
        .replace(".", "")\
        .replace("\'", "")\
        .replace("%", "")\
        .replace("*", "")\
        .replace(":", "")\
        .strip()\
        .lower()\
        .encode('ascii', 'ignore')\
        .decode('utf-8')


def set_makes_sense(nature, spread, item, ability, moves):
    if item in constants.CHOICE_ITEMS and any(all_move_json[m.name][constants.CATEGORY] not in constants.DAMAGING_CATEGORIES and m.name != 'trick' for m in moves):
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
    new_stats = stats.copy()
    try:
        new_stats[natures[nature]['plus']] *= 1.1
        new_stats[natures[nature]['minus']] /= 1.1
    except KeyError:
        pass

    return new_stats


def common_pkmn_stat_calc(stat: int, iv: int, ev: int, level: int):
    return math.floor(((2 * stat + iv + math.floor(ev / 4)) * level) / 100)


def calculate_stats(base_stats, level, ivs=(31,) * 6, evs=(85,) * 6, nature='serious'):
    new_stats = dict()

    new_stats[constants.HITPOINTS] = common_pkmn_stat_calc(
        base_stats[constants.HITPOINTS],
        ivs[0],
        evs[0],
        level
    ) + level + 10

    new_stats[constants.ATTACK] = common_pkmn_stat_calc(
        base_stats[constants.ATTACK],
        ivs[1],
        evs[1],
        level
    ) + 5

    new_stats[constants.DEFENSE] = common_pkmn_stat_calc(
        base_stats[constants.DEFENSE],
        ivs[2],
        evs[2],
        level
    ) + 5

    new_stats[constants.SPECIAL_ATTACK] = common_pkmn_stat_calc(
        base_stats[constants.SPECIAL_ATTACK],
        ivs[3],
        evs[3],
        level
    ) + 5

    new_stats[constants.SPECIAL_DEFENSE] = common_pkmn_stat_calc(
        base_stats[constants.SPECIAL_DEFENSE],
        ivs[4],
        evs[4],
        level
    ) + 5

    new_stats[constants.SPEED] = common_pkmn_stat_calc(
        base_stats[constants.SPEED],
        ivs[5],
        evs[5],
        level
    ) + 5

    new_stats = update_stats_from_nature(new_stats, nature)
    new_stats = {k: int(v) for k, v in new_stats.items()}
    return new_stats
