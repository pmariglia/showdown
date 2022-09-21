import re
import json
from copy import deepcopy
import logging

import constants
from data import all_move_json
from data import pokedex
from showdown.battle import Pokemon
from showdown.battle import LastUsedMove
from showdown.battle import DamageDealt
from showdown.battle import StatRange
from showdown.engine.helpers import normalize_name
from showdown.engine.helpers import get_pokemon_info_from_condition
from showdown.engine.helpers import calculate_stats
from showdown.engine.find_state_instructions import get_effective_speed
from showdown.engine.damage_calculator import calculate_damage
from showdown.engine.objects import boost_multiplier_lookup


logger = logging.getLogger(__name__)


MOVE_END_STRINGS = {'move', 'switch', 'upkeep', ''}


def can_have_priority_modified(battle, pokemon, move_name):
    return (
        "prankster" in [normalize_name(a) for a in pokedex[pokemon.name][constants.ABILITIES].values()] or
        move_name == "grassyglide" and battle.field == constants.GRASSY_TERRAIN
    )


def can_have_speed_modified(battle, pokemon):
    return (
        (
            pokemon.item is None and
            "unburden" in [normalize_name(a) for a in pokedex[pokemon.name][constants.ABILITIES].values()]
        ) or
        (
            battle.weather == constants.RAIN and
            pokemon.ability is None and
            "swiftswim" in [normalize_name(a) for a in pokedex[pokemon.name][constants.ABILITIES].values()]
        ) or
        (
            battle.weather == constants.SUN and
            pokemon.ability is None and
            "chlorophyll" in [normalize_name(a) for a in pokedex[pokemon.name][constants.ABILITIES].values()]
        ) or
        (
            battle.weather == constants.SAND and
            pokemon.ability is None and
            "sandrush" in [normalize_name(a) for a in pokedex[pokemon.name][constants.ABILITIES].values()]
        ) or
        (
            battle.weather == constants.HAIL and
            pokemon.ability is None and
            "slushrush" in [normalize_name(a) for a in pokedex[pokemon.name][constants.ABILITIES].values()]
        ) or
        (
            battle.field == constants.ELECTRIC_TERRAIN and
            pokemon.ability is None and
            "surgesurfer" in [normalize_name(a) for a in pokedex[pokemon.name][constants.ABILITIES].values()]
        ) or
        (
            pokemon.status == constants.PARALYZED and
            pokemon.ability is None and
            "quickfeet" in [normalize_name(a) for a in pokedex[pokemon.name][constants.ABILITIES].values()]
        )
    )


def find_pokemon_in_reserves(pkmn_name, reserves):
    for reserve_pkmn in reserves:
        if pkmn_name.startswith(reserve_pkmn.name) or reserve_pkmn.name.startswith(pkmn_name) or reserve_pkmn.base_name == pkmn_name:
            return reserve_pkmn
    return None


def is_opponent(battle,  split_msg):
    return not split_msg[2].startswith(battle.user.name)


def request(battle, split_msg):
    """Update the user's team given the battle JSON in split_msg[2]
       Also updates some battle meta-data such as rqid, force_switch, and wait"""
    if len(split_msg) >= 2:
        battle_json = json.loads(split_msg[2].strip('\''))
        logger.debug("Received battle JSON from server: {}".format(battle_json))
        battle.rqid = battle_json[constants.RQID]

        if battle_json.get(constants.FORCE_SWITCH):
            battle.force_switch = True
        else:
            battle.force_switch = False

        if battle_json.get(constants.WAIT):
            battle.wait = True
        else:
            battle.wait = False

        if not battle.wait:
            battle.request_json = battle_json


def inactive(battle, split_msg):
    regex_string = "(\d+) sec this turn"
    if split_msg[2].startswith(constants.TIME_LEFT):
        capture = re.search(regex_string, split_msg[2])
        try:
            time_left = int(capture.group(1))
            battle.time_remaining = time_left
            logger.debug("Time left: {}".format(time_left))
        except ValueError:
            logger.warning("{} is not a valid int".format(capture.group(1)))
        except AttributeError:
            logger.warning("'{}' does not match the regex '{}'".format(split_msg[2], regex_string))


def inactiveoff(battle, _):
    battle.time_remaining = None


def switch_or_drag(battle, split_msg):
    if is_opponent(battle, split_msg):
        side = battle.opponent
        logger.debug("Opponent has switched - clearing the last used move")
    else:
        side = battle.user
        side.side_conditions[constants.TOXIC_COUNT] = 0

    if side.active is not None:
        # set the pkmn's types back to their original value if the types were changed
        if constants.TYPECHANGE in side.active.volatile_statuses:
            original_types = pokedex[side.active.name][constants.TYPES]
            logger.debug("{} had it's type changed - changing its types back to {}".format(side.active.name, original_types))
            side.active.types = original_types

        # if the target was transformed, reset its transformed attributes
        if constants.TRANSFORM in side.active.volatile_statuses:
            logger.debug("{} was transformed. Resetting its transformed attributes".format(side.active.name))
            side.active.stats = calculate_stats(side.active.base_stats, side.active.level)
            side.active.ability = None
            side.active.moves = []
            side.active.types = pokedex[side.active.name][constants.TYPES]

        # reset the boost of the pokemon being replaced
        side.active.boosts.clear()

        # reset the volatile statuses of the pokemon being replaced
        side.active.volatile_statuses.clear()

        # reset toxic count for this side
        side.side_conditions[constants.TOXIC_COUNT] = 0

        # if the side is alive and has regenerator, give it back 1/3 of it's maxhp
        if side.active.hp > 0 and not side.active.fainted and side.active.ability == "regenerator":
            health_healed = int(side.active.max_hp / 3)
            side.active.hp = min(side.active.hp + health_healed, side.active.max_hp)
            logger.debug(
                "{} switched out with regenerator. Healing it to {}/{}".format(
                    side.active.name, side.active.hp, side.active.max_hp
                )
            )

    # check if the pokemon exists in the reserves
    # if it does not, then the newly-created pokemon is used (for formats without team preview)
    pkmn = Pokemon.from_switch_string(split_msg[3])
    pkmn = find_pokemon_in_reserves(pkmn.name, side.reserve)

    if pkmn is None:
        pkmn = Pokemon.from_switch_string(split_msg[3])
    else:
        side.reserve.remove(pkmn)

    side.last_used_move = LastUsedMove(
        pokemon_name=None,
        move='switch {}'.format(pkmn.name),
        turn=battle.turn
    )

    # pkmn != active is a special edge-case for Zoroark
    if side.active is not None and pkmn != side.active:
        side.reserve.append(side.active)

    side.active = pkmn
    if side.active.name in constants.UNKOWN_POKEMON_FORMES:
        side.active = Pokemon.from_switch_string(split_msg[3])


