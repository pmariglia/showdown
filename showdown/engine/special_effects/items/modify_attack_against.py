import constants

from ...damage_calculator import is_super_effective


def eviolite(attacking_move, attacking_pokemon, defending_pokemon):
    attacking_move = attacking_move.copy()
    attacking_move[constants.BASE_POWER] /= 1.5
    return attacking_move


def rockyhelmet(attacking_move, attacking_pokemon, defending_pokemon):
    if constants.CONTACT in attacking_move[constants.FLAGS]:
        attacking_move = attacking_move.copy()
        attacking_move[constants.HEAL] = [-1, 6]
        attacking_move[constants.HEAL_TARGET] = constants.SELF
    return attacking_move


def assaultvest(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.CATEGORY] == constants.SPECIAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] /= 1.5
    return attacking_move


def airballoon(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'ground' and attacking_move[constants.ID] != 'thousandarrows':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] = 0
    return attacking_move


def weaknesspolicy(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.CATEGORY] in constants.DAMAGING_CATEGORIES and is_super_effective(attacking_move[constants.TYPE], defending_pokemon.types):
        attacking_move = attacking_move.copy()
        attacking_move[constants.BOOSTS] = {
            constants.ATTACK: 2,
            constants.SPECIAL_ATTACK: 2,
        }
    return attacking_move


item_lookup = {
    'weaknesspolicy': weaknesspolicy,
    'eviolite': eviolite,
    'rockyhelmet': rockyhelmet,
    'assaultvest': assaultvest,
    'airballoon': airballoon
}


def item_modify_attack_against(item_name, attacking_move, attacking_pokemon, defending_pokemon):
    item_func = item_lookup.get(item_name)
    if item_func is not None:
        return item_func(attacking_move, attacking_pokemon, defending_pokemon)
    else:
        return attacking_move
