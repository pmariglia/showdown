import constants

from showdown.calculate_damage import is_super_effective


def levitate(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'ground' and attacking_move[constants.TARGET] in constants.MOVE_TARGET_OPPONENT:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = 0
        return attacking_move
    else:
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


def immunity(attacking_move, attacking_pokemon, defending_pokemon):
    poison_strings = [constants.POISON, constants.TOXIC]
    if attacking_move.get(constants.STATUS) in poison_strings:
        attacking_move = attacking_move.copy()
        attacking_move[constants.STATUS] = None
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


ability_lookup = {
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
    'fluffy': fluffy,
    'immunity': immunity,
    'ironbarbs': ironbarbs,
    'wonderguard': wonderguard,
    'roughskin': roughskin,
    'magicbounce': magicbounce
}


def ability_modify_attack_against(ability_name, attacking_move, attacking_pokemon, defending_pokemon):
    ability_func = ability_lookup.get(ability_name)
    if ability_func is not None:
        return ability_func(attacking_move, attacking_pokemon, defending_pokemon)
    else:
        return attacking_move
