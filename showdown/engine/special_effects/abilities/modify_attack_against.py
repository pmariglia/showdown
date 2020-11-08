import constants

from ...damage_calculator import is_super_effective


def levitate(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'ground' and attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT and attacking_move[constants.ID] != 'thousandarrows':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = 0
    return attacking_move


def lightningrod(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'electric' and attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = True
        attacking_move[constants.BASE_POWER] = 0
        attacking_move[constants.TARGET] = constants.NORMAL
        attacking_move[constants.CATEGORY] = constants.STATUS
        attacking_move[constants.BOOSTS] = {
            constants.SPECIAL_ATTACK: 1
        }
    return attacking_move


def stormdrain(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'water' and attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = True
        attacking_move[constants.BASE_POWER] = 0
        attacking_move[constants.TARGET] = constants.NORMAL
        attacking_move[constants.CATEGORY] = constants.STATUS
        attacking_move[constants.BOOSTS] = {
            constants.SPECIAL_ATTACK: 1
        }
    return attacking_move


def voltabsorb(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'electric' and attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = True
        attacking_move[constants.BASE_POWER] = 0
        attacking_move[constants.HEAL_TARGET] = constants.NORMAL
        attacking_move[constants.CATEGORY] = constants.STATUS
        attacking_move[constants.HEAL] = [
            1,
            4
        ]
    return attacking_move


def waterabsorb(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'water' and attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = True
        attacking_move[constants.BASE_POWER] = 0
        attacking_move[constants.HEAL_TARGET] = constants.NORMAL
        attacking_move[constants.CATEGORY] = constants.STATUS
        attacking_move[constants.HEAL] = [
            1,
            4
        ]
    return attacking_move


def motordrive(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'electric' and attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = True
        attacking_move[constants.BASE_POWER] = 0
        attacking_move[constants.TARGET] = constants.NORMAL
        attacking_move[constants.CATEGORY] = constants.STATUS
        attacking_move[constants.BOOSTS] = {
            constants.SPEED: 1
        }
    return attacking_move


def sapsipper(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'grass' and attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = True
        attacking_move[constants.BASE_POWER] = 0
        attacking_move[constants.VOLATILE_STATUS] = None
        attacking_move[constants.TARGET] = constants.NORMAL
        attacking_move[constants.CATEGORY] = constants.STATUS
        attacking_move[constants.BOOSTS] = {
            constants.ATTACK: 1
        }
    return attacking_move


def multiscale(attacking_move, attacking_pokemon, defending_pokemon):
    if defending_pokemon.hp >= defending_pokemon.maxhp:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] /= 2

    return attacking_move


def thickfat(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] in ['fire', 'ice']:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] /= 2
    return attacking_move


def solidrock(attacking_move, attacking_pokemon, defending_pokemon):
    if is_super_effective(attacking_move[constants.TYPE], defending_pokemon.types):
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= (3/4)
    return attacking_move


def contrary(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
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

    return attacking_move


def noguard(attacking_move, attacking_pokemon, defending_pokemon):
    attacking_move = attacking_move.copy()
    attacking_move[constants.ACCURACY] = True
    return attacking_move


def flashfire(attacking_move, attacking_pokemon, defending_pokemon):
    # does not account for the 'flashfire' volatile status
    if attacking_move[constants.TYPE] == 'fire':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = 0
        attacking_move[constants.STATUS] = None
    return attacking_move


def bulletproof(attacking_move, attacking_pokemon, defending_pokemon):
    if 'bullet' in attacking_move[constants.FLAGS]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = 0
    return attacking_move


def furcoat(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 0.5
    return attacking_move


def fluffy(attacking_move, attacking_pokemon, defending_pokemon):
    if constants.CONTACT in attacking_move[constants.FLAGS]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 0.5
    if attacking_move[constants.TYPE] == 'fire':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 2
    return attacking_move


def magicbounce(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.FLAGS].get(constants.REFLECTABLE):
        attacking_move = attacking_move.copy()
        attacking_move[constants.TARGET] = constants.SELF

    return attacking_move


def ironbarbs(attacking_move, attacking_pokemon, defending_pokemon):
    if constants.CONTACT in attacking_move[constants.FLAGS]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.HEAL] = [-1, 8]
        attacking_move[constants.HEAL_TARGET] = constants.SELF
    return attacking_move


def roughskin(attacking_move, attacking_pokemon, defending_pokemon):
    if constants.CONTACT in attacking_move[constants.FLAGS]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.HEAL] = [-1, 16]
        attacking_move[constants.HEAL_TARGET] = constants.SELF
    return attacking_move


def wonderguard(attacking_move, attacking_pokemon, defending_pokemon):
    if not is_super_effective(attacking_move[constants.TYPE], defending_pokemon.types):
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = 0
    return attacking_move


def stamina(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.CATEGORY] in constants.DAMAGING_CATEGORIES:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BOOSTS] = {constants.DEFENSE: 1}

    return attacking_move


def waterbubble(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'fire':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] /= 2

    return attacking_move


def queenlymajesty(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.PRIORITY] > 0:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = 0

    return attacking_move


def tanglinghair(attacking_move, attacking_pokemon, defending_pokemon):
    if constants.CONTACT in attacking_move[constants.FLAGS]:
        attacking_move = attacking_move.copy()
        if constants.SELF in attacking_move:
            attacking_move[constants.SELF] = attacking_move[constants.SELF].copy()
        else:
            attacking_move[constants.SELF] = dict()

        if constants.BOOSTS in attacking_move[constants.SELF]:
            attacking_move[constants.SELF][constants.BOOSTS] = attacking_move[constants.SELF][constants.BOOSTS].copy()
        else:
            attacking_move[constants.SELF][constants.BOOSTS] = dict()

        if constants.SPEED in attacking_move[constants.SELF][constants.BOOSTS]:
            attacking_move[constants.SELF][constants.BOOSTS][constants.SPEED] -= 1
        else:
            attacking_move[constants.SELF][constants.BOOSTS][constants.SPEED] = -1

    return attacking_move


def cottondown(attacking_move, attacking_pokemon, defending_pokemon):
    attacking_move = attacking_move.copy()
    if constants.SELF in attacking_move:
        attacking_move[constants.SELF] = attacking_move[constants.SELF].copy()
    else:
        attacking_move[constants.SELF] = dict()

    if constants.BOOSTS in attacking_move[constants.SELF]:
        attacking_move[constants.SELF][constants.BOOSTS] = attacking_move[constants.SELF][constants.BOOSTS].copy()
    else:
        attacking_move[constants.SELF][constants.BOOSTS] = dict()

    if constants.SPEED in attacking_move[constants.SELF][constants.BOOSTS]:
        attacking_move[constants.SELF][constants.BOOSTS][constants.SPEED] -= 1
    else:
        attacking_move[constants.SELF][constants.BOOSTS][constants.SPEED] = -1

    return attacking_move


def marvelscale(attacking_move, attacking_pokemon, defending_pokemon):
    if defending_pokemon.status is not None and attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] /= 1.5

    return attacking_move


def justified(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'dark' and attacking_move[constants.CATEGORY] in constants.DAMAGING_CATEGORIES:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BOOSTS] = {  # damaging moves dont have boosts so dont bother copying
            constants.ATTACK: 1
        }

    return attacking_move


def shielddust(attacking_move, attacking_pokemon, defending_pokemon):
    if constants.SECONDARY in attacking_move:
        attacking_move = attacking_move.copy()
        attacking_move[constants.SECONDARY] = False

    return attacking_move


def competitive(attacking_move, attacking_pokemon, defending_pokemon):
    attacking_move = attacking_move.copy()
    if constants.BOOSTS in attacking_move:
        attacking_move[constants.BOOSTS] = attacking_move[constants.BOOSTS].copy()
        for _ in attacking_move[constants.BOOSTS].copy():
            if constants.SPECIAL_ATTACK not in attacking_move[constants.BOOSTS]:
                attacking_move[constants.BOOSTS][constants.SPECIAL_ATTACK] = 2
            else:
                attacking_move[constants.BOOSTS][constants.SPECIAL_ATTACK] += 2

    elif attacking_move[constants.SECONDARY] and constants.BOOSTS in attacking_move[constants.SECONDARY]:
        attacking_move[constants.SECONDARY] = attacking_move[constants.SECONDARY].copy()
        attacking_move[constants.SECONDARY][constants.BOOSTS] = attacking_move[constants.SECONDARY][constants.BOOSTS].copy()
        for _ in attacking_move[constants.SECONDARY][constants.BOOSTS].copy():
            if constants.SPECIAL_ATTACK not in attacking_move[constants.SECONDARY][constants.BOOSTS]:
                attacking_move[constants.SECONDARY][constants.BOOSTS][constants.SPECIAL_ATTACK] = 2
            else:
                attacking_move[constants.SECONDARY][constants.BOOSTS][constants.SPECIAL_ATTACK] += 2

    return attacking_move


def defiant(attacking_move, attacking_pokemon, defending_pokemon):
    attacking_move = attacking_move.copy()
    if constants.BOOSTS in attacking_move:
        attacking_move[constants.BOOSTS] = attacking_move[constants.BOOSTS].copy()
        for _ in attacking_move[constants.BOOSTS].copy():
            if constants.ATTACK not in attacking_move[constants.BOOSTS]:
                attacking_move[constants.BOOSTS][constants.ATTACK] = 2
            else:
                attacking_move[constants.BOOSTS][constants.ATTACK] += 2

    elif attacking_move[constants.SECONDARY] and constants.BOOSTS in attacking_move[constants.SECONDARY]:
        attacking_move[constants.SECONDARY] = attacking_move[constants.SECONDARY].copy()
        attacking_move[constants.SECONDARY][constants.BOOSTS] = attacking_move[constants.SECONDARY][constants.BOOSTS].copy()
        for _ in attacking_move[constants.SECONDARY][constants.BOOSTS].copy():
            if constants.ATTACK not in attacking_move[constants.SECONDARY][constants.BOOSTS]:
                attacking_move[constants.SECONDARY][constants.BOOSTS][constants.ATTACK] = 2
            else:
                attacking_move[constants.SECONDARY][constants.BOOSTS][constants.ATTACK] += 2

    return attacking_move


def weakarmor(attacking_move, attacking_pokemon, defending_pokemon):
    if constants.PHYSICAL in attacking_move[constants.CATEGORY]:
        attacking_move = attacking_move.copy()
        if constants.BOOSTS in attacking_move:
            attacking_move[constants.BOOSTS] = attacking_move[constants.BOOSTS].copy()
        else:
            attacking_move[constants.BOOSTS] = dict()

        if constants.DEFENSE in attacking_move[constants.BOOSTS]:
            attacking_move[constants.BOOSTS][constants.DEFENSE] -= 1
        else:
            attacking_move[constants.BOOSTS][constants.DEFENSE] = -1

        if constants.SPEED in attacking_move[constants.BOOSTS]:
            attacking_move[constants.BOOSTS][constants.SPEED] += 2
        else:
            attacking_move[constants.BOOSTS][constants.SPEED] = 2

    return attacking_move


def liquidooze(attacking_move, attacking_pokemon, defending_pokemon):
    if constants.DRAIN in attacking_move:
        attacking_move = attacking_move.copy()
        attacking_move[constants.DRAIN] = attacking_move[constants.DRAIN].copy()
        attacking_move[constants.DRAIN][0] *= -1

    return attacking_move


def innerfocus(attacking_move, attacking_pokemon, defending_pokemon):
    if (
        attacking_move[constants.SECONDARY] and
        constants.VOLATILE_STATUS in attacking_move[constants.SECONDARY] and
        attacking_move[constants.SECONDARY][constants.VOLATILE_STATUS] == constants.FLINCH
    ):
        attacking_move = attacking_move.copy()
        attacking_move[constants.SECONDARY] = False

    return attacking_move


def soundproof(attacking_move, attacking_pokemon, defending_pokemon):
    if constants.SOUND in attacking_move[constants.FLAGS]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = False

    return attacking_move


def darkaura(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'dark' and attacking_pokemon.ability != 'aurabreak':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.33

    return attacking_move


def fairyaura(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'fairy' and attacking_pokemon.ability != 'aurabreak':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.33

    return attacking_move


def icescales(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.CATEGORY] == constants.SPECIAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 0.5

    return attacking_move


def punkrock(attacking_move, attacking_pokemon, defending_pokemon):
    if constants.SOUND in attacking_move[constants.FLAGS]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 0.5
    return attacking_move


def steamengine(attacking_move, attacking_pokemon, defending_pokemon):
    # duplicated from 'weakarmor'
    if attacking_move[constants.TYPE] in ['fire', 'water']:
        attacking_move = attacking_move.copy()
        if constants.BOOSTS in attacking_move:
            attacking_move[constants.BOOSTS] = attacking_move[constants.BOOSTS].copy()
        else:
            attacking_move[constants.BOOSTS] = dict()

        if constants.SPEED in attacking_move[constants.BOOSTS]:
            attacking_move[constants.BOOSTS][constants.SPEED] += 6
        else:
            attacking_move[constants.BOOSTS][constants.SPEED] = 6

    return attacking_move


def damp(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.ID] in ["explosion", "selfdestruct", "mistyexplosion", "mindblown"]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.HEAL] = [0, 1]
        attacking_move[constants.BASE_POWER] = 0

    return attacking_move


ability_lookup = {
    'damp': damp,
    'steamengine': steamengine,
    'punkrock': punkrock,
    'icescales': icescales,
    'fairyaura': fairyaura,
    'darkaura': darkaura,
    'soundproof': soundproof,
    'innerfocus': innerfocus,
    'liquidooze': liquidooze,
    'weakarmor': weakarmor,
    'defiant': defiant,
    'competitive': competitive,
    'shielddust': shielddust,
    'justified': justified,
    'marvelscale': marvelscale,
    'tanglinghair': tanglinghair,
    'cottondown': cottondown,
    'queenlymajesty': queenlymajesty,
    'waterbubble': waterbubble,
    'stamina': stamina,
    'levitate': levitate,
    'lightningrod': lightningrod,
    'stormdrain': stormdrain,
    'voltabsorb': voltabsorb,
    'waterabsorb': waterabsorb,
    'dryskin': waterabsorb,
    'motordrive': motordrive,
    'sapsipper': sapsipper,
    'multiscale': multiscale,
    'shadowshield': multiscale,
    'thickfat': thickfat,
    'solidrock': solidrock,
    'contrary': contrary,
    'noguard': noguard,
    'flashfire': flashfire,
    'bulletproof': bulletproof,
    'furcoat': furcoat,
    'prismarmor': solidrock,
    'filter': solidrock,
    'fluffy': fluffy,
    'ironbarbs': ironbarbs,
    'wonderguard': wonderguard,
    'roughskin': roughskin,
    'magicbounce': magicbounce
}


def ability_modify_attack_against(ability_name, attacking_move, attacking_pokemon, defending_pokemon):
    if (
        attacking_pokemon.ability == 'neutralizinggas' or
        defending_pokemon.ability == 'neutralizinggas' or
        attacking_pokemon.ability in constants.ABILITIES_THAT_IGNORE_OTHER_ABILITIES and defending_pokemon.ability in constants.BYPASSABLE_ABILITIES
    ):
        return attacking_move
    ability_func = ability_lookup.get(ability_name)
    if ability_func is not None:
        return ability_func(attacking_move, attacking_pokemon, defending_pokemon)
    else:
        return attacking_move
