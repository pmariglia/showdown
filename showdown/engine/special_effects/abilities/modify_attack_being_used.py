import constants

from ...damage_calculator import is_not_very_effective
from ...damage_calculator import is_super_effective


def analytic(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if not first_move:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.3
    return attacking_move


def adaptability(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] in attacking_pokemon.types:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = int(attacking_move[constants.BASE_POWER] * 4/3)
    return attacking_move


def aerilate(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'normal':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = int(attacking_move[constants.BASE_POWER] * 1.2)
        attacking_move[constants.TYPE] = 'flying'
    return attacking_move


def galvanize(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'normal':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = int(attacking_move[constants.BASE_POWER] * 1.2)
        attacking_move[constants.TYPE] = 'electric'
    return attacking_move


def liquidvoice(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if constants.SOUND in attacking_move[constants.FLAGS]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.TYPE] = 'water'
    return attacking_move


def compoundeyes(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.ACCURACY] is not True:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] *= 1.3
    return attacking_move


def contrary(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    # look at this logic, I want to fucking die
    if attacking_move[constants.TARGET] in constants.MOVE_TARGET_SELF:
        attacking_move = attacking_move.copy()
        if constants.BOOSTS in attacking_move:
            attacking_move[constants.BOOSTS] = attacking_move[constants.BOOSTS].copy()
            for k, v in attacking_move[constants.BOOSTS].items():
                attacking_move[constants.BOOSTS][k] = -1*v
        if attacking_move[constants.SECONDARY] and constants.BOOSTS in attacking_move[constants.SECONDARY]:
            attacking_move[constants.SECONDARY] = attacking_move[constants.SECONDARY].copy()
            attacking_move[constants.SECONDARY][constants.BOOSTS] = attacking_move[constants.SECONDARY][constants.BOOSTS].copy()
            for k, v in attacking_move[constants.SECONDARY][constants.BOOSTS].items():
                attacking_move[constants.SECONDARY][constants.BOOSTS][k] = -1*v
    elif constants.SELF in attacking_move and constants.BOOSTS in attacking_move[constants.SELF]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.SELF] = attacking_move[constants.SELF].copy()
        attacking_move[constants.SELF][constants.BOOSTS] = attacking_move[constants.SELF][constants.BOOSTS].copy()
        for k, v in attacking_move[constants.SELF][constants.BOOSTS].items():
            attacking_move[constants.SELF][constants.BOOSTS][k] = -1 * v

    elif attacking_move[constants.SECONDARY] and constants.SELF in attacking_move[constants.SECONDARY]:
        if constants.BOOSTS in attacking_move[constants.SECONDARY][constants.SELF]:
            attacking_move = attacking_move.copy()
            attacking_move[constants.SECONDARY] = attacking_move[constants.SECONDARY].copy()
            attacking_move[constants.SECONDARY][constants.SELF] = attacking_move[constants.SECONDARY][constants.SELF].copy()
            attacking_move[constants.SECONDARY][constants.SELF][constants.BOOSTS] = attacking_move[constants.SECONDARY][constants.SELF][constants.BOOSTS].copy()
            for k, v in attacking_move[constants.SECONDARY][constants.SELF][constants.BOOSTS].items():
                attacking_move[constants.SECONDARY][constants.SELF][constants.BOOSTS][k] = -1 * v

    return attacking_move


def hustle(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] *= 0.8
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def ironfist(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if "punch" in attacking_move[constants.FLAGS]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def megalauncher(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if "pulse" in attacking_move[constants.FLAGS]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def noguard(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    attacking_move = attacking_move.copy()
    attacking_move[constants.ACCURACY] = True
    return attacking_move


def pixilate(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'normal':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = int(attacking_move[constants.BASE_POWER] * 1.2)
        attacking_move[constants.TYPE] = 'fairy'
    return attacking_move


def refrigerate(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'normal':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = int(attacking_move[constants.BASE_POWER] * 1.2)
        attacking_move[constants.TYPE] = 'ice'
    return attacking_move


def scrappy(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    # this logic is technically wrong, but it at least allows the move to hit
    # for example, a fighting move on ice/ghost should technically be super-effective
    # this logic would make it do neutral damage instead
    if 'ghost' in defending_pokemon.types:
        attacking_move = attacking_move.copy()
        attacking_move[constants.TYPE] = "typeless"
    return attacking_move


def serenegrace(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.SECONDARY]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.SECONDARY] = attacking_move[constants.SECONDARY].copy()
        attacking_move[constants.SECONDARY][constants.CHANCE] *= 2
        if attacking_move[constants.SECONDARY][constants.CHANCE] > 100:
            attacking_move[constants.SECONDARY][constants.CHANCE] = 100
    return attacking_move


def sheerforce(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.SECONDARY]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.SECONDARY] = False
        attacking_move[constants.BASE_POWER] *= 1.3
    return attacking_move


def strongjaw(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if "bite" in attacking_move[constants.FLAGS]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def technician(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.BASE_POWER] <= 60:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def toughclaws(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if "contact" in attacking_move[constants.FLAGS]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.3
    return attacking_move


def toxicboost(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        if attacking_pokemon.status in [constants.POISON, constants.TOXIC]:
            attacking_move = attacking_move.copy()
            attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def hugepower(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 2
    return attacking_move


def guts(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_pokemon.status is not None and attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
        if attacking_pokemon.status == constants.BURN:
            attacking_move[constants.BASE_POWER] *= 2
    return attacking_move


def reckless(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if constants.RECOIL in attacking_move:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def rockhead(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if constants.RECOIL in attacking_move:
        attacking_move = attacking_move.copy()
        del attacking_move[constants.RECOIL]
    return attacking_move


def parentalbond(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    attacking_move = attacking_move.copy()
    attacking_move[constants.BASE_POWER] *= 1.25
    return attacking_move


def tintedlens(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if is_not_very_effective(attacking_move[constants.TYPE], defending_pokemon.types):
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 2
    return attacking_move


def skilllink(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.ID] in ['bulletseed', 'iciclespear', 'pinmissile', 'rockblast', 'tailslap', 'watershuriken']:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 5
    return attacking_move


def waterbubble(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'water':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 2

    return attacking_move


def steelworker(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'steel':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def neuroforce(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if is_super_effective(attacking_move[constants.TYPE], defending_pokemon.types):
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.25
    return attacking_move


def blaze(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'fire' and (attacking_pokemon.hp / attacking_pokemon.maxhp) <= 1/3:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def torrent(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'water' and (attacking_pokemon.hp / attacking_pokemon.maxhp) <= 1/3:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5

    return attacking_move


def overgrow(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'grass' and (attacking_pokemon.hp / attacking_pokemon.maxhp) <= 1/3:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def swarm(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'bug' and (attacking_pokemon.hp / attacking_pokemon.maxhp) <= 1/3:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def defeatist(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_pokemon.hp*2 <= attacking_pokemon.maxhp:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 0.5

    return attacking_move


def sandforce(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if weather == constants.SAND and attacking_move[constants.TYPE] in ['ground', 'rock', 'steel']:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.3
    return attacking_move


def darkaura(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'dark' and defending_pokemon.ability != 'aurabreak':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.33

    return attacking_move


def fairyaura(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'fairy' and defending_pokemon.ability != 'aurabreak':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.33
    return attacking_move


def prankster(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if 'dark' in defending_pokemon.types and attacking_move[constants.CATEGORY] == constants.STATUS:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = False
    return attacking_move


def gorillatactics(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def punkrock(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if constants.SOUND in attacking_move[constants.FLAGS]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.3
    return attacking_move


def steelyspirit(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'steel':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def stakeout(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if constants.SWITCH_STRING in defending_move:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 2
    return attacking_move


def solarpower(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if weather in [constants.SUN, constants.DESOLATE_LAND]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def transistor(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'electric':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def dragonsmaw(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_move[constants.TYPE] == 'dragon':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


ability_lookup = {
    'transistor': transistor,
    'dragonsmaw': dragonsmaw,
    'solarpower': solarpower,
    'liquidvoice': liquidvoice,
    'stakeout': stakeout,
    'steelyspirit': steelyspirit,
    'punkrock': punkrock,
    'gorillatactics': gorillatactics,
    'prankster': prankster,
    'toughclaws': toughclaws,
    'fairyaura': fairyaura,
    'darkaura': darkaura,
    'sandforce': sandforce,
    'defeatist': defeatist,
    'swarm': swarm,
    'overgrow': overgrow,
    'torrent': torrent,
    'blaze': blaze,
    'neuroforce': neuroforce,
    'steelworker': steelworker,
    'galvanize': galvanize,
    'waterbubble': waterbubble,
    'adaptability': adaptability,
    'analytic': analytic,
    'aerilate': aerilate,
    'compoundeyes': compoundeyes,
    'contrary': contrary,
    'hustle': hustle,
    'ironfist': ironfist,
    'megalauncher': megalauncher,
    'noguard': noguard,
    'pixilate': pixilate,
    'refrigerate': refrigerate,
    'scrappy': scrappy,
    'serenegrace': serenegrace,
    'sheerforce': sheerforce,
    'strongjaw': strongjaw,
    'technician': technician,
    'hugepower': hugepower,
    'purepower': hugepower,
    'reckless': reckless,
    'rockhead': rockhead,
    'guts': guts,
    'parentalbond': parentalbond,
    'toxicboost': toxicboost,
    'tintedlens': tintedlens,
    'skilllink': skilllink
}


def ability_modify_attack_being_used(ability_name, attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather):
    if attacking_pokemon.ability == 'neutralizinggas' or defending_pokemon.ability == 'neutralizinggas':
        return attacking_move
    ability_func = ability_lookup.get(ability_name)
    if ability_func is not None:
        return ability_func(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move, weather)
    else:
        return attacking_move