def heal_or_damage(battle, split_msg):
    if is_opponent(battle, split_msg):
        side = battle.opponent
        other_side = battle.user
        pkmn = battle.opponent.active

        # opponent hp is given as a percentage
        if constants.FNT in split_msg[3]:
            pkmn.hp = 0
        else:
            new_hp_percentage = float(split_msg[3].split('/')[0]) / 100
            pkmn.hp = pkmn.max_hp * new_hp_percentage

    else:
        side = battle.user
        other_side = battle.opponent
        pkmn = battle.user.active
        if constants.FNT in split_msg[3]:
            pkmn.hp = 0
        else:
            pkmn.hp = float(split_msg[3].split('/')[0])
            pkmn.max_hp = float(split_msg[3].split('/')[1].split()[0])

    # increase the amount of turns toxic has been active
    if len(split_msg) == 5 and constants.TOXIC in split_msg[3] and '[from] psn' in split_msg[4]:
        side.side_conditions[constants.TOXIC_COUNT] += 1

    if len(split_msg) == 6 and split_msg[4].startswith('[from] item:') and other_side.name in split_msg[5]:
        item = normalize_name(split_msg[4].split('item:')[-1])
        logger.debug("Setting {}'s item to: {}".format(other_side.active.name, item))
        other_side.active.item = item

    # set the ability for the other side (the side not taking damage, '-damage' only)
    if len(split_msg) == 6 and split_msg[4].startswith('[from] ability:') and other_side.name in split_msg[5] and split_msg[1] == '-damage':
        ability = normalize_name(split_msg[4].split('ability:')[-1])
        logger.debug("Setting {}'s ability to: {}".format(other_side.active.name, ability))
        other_side.active.ability = ability

    # set the ability of the side (the side being healed, '-heal' only)
    if len(split_msg) == 6 and constants.ABILITY in split_msg[4] and other_side.name in split_msg[5] and split_msg[1] == '-heal':
        ability = normalize_name(split_msg[4].split(constants.ABILITY)[-1].strip(": "))
        logger.debug("Setting {}'s ability to: {}".format(pkmn.name, ability))
        pkmn.ability = ability

    # give that pokemon an item if this string specifies one
    if len(split_msg) == 5 and constants.ITEM in split_msg[4] and pkmn.item is not None:
        item = normalize_name(split_msg[4].split(constants.ITEM)[-1].strip(": "))
        logger.debug("Setting {}'s item to: {}".format(pkmn.name, item))
        pkmn.item = item


def faint(battle, split_msg):
    if is_opponent(battle, split_msg):
        side = battle.opponent
    else:
        side = battle.user

    side.active.hp = 0


def move(battle, split_msg):
    if '[from]' in split_msg[-1] and split_msg[-1] != "[from]lockedmove":
        return

    move_name = normalize_name(split_msg[3].strip().lower())

    if is_opponent(battle, split_msg):
        side = battle.opponent
        pkmn = battle.opponent.active
    else:
        side = battle.user
        pkmn = battle.user.active

    # remove volatile status if they have it
    # this is for preparation moves like Phantom Force
    if move_name in pkmn.volatile_statuses:
        logger.debug("Removing volatile status {} from {}".format(move_name, pkmn.name))
        pkmn.volatile_statuses.remove(move_name)

    # add the move to it's moves if it hasn't been seen
    # decrement the PP by one
    # if the move is unknown, do nothing
    move_object = pkmn.get_move(move_name)
    if move_object is None:
        new_move = pkmn.add_move(move_name)
        if new_move is not None:
            new_move.current_pp -= 1
    else:
        move_object.current_pp -= 1
        logger.debug("{} already has the move {}. Decrementing the PP by 1".format(pkmn.name, move_name))

    # if this pokemon used two different moves without switching,
    # set a flag to signify that it cannot have a choice item
    if (
            is_opponent(battle, split_msg) and
            side.last_used_move.pokemon_name == side.active.name and
            side.last_used_move.move != move_name
    ):
        logger.debug("{} used two different moves - it cannot have a choice item".format(pkmn.name))
        pkmn.can_have_choice_item = False
        if pkmn.item in constants.CHOICE_ITEMS:
            logger.warning("{} has a choice item, but used two different moves - setting it's item to UNKNOWN".format(pkmn.name))
            pkmn.item = constants.UNKNOWN_ITEM

    # if the opponent uses a boosting status move, they cannot have a choice item
    # this COULD be set for any status move, but some pkmn uncommonly run things like specs + wisp
    try:
        if constants.BOOSTS in all_move_json[move_name] and all_move_json[move_name][constants.CATEGORY] == constants.STATUS:
            logger.debug("{} used a boosting status-move. Setting can_have_choice_item to False".format(pkmn.name))
            pkmn.can_have_choice_item = False
    except KeyError:
        pass

    try:
        if all_move_json[move_name][constants.CATEGORY] == constants.STATUS:
            logger.debug("{} used a status-move. Setting can_have_assultvest to False".format(pkmn.name))
            pkmn.can_have_assaultvest = False
    except KeyError:
        pass

    try:
        category = all_move_json[move_name][constants.CATEGORY]
        logger.debug("Setting {}'s last used move: {}".format(pkmn.name, move_name))
        side.last_used_move = LastUsedMove(
            pokemon_name=pkmn.name,
            move=move_name,
            turn=battle.turn
        )
    except KeyError:
        category = None
        side.last_used_move = LastUsedMove(
            pokemon_name=pkmn.name,
            move=constants.DO_NOTHING_MOVE,
            turn=battle.turn
        )

    # if this pokemon used a damaging move, eliminate the possibility of it having a lifeorb
    # the lifeorb will reveal itself if it has it
    if category in constants.DAMAGING_CATEGORIES and not any([normalize_name(a) in ['sheerforce', 'magicguard'] for a in pokedex[pkmn.name][constants.ABILITIES].values()]):
        logger.debug("{} used a damaging move - not guessing lifeorb anymore".format(pkmn.name))
        pkmn.can_have_life_orb = False

    # there is nothing special in the protocol for "wish" - it must be extracted here
    if move_name == constants.WISH and 'still' not in split_msg[4]:
        logger.debug("{} used wish - expecting {} health of recovery next turn".format(side.active.name, side.active.max_hp/2))
        side.wish = (2, side.active.max_hp/2)


