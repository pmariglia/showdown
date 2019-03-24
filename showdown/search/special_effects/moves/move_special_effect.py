import constants


def suckerpunch(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move):
    if not first_move or defending_move.get(constants.CATEGORY) not in constants.DAMAGING_CATEGORIES:
        attacking_move = attacking_move.copy()
        attacking_move[constants.ACCURACY] = 0

    return attacking_move


def eruption(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move):
    attacking_move = attacking_move.copy()
    attacker_hp_percent = attacking_pokemon.hp / attacking_pokemon.maxhp
    attacking_move[constants.BASE_POWER] *= attacker_hp_percent
    return attacking_move


def tailslap(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move):
    # skill-link will boost damage by 5x, so no need to do it again here if that is the pokemon's ability
    if attacking_pokemon.ability != 'skilllink':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 3.2
    return attacking_move


def freezedry(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move):
    if 'water' in defending_pokemon.types:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 4
    return attacking_move


def hex(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move):
    if defending_pokemon.status is not None:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 2
    return attacking_move


def foulplay(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move):
    attacking_move = attacking_move.copy()
    attacking_move[constants.BASE_POWER] *= defending_pokemon.attack / attacking_pokemon.attack
    return attacking_move


def storedpower(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move):
    multiplier = attacking_pokemon.attack_boost + attacking_pokemon.defense_boost + \
                 attacking_pokemon.special_attack_boost + attacking_pokemon.special_defense_boost + \
                 attacking_pokemon.speed_boost
    if multiplier > 0:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= multiplier
    return attacking_move


def psyshock(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move):
    attacking_move = attacking_move.copy()
    attacking_move[constants.BASE_POWER] *= (defending_pokemon.defense / defending_pokemon.special_defense)
    return attacking_move


def facade(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move):
    if attacking_pokemon.status is not None:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 2
    return attacking_move


def avalanche(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move):
    if first_move is False and defending_move.get(constants.CATEGORY) in constants.DAMAGING_CATEGORIES:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 2
    return attacking_move


def gyroball(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move):
    # power = 25 × TargetSpeed ÷ UserSpeed
    attacking_move = attacking_move.copy()
    attacker_speed = attacking_pokemon.calculate_boosted_stats()[constants.SPEED]
    defender_speed = defending_pokemon.calculate_boosted_stats()[constants.SPEED]
    attacking_move[constants.BASE_POWER] = min(150, 25 * defender_speed / attacker_speed)
    return attacking_move


move_lookup = {
    'suckerpunch': suckerpunch,
    'eruption': eruption,
    'waterspout': eruption,
    'hex': hex,
    'freezedry': freezedry,
    'tailslap': tailslap,
    'bulletseed': tailslap,
    'rockblast': tailslap,
    'bonerush': tailslap,
    'iciclespear': tailslap,
    'pinmissile': tailslap,
    'foulplay': foulplay,
    'storedpower': storedpower,
    'psyshock': psyshock,
    'psystrike': psyshock,
    'secretsword': psyshock,
    'avalanche': avalanche,
    'facade': facade,
    'gyroball': gyroball
}


def modify_attack_being_used(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move):
    move_func = move_lookup.get(attacking_move[constants.ID])
    if move_func is not None:
        return move_func(attacking_move, defending_move, attacking_pokemon, defending_pokemon, first_move)
    else:
        return attacking_move
