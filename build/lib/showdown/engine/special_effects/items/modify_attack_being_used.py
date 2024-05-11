import constants

from ...damage_calculator import is_super_effective


def choiceband(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def choicespecs(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.CATEGORY] == constants.SPECIAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.5
    return attacking_move


def lifeorb(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.CATEGORY] in constants.DAMAGING_CATEGORIES:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.3
        attacking_move[constants.HEAL] = [-1, 10]
        attacking_move[constants.HEAL_TARGET] = constants.SELF
    return attacking_move


def expertbelt(attacking_move, attacking_pokemon, defending_pokemon):
    if is_super_effective(attacking_move[constants.TYPE], defending_pokemon.types):
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def blackglasses(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'dark':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def magnet(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'electric':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def spelltag(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'ghost':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def thickclub(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_pokemon.id in ['cubone', 'marowak', 'marowakalola'] and attacking_move[constants.CATEGORY] == constants.PHYSICAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 2
    return attacking_move


def whiteherb(attacking_move, attacking_pokemon, defending_pokemon):
    if constants.BOOSTS in attacking_move and attacking_move[constants.TARGET] in constants.MOVE_TARGET_SELF:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BOOSTS] = attacking_move[constants.BOOSTS].copy()
        for k in attacking_move[constants.BOOSTS].copy():
            if attacking_move[constants.BOOSTS][k] < 0:
                del attacking_move[constants.BOOSTS][k]
    return attacking_move


def wiseglasses(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.CATEGORY] == constants.SPECIAL:
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.1
    return attacking_move


def blackbelt(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'dark':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def charcoal(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'fire':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def dragonfang(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'dragon':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def hardstone(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'rock':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def metalcoat(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'steel':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def miracleseed(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'grass':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def mysticwater(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'water':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def nevermeltice(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'ice':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def poisonbarb(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'poison':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def sharpbeak(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'flying':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def silkscarf(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'normal':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def silverpowder(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'bug':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def softsand(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'ground':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def twistedspoon(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_move[constants.TYPE] == 'psychic':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def souldew(attacking_move, attacking_pokemon, defending_pokemon):
    if (
        (attacking_pokemon.id == 'latios' or attacking_pokemon.id == 'latias') and
        (attacking_move[constants.TYPE] == 'psychic' or attacking_move[constants.TYPE] == 'dragon')
    ):
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def adamantorb(attacking_move, attacking_pokemon, defending_pokemon):
    if (
        attacking_pokemon.id == 'dialga' and
        (attacking_move[constants.TYPE] == 'dragon' or attacking_move[constants.TYPE] == 'steel')
    ):
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def lustrousorb(attacking_move, attacking_pokemon, defending_pokemon):
    if (
        attacking_pokemon.id == 'palkia' and
        (attacking_move[constants.TYPE] == 'dragon' or attacking_move[constants.TYPE] == 'water')
    ):
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def griseousorb(attacking_move, attacking_pokemon, defending_pokemon):
    if (
        (attacking_pokemon.id == 'giratina' or attacking_pokemon.id == 'giratinaorigin') and
        (attacking_move[constants.TYPE] == 'dragon' or attacking_move[constants.TYPE] == 'ghost')
    ):
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 1.2
    return attacking_move


def lightball(attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_pokemon.id == 'pikachu':
        attacking_move = attacking_move.copy()
        attacking_move[constants.BASE_POWER] *= 2
    return attacking_move


def item_modify_attack_being_used(item_name, attacking_move, attacking_pokemon, defending_pokemon):
    try:
        return globals()[item_name](attacking_move, attacking_pokemon, defending_pokemon)
    except KeyError:
        return attacking_move