def boost(battle, split_msg):
    if is_opponent(battle, split_msg):
        pkmn = battle.opponent.active
    else:
        pkmn = battle.user.active

    stat = constants.STAT_ABBREVIATION_LOOKUPS[split_msg[3].strip()]
    amount = int(split_msg[4].strip())

    pkmn.boosts[stat] = min(pkmn.boosts[stat] + amount, constants.MAX_BOOSTS)


def unboost(battle, split_msg):
    if is_opponent(battle, split_msg):
        pkmn = battle.opponent.active
    else:
        pkmn = battle.user.active

    stat = constants.STAT_ABBREVIATION_LOOKUPS[split_msg[3].strip()]
    amount = int(split_msg[4].strip())

    pkmn.boosts[stat] = max(pkmn.boosts[stat] - amount, -1*constants.MAX_BOOSTS)


def status(battle, split_msg):
    if is_opponent(battle, split_msg):
        pkmn = battle.opponent.active
    else:
        pkmn = battle.user.active

    if len(split_msg) > 4 and 'item: ' in split_msg[4]:
        pkmn.item = normalize_name(split_msg[4].split('item:')[-1])

    status_name = split_msg[3].strip()
    logger.debug("{} got status: {}".format(pkmn.name, status_name))
    pkmn.status = status_name


def activate(battle, split_msg):
    if is_opponent(battle, split_msg):
        pkmn = battle.opponent.active
    else:
        pkmn = battle.user.active

    if split_msg[3].lower() == 'move: poltergeist':
        item = normalize_name(split_msg[4])
        logger.debug("{} has the item {}".format(pkmn.name, item))
        pkmn.item = item


def prepare(battle, split_msg):
    if is_opponent(battle, split_msg):
        pkmn = battle.opponent.active
    else:
        pkmn = battle.user.active

    being_prepared = normalize_name(split_msg[3])
    if being_prepared in pkmn.volatile_statuses:
        logger.warning("{} already has the volatile status {}".format(pkmn.name, being_prepared))
    else:
        pkmn.volatile_statuses.append(being_prepared)


def start_volatile_status(battle, split_msg):
    if is_opponent(battle, split_msg):
        pkmn = battle.opponent.active
        side = battle.opponent
    else:
        pkmn = battle.user.active
        side = battle.user

    volatile_status = normalize_name(split_msg[3].split(":")[-1])

    # for some reason futuresight is sent with the `-start` message
    # `-start` is typically reserved for volatile statuses
    if volatile_status == "futuresight":
        side.future_sight = (3, pkmn.name)
        return

    if volatile_status not in pkmn.volatile_statuses:
        logger.debug("Starting the volatile status {} on {}".format(volatile_status, pkmn.name))
        pkmn.volatile_statuses.append(volatile_status)

    if volatile_status == constants.DYNAMAX:
        pkmn.hp *= 2
        pkmn.max_hp *= 2
        logger.debug("{} started dynamax - doubling their HP to {}/{}".format(pkmn.name, pkmn.hp, pkmn.max_hp))

    if constants.ABILITY in split_msg[3]:
        pkmn.ability = volatile_status

    if len(split_msg) == 6 and constants.ABILITY in normalize_name(split_msg[5]):
        pkmn.ability = normalize_name(split_msg[5].split('ability:')[-1])

    if volatile_status == constants.TYPECHANGE:
        if split_msg[4] == "[from] move: Reflect Type":
            pkmn_name = normalize_name(split_msg[5].split(":")[-1])
            new_types = deepcopy(pokedex[pkmn_name][constants.TYPES])
        else:
            new_types = [normalize_name(t) for t in split_msg[4].split("/")]

        logger.debug("Setting {}'s types to {}".format(pkmn.name, new_types))
        pkmn.types = new_types


def end_volatile_status(battle, split_msg):
    if is_opponent(battle, split_msg):
        pkmn = battle.opponent.active
    else:
        pkmn = battle.user.active

    volatile_status = normalize_name(split_msg[3].split(":")[-1])
    if volatile_status not in pkmn.volatile_statuses:
        logger.warning("Pokemon '{}' does not have the volatile status '{}'".format(pkmn.to_dict(), volatile_status))
    else:
        logger.debug("Removing the volatile status {} from {}".format(volatile_status, pkmn.name))
        pkmn.volatile_statuses.remove(volatile_status)
        if volatile_status == constants.DYNAMAX:
            pkmn.hp /= 2
            pkmn.max_hp /= 2
            logger.debug("{} ended dynamax - halving their HP to {}/{}".format(pkmn.name, pkmn.hp, pkmn.max_hp))


