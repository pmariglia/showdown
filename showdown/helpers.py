import math
import constants

from data import all_move_json


boost_multiplier_lookup = {
    -6: 2/8,
    -5: 2/7,
    -4: 2/6,
    -3: 2/5,
    -2: 2/4,
    -1: 2/3,
    0: 2/2,
    1: 3/2,
    2: 4/2,
    3: 5/2,
    4: 6/2,
    5: 7/2,
    6: 8/2
}


accuracy_multiplier_lookup = {
    -6: 3/9,
    -5: 3/8,
    -4: 3/7,
    -3: 3/6,
    -2: 3/5,
    -1: 3/4,
    0: 3/3,
    1: 4/3,
    2: 5/3,
    3: 6/3,
    4: 7/3,
    5: 8/3,
    6: 9/3
}


def battle_is_over(state):
    if state.self.active.hp <= 0 and not any(pkmn.hp for pkmn in state.self.reserve.values()):
        return -1
    elif state.opponent.active.hp <= 0 and not any(pkmn.hp for pkmn in state.opponent.reserve.values()) and len(state.opponent.reserve) == 5:
        return 1

    return False


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
    if item in constants.CHOICE_ITEMS and any(all_move_json[m][constants.CATEGORY] not in constants.DAMAGING_CATEGORIES and m != 'trick' for m in moves):
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


def _update_stats_from_nature(stats, nature):
    if nature in ['lonely', 'adamant', 'naughty', 'brave']:
        stats[constants.ATTACK] *= 1.1
    if nature in ['bold', 'impish', 'lax', 'relaxed']:
        stats[constants.DEFENSE] *= 1.1
    if nature in ['modest', 'mild', 'rash', 'quiet']:
        stats[constants.SPECIAL_ATTACK] *= 1.1
    if nature in ['calm', 'gentle', 'careful', 'sassy']:
        stats[constants.SPECIAL_ATTACK] *= 1.1
    if nature in ['timid', 'hasty', 'jolly', 'naive']:
        stats[constants.SPEED] *= 1.1

    if nature in ['bold', 'modest', 'calm', 'timid']:
        stats[constants.ATTACK] /= 1.1
    if nature in ['lonely', 'mild', 'gentle', 'hasty']:
        stats[constants.DEFENSE] /= 1.1
    if nature in ['adamant', 'impish', 'careful', 'jolly']:
        stats[constants.SPECIAL_ATTACK] /= 1.1
    if nature in ['naughty', 'lax', 'rash', 'naive']:
        stats[constants.SPECIAL_DEFENSE] /= 1.1
    if nature in ['brave', 'relaxed', 'quiet', 'sassy']:
        stats[constants.SPEED] /= 1.1


def calculate_stats(base_stats, level, ivs=(31,) * 6, evs=(85,) * 6, nature='serious'):

    def _common_pkmn_stat_calc(stat: int, iv: int, ev: int, level: int):
        return math.floor(((2 * stat + iv + math.floor(ev / 4)) * level) / 100)

    new_stats = dict()

    new_stats[constants.HITPOINTS] = _common_pkmn_stat_calc(base_stats[constants.HITPOINTS],
                                                            ivs[0],
                                                            evs[0],
                                                            level) + level + 10

    new_stats[constants.ATTACK] = _common_pkmn_stat_calc(base_stats[constants.ATTACK],
                                                         ivs[1],
                                                         evs[1],
                                                         level) + 5

    new_stats[constants.DEFENSE] = _common_pkmn_stat_calc(base_stats[constants.DEFENSE],
                                                          ivs[2],
                                                          evs[2],
                                                          level) + 5

    new_stats[constants.SPECIAL_ATTACK] = _common_pkmn_stat_calc(base_stats[constants.SPECIAL_ATTACK],
                                                                 ivs[3],
                                                                 evs[3],
                                                                 level) + 5

    new_stats[constants.SPECIAL_DEFENSE] = _common_pkmn_stat_calc(base_stats[constants.SPECIAL_DEFENSE],
                                                                  ivs[4],
                                                                  evs[4],
                                                                  level) + 5
    new_stats[constants.SPEED] = _common_pkmn_stat_calc(base_stats[constants.SPEED],
                                                        ivs[5],
                                                        evs[5],
                                                        level) + 5

    _update_stats_from_nature(new_stats, nature)
    new_stats = {k: int(v) for k, v in new_stats.items()}
    return new_stats
