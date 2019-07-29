from showdown.helpers import normalize_name
import constants
from . import scoring


def evaluate_pokemon(pkmn):
    score = 0
    if pkmn.hp <= 0:
        return score

    score += scoring.POKEMON_ALIVE_STATIC
    score += scoring.POKEMON_HP * (float(pkmn.hp) / pkmn.maxhp)

    # boosts have diminishing returns
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

    return round(score)