def curestatus(battle, split_msg):
    if is_opponent(battle, split_msg):
        side = battle.opponent
    else:
        side = battle.user

    pkmn_name = split_msg[2].split(':')[-1].strip()

    if normalize_name(pkmn_name) == side.active.name:
        pkmn = side.active
    else:
        try:
            pkmn = next(filter(lambda x: x.name == normalize_name(pkmn_name), side.reserve))
        except StopIteration:
            logger.warning(
                "The pokemon {} does not exist in the party, defaulting to the active pokemon".format(normalize_name(pkmn_name))
            )
            pkmn = side.active

    pkmn.status = None


def cureteam(battle, split_msg):
    """Cure every pokemon on the opponent's team of it's status"""
    if is_opponent(battle, split_msg):
        side = battle.opponent
    else:
        side = battle.user

    side.active.status = None
    for pkmn in filter(lambda p: isinstance(p, Pokemon), side.reserve):
        pkmn.status = None


def weather(battle, split_msg):
    if is_opponent(battle, split_msg):
        side = battle.opponent
    else:
        side = battle.user

    weather_name = normalize_name(split_msg[2].split(':')[-1].strip())
    logger.debug("Weather {} started".format(weather_name))
    battle.weather = weather_name

    if len(split_msg) >= 5 and side.name in split_msg[4]:
        ability = normalize_name(split_msg[3].split(':')[-1].strip())
        logger.debug("Setting {} ability to {}".format(side.active.name, ability))
        side.active.ability = ability


def fieldstart(battle, split_msg):
    """Set the battle's field condition"""
    field_name = normalize_name(split_msg[2].split(':')[-1].strip())

    # trick room shows up as a `-fieldstart` item but is separate from the other fields
    if field_name == constants.TRICK_ROOM:
        logger.debug("Setting trickroom")
        battle.trick_room = True
    else:
        logger.debug("Setting the field to {}".format(field_name))
        battle.field = field_name


def fieldend(battle, split_msg):
    """Remove the battle's field condition"""
    field_name = normalize_name(split_msg[2].split(':')[-1].strip())

    # trick room shows up as a `-fieldend` item but is separate from the other fields
    if field_name == constants.TRICK_ROOM:
        logger.debug("Removing trick room")
        battle.trick_room = False
    else:
        logger.debug("Setting the field to None")
        battle.field = None


def sidestart(battle, split_msg):
    """Set a side effect such as stealth rock or sticky web"""
    condition = split_msg[3].split(':')[-1].strip()
    condition = normalize_name(condition)

    if is_opponent(battle, split_msg):
        logger.debug("Side condition {} starting for opponent".format(condition))
        battle.opponent.side_conditions[condition] += 1
    else:
        logger.debug("Side condition {} starting for bot".format(condition))
        battle.user.side_conditions[condition] += 1


def sideend(battle, split_msg):
    """Remove a side effect such as stealth rock or sticky web"""
    condition = split_msg[3].split(':')[-1].strip()
    condition = normalize_name(condition)

    if is_opponent(battle, split_msg):
        logger.debug("Side condition {} ending for opponent".format(condition))
        battle.opponent.side_conditions[condition] = 0
    else:
        logger.debug("Side condition {} ending for bot".format(condition))
        battle.user.side_conditions[condition] = 0


def swapsideconditions(battle, _):
    user_sc = battle.user.side_conditions
    opponent_sc = battle.opponent.side_conditions
    for side_condition in constants.COURT_CHANGE_SWAPS:
        user_sc[side_condition], opponent_sc[side_condition] = opponent_sc[side_condition], user_sc[side_condition]


def set_item(battle, split_msg):
    """Set the opponent's item"""
    if is_opponent(battle, split_msg):
        side = battle.opponent
    else:
        side = battle.user

    item = normalize_name(split_msg[3].strip())
    logger.debug("Setting {}'s item to {}".format(side.active.name, item))
    side.active.item = item


def remove_item(battle, split_msg):
    """Remove the opponent's item"""
    if is_opponent(battle, split_msg):
        side = battle.opponent
    else:
        side = battle.user

    logger.debug("Removing {}'s item".format(side.active.name))
    side.active.item = None


def set_ability(battle, split_msg):
    if is_opponent(battle, split_msg):
        side = battle.opponent
    else:
        side = battle.user

    for msg in split_msg:
        if constants.ABILITY in normalize_name(msg):
            ability = normalize_name(msg.split(':')[-1])
            logger.debug("Setting {}'s ability to {}".format(side.active.name, ability))
            side.active.ability = ability


def set_opponent_ability_from_ability_tag(battle, split_msg):
    if is_opponent(battle, split_msg):
        side = battle.opponent
    else:
        side = battle.user

    ability = normalize_name(split_msg[3])
    logger.debug("Setting {}'s ability to {}".format(side.active.name, ability))
    side.active.ability = ability


def form_change(battle, split_msg):
    if is_opponent(battle, split_msg):
        side = battle.opponent
    else:
        side = battle.user

    base_name = side.active.base_name
    hp_percent = float(side.active.hp) / side.active.max_hp
    previous_moves = side.active.moves
    previous_boosts = side.active.boosts
    previous_status = side.active.status
    previous_item = side.active.item

    new_pokemon = Pokemon.from_switch_string(split_msg[3])
    new_pokemon.moves = previous_moves
    if new_pokemon in side.reserve:
        side.reserve.remove(new_pokemon)

    side.active = new_pokemon
    side.active.hp = hp_percent * side.active.max_hp
    side.active.boosts = previous_boosts
    side.active.status = previous_status
    side.active.item = previous_item

    if side.active.name != "zoroark":
        side.active.base_name = base_name


