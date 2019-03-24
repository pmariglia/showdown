from showdown.helpers import normalize_name
import constants
from . import scoring


cache = dict()


def evaluate_pokemon(pkmn):

    try:
        return cache[(pkmn.hp, pkmn.maxhp, pkmn.attack_boost, pkmn.defense_boost, pkmn.special_attack_boost, pkmn.special_defense_boost, pkmn.speed_boost, pkmn.status) + tuple(pkmn.volatile_status)]
    except KeyError:
        pass

    score = 0
    if pkmn.hp <= 0:
        return score

    # an alive pokemon's value decreases as it passes certain HP-percentage barriers
    pkmn_hp_percent = (float(pkmn.hp) / pkmn.maxhp)
    for k in sorted(scoring.POKEMON_ALIVE):
        if pkmn_hp_percent <= k:
            score += scoring.POKEMON_ALIVE[k]
            break

    score += scoring.POKEMON_HP * pkmn_hp_percent

    # boosts have diminishing returns in terms of value to the evaluation
    score += scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.attack_boost] * scoring.POKEMON_BOOSTS[constants.ATTACK]
    score += scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.defense_boost] * scoring.POKEMON_BOOSTS[constants.DEFENSE]
    score += scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.special_attack_boost] * scoring.POKEMON_BOOSTS[constants.SPECIAL_ATTACK]
    score += scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.special_defense_boost] * scoring.POKEMON_BOOSTS[constants.SPECIAL_DEFENSE]
    score += scoring.POKEMON_BOOST_DIMINISHING_RETURNS[pkmn.speed_boost] * scoring.POKEMON_BOOSTS[constants.SPEED]

    score += scoring.POKEMON_STATUSES[pkmn.status]

    for vol_stat in pkmn.volatile_status:
        try:
            score += scoring.POKEMON_VOLATILE_STATUSES[normalize_name(vol_stat)]
        except KeyError:
            pass

    score = round(score)

    cache[(pkmn.hp, pkmn.maxhp, pkmn.attack_boost, pkmn.defense_boost, pkmn.special_attack_boost, pkmn.special_defense_boost, pkmn.speed_boost, pkmn.status) + tuple(pkmn.volatile_status)] = score

    return score