def zpower(battle, split_msg):
    if is_opponent(battle, split_msg):
        side = battle.opponent
    else:
        side = battle.user

    logger.debug("{} Used a Z-Move, setting item to None".format(side.active.name))
    side.active.item = None


def clearnegativeboost(battle, split_msg):
    if is_opponent(battle, split_msg):
        pkmn = battle.opponent.active
    else:
        pkmn = battle.user.active

    for stat, value in pkmn.boosts.items():
        if value < 0:
            logger.debug("Setting {}'s {} stat to 0".format(pkmn.name, stat))
            pkmn.boosts[stat] = 0


def clearallboost(battle, _):
    pkmn = battle.user.active
    for stat, value in pkmn.boosts.items():
        if value != 0:
            logger.debug("Setting {}'s {} stat to 0".format(pkmn.name, stat))
            pkmn.boosts[stat] = 0

    pkmn = battle.opponent.active
    for stat, value in pkmn.boosts.items():
        if value != 0:
            logger.debug("Setting {}'s {} stat to 0".format(pkmn.name, stat))
            pkmn.boosts[stat] = 0


def singleturn(battle, split_msg):
    if is_opponent(battle, split_msg):
        side = battle.opponent
    else:
        side = battle.user

    move_name = normalize_name(split_msg[3].split(':')[-1])
    if move_name in constants.PROTECT_VOLATILE_STATUSES:
        # set to 2 because the `upkeep` function will decrement by 1 on every end-of-turn
        side.side_conditions[constants.PROTECT] = 2
        logger.debug("{} used protect".format(side.active.name))


def upkeep(battle, _):
    if battle.user.side_conditions[constants.PROTECT] > 0:
        battle.user.side_conditions[constants.PROTECT] -= 1
        logger.debug("Setting protect to {} for the bot".format(battle.user.side_conditions[constants.PROTECT]))

    if battle.opponent.side_conditions[constants.PROTECT] > 0:
        battle.opponent.side_conditions[constants.PROTECT] -= 1
        logger.debug("Setting protect to {} for the opponent".format(battle.opponent.side_conditions[constants.PROTECT]))

    if battle.user.wish[0] > 0:
        battle.user.wish = (battle.user.wish[0] - 1, battle.user.wish[1])
        logger.debug("Decrementing wish to {} for the bot".format(battle.user.wish[0]))

    if battle.opponent.wish[0] > 0:
        battle.opponent.wish = (battle.opponent.wish[0] - 1, battle.opponent.wish[1])
        logger.debug("Decrementing wish to {} for the opponent".format(battle.opponent.wish[0]))

    if battle.user.future_sight[0] > 0:
        battle.user.future_sight = (battle.user.future_sight[0] - 1, battle.user.future_sight[1])
        logger.debug("Decrementing future_sight to {} for the bot".format(battle.user.future_sight[0]))

    if battle.opponent.future_sight[0] > 0:
        battle.opponent.future_sight = (battle.opponent.future_sight[0] - 1, battle.opponent.future_sight[1])
        logger.debug("Decrementing future_sight to {} for the opponent".format(battle.opponent.future_sight[0]))


def mega(battle, split_msg):
    if is_opponent(battle, split_msg):
        side = battle.opponent
    else:
        side = battle.user

    side.active.is_mega = True
    logger.debug("Mega-Pokemon: {}".format(side.active.name))


def transform(battle, split_msg):
    if is_opponent(battle, split_msg):
        transformed_into_name = battle.user.active.name

        battle_copy = deepcopy(battle)
        battle.opponent.active.boosts = deepcopy(battle.user.active.boosts)

        battle_copy.user.from_json(battle_copy.request_json)

        if battle_copy.user.active.name == transformed_into_name or battle_copy.user.active.name.startswith(transformed_into_name):
            transformed_into = battle_copy.user.active
        else:
            transformed_into = find_pokemon_in_reserves(transformed_into_name, battle_copy.user.reserve)

        logger.debug("Opponent {} transformed into {}".format(battle.opponent.active.name, battle.user.active.name))
        battle.opponent.active.stats = deepcopy(transformed_into.stats)
        battle.opponent.active.ability = deepcopy(transformed_into.ability)
        battle.opponent.active.moves = deepcopy(transformed_into.moves)
        battle.opponent.active.types = deepcopy(transformed_into.types)

        if constants.TRANSFORM not in battle.opponent.active.volatile_statuses:
            battle.opponent.active.volatile_statuses.append(constants.TRANSFORM)


def turn(battle, split_msg):
    battle.turn = int(split_msg[2])


def noinit(battle, split_msg):
    if split_msg[2] == "rename":
        battle.battle_tag = split_msg[3]
        logger.debug("Renamed battle to {}".format(battle.battle_tag))


def check_speed_ranges(battle, msg_lines):
    """
    Intention:
        This function is intended to set the min or max possible speed that the opponent's
        active Pokemon could possibly have given a turn that just happened.

        For example: if both the bot and the opponent use an equal priority move but the
        opponent moves first, then the opponent's min_speed attribute will be set to the
        bots actual speed. This is because the opponent must have at least that much speed
        for it to have gone first.

        These min/max speeds are set without knowledge of items. If the opponent goes first
        when having a choice scarf then min speed will still be set to the bots speed. When
        it comes time to guess a Pokemon's possible set(s), the item must be taken into account
        as well when determining the final speed of a Pokemon. Abilities are NOT taken into
        consideration because their speed modifications are subject to certain conditions
        being present, whereas a choice scarf ALWAYS boosts speed.

        If there is a situation where an ability could have modified the turn order (either by
        changing a move's priority or giving a Pokemon more speed) then this check should be
        skipped. Examples are:
            - the opponent COULD have a speed-boosting weather ability AND that weather is up
            - the opponent COULD have prankster and it used a status move
            - Grassy Glide is used when Grassy Terrain is up
    """
    def get_move_information(m):
        try:
            return m.split('|')[2], all_move_json[normalize_name(m.split('|')[3])]
        except KeyError:
            logger.debug("Unknown move {} - using standard 0 priority move".format(normalize_name(m.split('|')[3])))
            return m.split('|')[2], {constants.ID: "unknown", constants.PRIORITY: 0}

    moves = [get_move_information(m) for m in msg_lines if m.startswith('|move|')]
    if len(moves) != 2 or moves[0][1][constants.PRIORITY] != moves[1][1][constants.PRIORITY]:
        return

    bot_went_first = moves[0][0].startswith(battle.user.name)

    if (
        battle.opponent.active is None or
        battle.opponent.active.item == "choicescarf" or
        can_have_speed_modified(battle, battle.opponent.active) or
        (not bot_went_first and can_have_priority_modified(battle, battle.opponent.active, moves[0][1][constants.ID])) or
        (bot_went_first and can_have_priority_modified(battle, battle.user.active, moves[0][1][constants.ID]))
    ):
        return

    battle_copy = deepcopy(battle)
    battle_copy.user.from_json(battle_copy.request_json)

    speed_threshold = int(
        boost_multiplier_lookup[battle_copy.user.active.boosts[constants.SPEED]] *
        battle_copy.user.active.stats[constants.SPEED] /
        boost_multiplier_lookup[battle_copy.opponent.active.boosts[constants.SPEED]]
    )

    if battle.opponent.side_conditions[constants.TAILWIND]:
        speed_threshold = int(speed_threshold / 2)

    if battle.user.side_conditions[constants.TAILWIND]:
        speed_threshold = int(speed_threshold * 2)

    if battle.opponent.active.status == constants.PARALYZED:
        speed_threshold = int(speed_threshold * 2)

    if battle.user.active.status == constants.PARALYZED:
        speed_threshold = int(speed_threshold / 2)

    if battle.user.active.item == "choicescarf":
        speed_threshold = int(speed_threshold * 1.5)

    # we want to swap which attribute gets updated in trickroom because the slower pokemon goes first
    if battle.trick_room:
        bot_went_first = not bot_went_first

    if bot_went_first:
        opponent_max_speed = min(battle.opponent.active.speed_range.max, speed_threshold)
        battle.opponent.active.speed_range = StatRange(
            min=battle.opponent.active.speed_range.min,
            max=opponent_max_speed
        )
        logger.info("Updated {}'s max speed to {}".format(battle.opponent.active.name, battle.opponent.active.speed_range.max))

    else:
        opponent_min_speed = max(battle.opponent.active.speed_range.min, speed_threshold)
        battle.opponent.active.speed_range = StatRange(
            min=opponent_min_speed,
            max=battle.opponent.active.speed_range.max
        )
        logger.info(
            "Updated {}'s min speed to {}".format(battle.opponent.active.name, battle.opponent.active.speed_range.min))


def check_choicescarf(battle, msg_lines):
    def get_move_information(m):
        try:
            return m.split('|')[2], all_move_json[normalize_name(m.split('|')[3])]
        except KeyError:
            logger.debug("Unknown move {} - using standard 0 priority move".format(normalize_name(m.split('|')[3])))
            return m.split('|')[2], {constants.ID: "unknown", constants.PRIORITY: 0}

    moves = [get_move_information(m) for m in msg_lines if m.startswith('|move|')]
    if len(moves) != 2 or moves[0][0].startswith(battle.user.name) or moves[0][1][constants.PRIORITY] != moves[1][1][constants.PRIORITY]:
        return

    if (
        battle.opponent.active is None or
        battle.opponent.active.item != constants.UNKNOWN_ITEM or
        can_have_speed_modified(battle, battle.opponent.active) or
        can_have_priority_modified(battle, battle.opponent.active, moves[0][1][constants.ID])
    ):
        return

    battle_copy = deepcopy(battle)
    battle_copy.user.from_json(battle_copy.request_json)
    if battle.battle_type == constants.RANDOM_BATTLE:
        battle_copy.opponent.active.set_spread('serious', '85,85,85,85,85,85')  # random battles have known spreads
    else:
        if battle.trick_room:
            battle_copy.opponent.active.set_spread('quiet', '0,0,0,0,0,0')  # assume as slow as possible in trickroom
        else:
            battle_copy.opponent.active.set_spread('jolly', '0,0,0,0,0,252')  # assume as fast as possible
    state = battle_copy.create_state()
    opponent_effective_speed = get_effective_speed(state, state.opponent)
    bot_effective_speed = get_effective_speed(state, state.user)

    if battle.trick_room:
        has_scarf = opponent_effective_speed > bot_effective_speed
    else:
        has_scarf = bot_effective_speed > opponent_effective_speed

    if has_scarf:
        logger.debug("Opponent {} could not have gone first - setting it's item to choicescarf".format(battle.opponent.active.name))
        battle.opponent.active.item = 'choicescarf'


def get_damage_dealt(battle, split_msg, next_messages):
    move_name = normalize_name(split_msg[3])
    critical_hit = False

    if is_opponent(battle, split_msg):
        attacking_side = battle.opponent
        defending_side = battle.user
    else:
        attacking_side = battle.user
        defending_side = battle.opponent

    for line in next_messages:
        next_line_split = line.split('|')
        # if one of these strings appears in index 1 then
        # exit out since we are done with this pokemon's move
        if len(next_line_split) < 2 or next_line_split[1] in MOVE_END_STRINGS:
            break

        elif next_line_split[1] == '-crit':
            critical_hit = True

        # if '-damage' appears, we want to parse the percentage damage dealt
        elif next_line_split[1] == '-damage' and defending_side.name in next_line_split[2]:
            final_health, maxhp, _ = get_pokemon_info_from_condition(next_line_split[3])
            # maxhp can be 0 if the targetted pokemon fainted
            # the message would be: "0 fnt"
            if maxhp == 0:
                maxhp = defending_side.active.max_hp

            damage_dealt = (defending_side.active.hp / defending_side.active.max_hp)*maxhp - final_health
            damage_percentage = round(damage_dealt / maxhp, 4)

            logger.debug("{} did {}% damage to {} with {}".format(attacking_side.active.name, damage_percentage * 100, defending_side.active.name, move_name))
            return DamageDealt(attacker=attacking_side.active.name, defender=defending_side.active.name, move=move_name, percent_damage=damage_percentage, crit=critical_hit)


def check_choice_band_or_specs(battle, damage_dealt):
    if (
        battle.opponent.active is None or
        battle.opponent.active.item != constants.UNKNOWN_ITEM or
        damage_dealt.crit or
        damage_dealt.move in constants.WEIGHT_BASED_MOVES or
        damage_dealt.move in constants.SPEED_BASED_MOVES or
        not battle.opponent.active.can_have_choice_item
    ):
        return

    try:
        move_dict = all_move_json[damage_dealt.move]
    except KeyError:
        logger.debug("Could not find the move {}, skipping choice item check".format(move))
        return

    if move_dict[constants.CATEGORY] == constants.PHYSICAL:
        choice_item = 'choiceband'
        spread = 'adamant', '0,252,0,0,0,0'
    elif move_dict[constants.CATEGORY] == constants.SPECIAL:
        choice_item = 'choicespecs'
        spread = 'modest', '0,0,0,252,0,0'
    else:
        # don't guess anything if the move was neither physical nor special
        return

    if battle.battle_type == constants.RANDOM_BATTLE:
        spread = 'serious', '85,85,85,85,85,85'

    min_damage_with_choice_item = float('inf')
    max_damage_without_choice_item = float('-inf')
    potential_battles = battle.prepare_battles(guess_mega_evo_opponent=False, join_moves_together=True)

    battle_copy = deepcopy(battle)
    battle_copy.user.from_json(battle.request_json)
    for b in potential_battles:

        # if the item is not the choice item - use it to find the max damage roll possible for all items
        if b.opponent.active.item != choice_item:
            b.opponent.active.set_spread(*spread)
            b.user.active.stats = battle_copy.user.active.stats

            state = b.create_state()

            damage = calculate_damage(state, constants.OPPONENT, damage_dealt.move, battle.user.last_used_move.move, calc_type='max')[0]
            max_damage_without_choice_item = max(max_damage_without_choice_item, damage)

        # also find the min damage roll possible for the choice-item
        b.opponent.active.item = choice_item
        b.opponent.active.set_spread(*spread)
        b.user.active.stats = battle_copy.user.active.stats

        state = b.create_state()

        damage = calculate_damage(state, constants.OPPONENT, damage_dealt.move, battle.user.last_used_move.move, calc_type='min')[0]
        min_damage_with_choice_item = min(min_damage_with_choice_item, damage)

    # dont infer if we did not find a damage amount
    if max_damage_without_choice_item == float('-inf') or min_damage_with_choice_item == float('inf'):
        return

    actual_damage_dealt = damage_dealt.percent_damage * battle.user.active.max_hp

    # if the damage dealt is more than 1.2x the max-roll WITHOUT a choice item then the pkmn DOES have a choice-item
    if actual_damage_dealt > (max_damage_without_choice_item * 1.2):  # multiply to avoid rounding errors
        logger.debug("{} has {}".format(battle.opponent.active.name, choice_item))
        battle.opponent.active.item = choice_item

    # if the damage dealt is less than 0.8x the min-roll given a choice-item then the pkmn DOES NOT have a choice-item
    if (
        actual_damage_dealt < (min_damage_with_choice_item * 0.8) and  # multiply to avoid rounding errors
        (battle.user.active.hp - actual_damage_dealt) > 1  # this is checking if the move KO-ed
                                                           # if it did, we do not want to set this flag
                                                           # Check for greater than 1 to avoid rounding errors
    ):
        logger.debug("{} did not do enough damage to have {}".format(battle.opponent.active.name, choice_item))
        if choice_item == "choiceband":
            battle.opponent.active.can_not_have_band = True
        elif choice_item == "choicespecs":
            battle.opponent.active.can_not_have_specs = True
        else:
            raise ValueError("{} is neither 'choiceband' or 'choicespecs'")


def check_heavydutyboots(battle, msg_lines):
    side_to_check = battle.opponent

    if (
        side_to_check.active.item != constants.UNKNOWN_ITEM or
        'magicguard' in [normalize_name(a) for a in pokedex[side_to_check.active.name][constants.ABILITIES].values()]
    ):
        return

    if side_to_check.side_conditions[constants.STEALTH_ROCK] > 0:
        pkmn_took_stealthrock_damage = False
        for line in msg_lines:
            split_line = line.split('|')

            # |-damage|p2a: Weedle|88/100|[from] Stealth Rock
            if (
                len(split_line) > 4 and
                split_line[1] == '-damage' and
                split_line[2].startswith(side_to_check.name) and
                split_line[4] == '[from] Stealth Rock'
            ):
                pkmn_took_stealthrock_damage = True

        if not pkmn_took_stealthrock_damage:
            logger.debug("{} has heavydutyboots".format(side_to_check.active.name))
            side_to_check.active.item = 'heavydutyboots'
        else:
            logger.debug("{} was affected by stealthrock, it cannot have heavydutyboots".format(side_to_check.active.name))
            side_to_check.active.can_have_heavydutyboots = False

    elif (
        side_to_check.side_conditions[constants.SPIKES] > 0 and
        'flying' not in side_to_check.active.types and
        side_to_check.active.ability != 'levitate'
    ):
        pkmn_took_spikes_damage = False
        for line in msg_lines:
            split_line = line.split('|')

            # |-damage|p2a: Weedle|88/100|[from] Spikes
            if (
                    len(split_line) > 4 and
                    split_line[1] == '-damage' and
                    split_line[2].startswith(side_to_check.name) and
                    split_line[4] == '[from] Spikes'
            ):
                pkmn_took_spikes_damage = True

        if not pkmn_took_spikes_damage:
            logger.debug("{} has heavydutyboots".format(side_to_check.active.name))
            side_to_check.active.item = 'heavydutyboots'
        else:
            logger.debug("{} was affected by spikes, it cannot have heavydutyboots".format(side_to_check.active.name))
            side_to_check.active.can_have_heavydutyboots = False
    elif (
        side_to_check.side_conditions[constants.TOXIC_SPIKES] > 0 and
        'flying' not in side_to_check.active.types and
        'poison' not in side_to_check.active.types and
        'steel' not in side_to_check.active.types and
        side_to_check.active.ability != 'levitate' and
        side_to_check.active.ability not in constants.IMMUNE_TO_POISON_ABILITIES
    ):
        pkmn_took_toxicspikes_poison = False
        for line in msg_lines:
            split_line = line.split('|')

            # a pokemon can be toxic-ed from sources other than toxicspikes
            # stopping at one of these strings ensures those other sources aren't considered
            if len(split_line) < 2 or split_line[1] in MOVE_END_STRINGS:
                break

            # |-status|p2a: Pikachu|psn
            if (
                    split_line[1] == '-status' and
                    (split_line[3] == constants.POISON or split_line[3] == constants.TOXIC) and
                    split_line[2].startswith(side_to_check.name)
            ):
                pkmn_took_toxicspikes_poison = True

        if not pkmn_took_toxicspikes_poison:
            logger.debug("{} has heavydutyboots".format(side_to_check.active.name))
            side_to_check.active.item = 'heavydutyboots'
        else:
            logger.debug("{} was affected by toxicspikes, it cannot have heavydutyboots".format(side_to_check.active.name))
            side_to_check.active.can_have_heavydutyboots = False

    elif (
            side_to_check.side_conditions[constants.STICKY_WEB] > 0 and
            'flying' not in side_to_check.active.types and
            side_to_check.active.ability != 'levitate'
    ):
        pkmn_was_affected_by_stickyweb = False
        for line in msg_lines:
            split_line = line.split('|')

            # |-activate|p2a: Gengar|move: Sticky Web
            if (
                    len(split_line) == 4 and
                    split_line[1] == '-activate' and
                    split_line[2].startswith(side_to_check.name) and
                    split_line[3] == 'move: Sticky Web'
            ):
                pkmn_was_affected_by_stickyweb = True

        if not pkmn_was_affected_by_stickyweb:
            logger.debug("{} has heavydutyboots".format(side_to_check.active.name))
            side_to_check.active.item = 'heavydutyboots'
        else:
            logger.debug("{} was affected by sticky web, it cannot have heavydutyboots".format(side_to_check.active.name))
            side_to_check.active.can_have_heavydutyboots = False


def update_battle(battle, msg):
    msg_lines = msg.split('\n')

    action = None
    check_speed_ranges(battle, msg_lines)
    for i, line in enumerate(msg_lines):
        split_msg = line.split('|')
        if len(split_msg) < 2:
            continue

        action = split_msg[1].strip()

        battle_modifiers_lookup = {
            'request': request,
            'switch': switch_or_drag,
            'faint': faint,
            'drag': switch_or_drag,
            '-heal': heal_or_damage,
            '-damage': heal_or_damage,
            'move': move,
            '-boost': boost,
            '-unboost': unboost,
            '-status': status,
            '-activate': activate,
            '-prepare': prepare,
            '-start': start_volatile_status,
            '-end': end_volatile_status,
            '-curestatus': curestatus,
            '-cureteam': cureteam,
            '-weather': weather,
            '-fieldstart': fieldstart,
            '-fieldend': fieldend,
            '-sidestart': sidestart,
            '-sideend': sideend,
            '-swapsideconditions': swapsideconditions,
            '-item': set_item,
            '-enditem': remove_item,
            '-immune': set_ability,
            '-ability': set_opponent_ability_from_ability_tag,
            'detailschange': form_change,
            'replace': form_change,
            '-formechange': form_change,
            '-transform': transform,
            '-mega': mega,
            '-zpower': zpower,
            '-clearnegativeboost': clearnegativeboost,
            '-clearallboost': clearallboost,
            '-singleturn': singleturn,
            'upkeep': upkeep,
            'inactive': inactive,
            'inactiveoff': inactiveoff,
            'turn': turn,
            'noinit': noinit,
        }

        function_to_call = battle_modifiers_lookup.get(action)
        if function_to_call is not None:
            function_to_call(battle, split_msg)

        if action == 'move' and is_opponent(battle, split_msg):
            check_choicescarf(battle, msg_lines)
            damage_dealt = get_damage_dealt(battle, split_msg, msg_lines[i + 1:])
            if damage_dealt:
                check_choice_band_or_specs(battle, damage_dealt)

        elif action == 'switch' and is_opponent(battle, split_msg):
            check_heavydutyboots(battle, msg_lines[i+1:])

        if action == 'turn':
            return True

    if action in ['inactive', 'updatesearch']:
        return False

    if action != "request":
        return battle.force_switch


async def async_update_battle(battle, msg):
    return update_battle(battle, msg)
