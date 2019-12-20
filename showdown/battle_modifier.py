import re
import json
from copy import deepcopy

import constants
from config import logger
from data import all_move_json
from data import pokedex
from showdown.battle import Pokemon
from showdown.battle import LastUsedMove
from showdown.helpers import normalize_name
from showdown.engine.find_state_instructions import get_effective_speed


def find_pokemon_in_reserves(pkmn_name, reserves):
    for reserve_pkmn in reserves:
        if pkmn_name.startswith(reserve_pkmn.name) or reserve_pkmn.base_name == pkmn_name:
            return reserve_pkmn
    return None


def is_opponent(battle,  split_msg):
    return not split_msg[2].startswith(battle.user.name)


def request(battle, split_msg):
    """Update the user's team given the battle JSON in split_msg[2]
       Also updates some battle meta-data such as rqid, force_switch, and wait"""
    if len(split_msg) >= 2:
        battle_json = json.loads(split_msg[2].strip('\''))
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
            battle.user.from_json(battle_json)


def inactive(battle, split_msg):
    regex_string = "(\d+) sec this turn"
    if split_msg[2].startswith(constants.TIME_LEFT):
        capture = re.search(regex_string, split_msg[2])
        try:
            battle.time_remaining = int(capture.group(1))
        except ValueError:
            logger.warning("{} is not a valid int".format(capture.group(1)))
        except AttributeError:
            logger.warning("'{}' does not match the regex '{}'".format(split_msg[2], regex_string))


def switch_or_drag(battle, split_msg):
    """The opponent's pokemon has changed
       If the new one hasn't been seen, create it"""
    if is_opponent(battle, split_msg):
        logger.debug("Opponent has switched - clearing the last used move")
        battle.opponent.last_used_move = LastUsedMove(
            pokemon_name=None,
            move='switch'
        )

        battle.opponent.side_conditions[constants.TOXIC_COUNT] = 0

        if battle.opponent.active is not None:
            # reset the boost of the pokemon being replaced
            battle.opponent.active.boosts.clear()

            if constants.DYNAMAX in battle.opponent.active.volatile_statuses:
                battle.opponent.active.hp /= 2
                battle.opponent.active.max_hp /= 2
                logger.debug("Opponent ended dynamax - halving their HP to {}/{}".format(battle.opponent.active.hp, battle.opponent.active.max_hp))

            # reset the volatile statuses of the pokemon being replaced
            battle.opponent.active.volatile_statuses.clear()

        # check if the pokemon exists in the reserves
        # if it does not, then the newly-created pokemon is used (for formats without team preview)
        pkmn = Pokemon.from_switch_string(split_msg[3])
        pkmn = find_pokemon_in_reserves(pkmn.name, battle.opponent.reserve)

        if pkmn is None:
            pkmn = Pokemon.from_switch_string(split_msg[3])
        else:
            battle.opponent.reserve.remove(pkmn)

        # pkmn != active is a special edge-case for Zoroark
        if battle.opponent.active is not None and pkmn != battle.opponent.active:
            battle.opponent.reserve.append(battle.opponent.active)

        battle.opponent.active = pkmn
        if battle.opponent.active.name in constants.UNKOWN_POKEMON_FORMES:
            battle.opponent.active = Pokemon.from_switch_string(split_msg[3])

    else:
        battle.user.side_conditions[constants.TOXIC_COUNT] = 0
        battle.user.active.boosts.clear()


def heal_or_damage(battle, split_msg):
    if is_opponent(battle, split_msg):
        pkmn = battle.opponent.active

        # opponent hp is given as a percentage
        if constants.FNT in split_msg[3]:
            pkmn.hp = 0
        else:
            new_hp_percentage = float(split_msg[3].split('/')[0]) / 100
            pkmn.hp = pkmn.max_hp * new_hp_percentage

            if len(split_msg) == 5 and constants.TOXIC in split_msg[3] and '[from] psn' in split_msg[4]:
                battle.opponent.side_conditions[constants.TOXIC_COUNT] += 1

        # give that pokemon an item if this string specifies one
        if len(split_msg) == 5 and constants.ITEM in split_msg[4] and pkmn.item is not None:
            item = normalize_name(split_msg[4].split(constants.ITEM)[-1].strip(": "))
            logger.debug("Setting opponent's item to: {}".format(item))
            pkmn.item = item

        # set the ability if the information is shown
        if len(split_msg) >= 5 and constants.ABILITY in split_msg[4]:
            ability = normalize_name(split_msg[4].split(constants.ABILITY)[-1].strip(": "))
            logger.debug("Setting opponent's ability to: {}".format(ability))
            pkmn.ability = ability

    else:
        if len(split_msg) == 5 and constants.TOXIC in split_msg[3] and '[from] psn' in split_msg[4]:
            battle.user.side_conditions[constants.TOXIC_COUNT] += 1
        elif len(split_msg) == 6 and split_msg[4].startswith('[from] ability:') and battle.opponent.name in split_msg[5]:
            ability = normalize_name(split_msg[4].split('ability:')[-1])
            logger.debug("Setting opponent's ability to: {}".format(ability))
            battle.opponent.active.ability = ability
        elif len(split_msg) == 6 and split_msg[4].startswith('[from] item:') and battle.opponent.name in split_msg[5]:
            item = normalize_name(split_msg[4].split('item:')[-1])
            logger.debug("Setting opponent's item to: {}".format(item))
            battle.opponent.active.item = item


def faint(battle, split_msg):
    if is_opponent(battle, split_msg):
        battle.opponent.active.hp = 0


def move(battle, split_msg):
    """The opponent's pokemon has made a move - add it to that pokemon's move list if necessary"""
    move_name = normalize_name(split_msg[3].strip().lower())
    if is_opponent(battle, split_msg):
        pkmn = battle.opponent.active
        move = pkmn.get_move(move_name)
        if move is None:
            new_move = pkmn.add_move(move_name)
            if new_move is not None:
                new_move.current_pp -= 1
        else:
            move.current_pp -= 1
            logger.debug("{} already has the move {}. Decrementing the PP by 1".format(pkmn.name, move_name))

        logger.debug("Setting opponent's last used move: {} - {}".format(battle.opponent.active.name, move_name))

        # if this pokemon used two different moves without switching,
        # set a flag to signify that it cannot have a choice item
        if (
            battle.opponent.last_used_move.pokemon_name == battle.opponent.active.name and
            battle.opponent.last_used_move.move != move_name
        ):
            logger.debug("Opponent's {} used two different moves - it cannot have a choice item".format(battle.opponent.active.name))
            battle.opponent.active.can_have_choice_item = False

        try:
            category = all_move_json[move_name][constants.CATEGORY]
        except KeyError:
            category = None

        # if this pokemon used a damaging move, eliminate the possibility of it having a lifeorb
        # the lifeorb will reveal itself if they have it
        if category in constants.DAMAGING_CATEGORIES and not any([normalize_name(a) in ['sheerforce', 'magicguard'] for a in pokedex[pkmn.name][constants.ABILITIES].values()]):
            logger.debug("Opponent's {} used a damaging move - not guessing lifeorb anymore".format(battle.opponent.active.name))
            pkmn.can_have_life_orb = False

        battle.opponent.last_used_move = LastUsedMove(
            pokemon_name=battle.opponent.active.name,
            move=move_name
        )


def boost(battle, split_msg):
    """Either pokemon has had their boosts increased"""

    if is_opponent(battle, split_msg):
        pkmn = battle.opponent.active
    else:
        pkmn = battle.user.active

    stat = constants.STAT_ABBREVIATION_LOOKUPS[split_msg[3].strip()]
    amount = int(split_msg[4].strip())

    pkmn.boosts[stat] = min(pkmn.boosts[stat] + amount, constants.MAX_BOOSTS)


def unboost(battle, split_msg):
    """Either pokemon has had their boosts lowered"""
    if is_opponent(battle, split_msg):
        pkmn = battle.opponent.active
    else:
        pkmn = battle.user.active

    stat = constants.STAT_ABBREVIATION_LOOKUPS[split_msg[3].strip()]
    amount = int(split_msg[4].strip())

    pkmn.boosts[stat] = max(pkmn.boosts[stat] - amount, -1*constants.MAX_BOOSTS)


def status(battle, split_msg):
    if is_opponent(battle, split_msg):
        status_name = split_msg[3].strip()
        logger.debug("Opponent got status {}".format(status_name))
        battle.opponent.active.status = status_name

        if len(split_msg) > 4 and 'item: ' in split_msg[4]:
            battle.opponent.active.item = normalize_name(split_msg[4].split('item:')[-1])


def start_volatile_status(battle, split_msg):
    if is_opponent(battle, split_msg):
        pkmn = battle.opponent.active
    else:
        pkmn = battle.user.active

    volatile_status = normalize_name(split_msg[3].split(":")[-1])
    if volatile_status not in pkmn.volatile_statuses:
        logger.debug("Starting the volatile status {} on {}".format(volatile_status, pkmn.name))
        pkmn.volatile_statuses.append(volatile_status)

    if is_opponent(battle, split_msg) and volatile_status == constants.DYNAMAX:
        pkmn.hp *= 2
        pkmn.max_hp *= 2
        logger.debug("Opponent started dynamax - doubling their HP to {}/{}".format(pkmn.hp, pkmn.max_hp))

    if is_opponent(battle, split_msg) and constants.ABILITY in split_msg[3]:
        pkmn.ability = volatile_status


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
        if is_opponent(battle, split_msg) and volatile_status == constants.DYNAMAX:
            pkmn.hp /= 2
            pkmn.max_hp /= 2
            logger.debug("Opponent ended dynamax - halving their HP to {}/{}".format(pkmn.hp, pkmn.max_hp))


def curestatus(battle, split_msg):
    if is_opponent(battle, split_msg):
        pkmn_name = split_msg[2].split(':')[-1].strip()

        if normalize_name(pkmn_name) == battle.opponent.active.name:
            pkmn = battle.opponent.active
        else:
            try:
                pkmn = next(filter(lambda x: x.name == normalize_name(pkmn_name), battle.opponent.reserve))
            except StopIteration:
                logger.warning(
                    "The pokemon {} does not exist in the opponent's party, defaulting to the active pokemon".format(
                        normalize_name(pkmn_name)))
                pkmn = battle.opponent.active

        pkmn.status = None


def cureteam(battle, split_msg):
    """Cure every pokemon on the opponent's team of it's status"""
    if is_opponent(battle, split_msg):
        battle.opponent.active.status = None
        for pkmn in filter(lambda p: isinstance(p, Pokemon), battle.opponent.reserve):
                pkmn.status = None


def weather(battle, split_msg):
    """Set the battle's weather"""
    weather_name = normalize_name(split_msg[2].split(':')[-1].strip())
    logger.debug("Weather {} started".format(weather_name))
    battle.weather = weather_name

    if len(split_msg) >= 5 and battle.opponent.name in split_msg[4]:
        ability = normalize_name(split_msg[3].split(':')[-1].strip())
        logger.debug("Setting opponent ability to {}".format(ability))
        battle.opponent.active.ability = ability


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


def set_item(battle, split_msg):
    """Set the opponent's item"""
    if is_opponent(battle, split_msg):
        item = normalize_name(split_msg[3].strip())
        logger.debug("Setting opponent's item to {}".format(item))
        battle.opponent.active.item = item


def remove_item(battle, split_msg):
    """Remove the opponent's item"""
    if is_opponent(battle, split_msg):
        logger.debug("Removing opponent's item")
        battle.opponent.active.item = None


def set_opponent_ability(battle, split_msg):
    if is_opponent(battle, split_msg):
        for msg in split_msg:
            if constants.ABILITY in normalize_name(msg):
                ability = normalize_name(msg.split(':')[-1])
                logger.debug("Setting opponent ability to {}".format(ability))
                battle.opponent.active.ability = ability


def set_opponent_ability_from_ability_tag(battle, split_msg):
    if is_opponent(battle, split_msg):
        ability = normalize_name(split_msg[3])
        logger.debug("Setting opponent ability to {}".format(ability))
        battle.opponent.active.ability = ability


def form_change(battle, split_msg):
    if is_opponent(battle, split_msg):
        base_name = battle.opponent.active.base_name
        hp_percent = float(battle.opponent.active.hp) / battle.opponent.active.max_hp
        moves = battle.opponent.active.moves
        boosts = battle.opponent.active.boosts
        status = battle.opponent.active.status

        new_pokemon = Pokemon.from_switch_string(split_msg[3])
        new_pokemon.moves = moves
        if new_pokemon in battle.opponent.reserve:
            battle.opponent.reserve.remove(new_pokemon)

        battle.opponent.active = new_pokemon
        battle.opponent.active.hp = hp_percent * battle.opponent.active.max_hp
        battle.opponent.active.boosts = boosts
        battle.opponent.active.status = status

        if battle.opponent.active.name != "zoroark":
            battle.opponent.active.base_name = base_name


def zpower(battle, split_msg):
    if is_opponent(battle, split_msg):
        logger.debug("{} Used a Z-Move, setting item to None".format(battle.opponent.active.name))
        battle.opponent.active.item = None


def clearnegativeboost(battle, split_msg):
    if is_opponent(battle, split_msg):
        pkmn = battle.opponent.active
    else:
        pkmn = battle.user.active

    for stat, value in pkmn.boosts.items():
        if value < 0:
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


def mega(battle, split_msg):
    if is_opponent(battle, split_msg):
        battle.opponent.active.is_mega = True
        logger.debug("Opponent Mega-Pokemon: {}".format(battle.opponent.active.name))


def check_choicescarf(battle, msg_lines):
    def get_move_information(m):
        try:
            return m.split('|')[2], all_move_json[normalize_name(m.split('|')[3])]
        except KeyError:
            logger.debug("Unknown move {} - using standard 0 priority move".format(normalize_name(m.split('|')[3])))
            return m.split('|')[2], {constants.PRIORITY: 0}

    if (
        battle.opponent.active is None or
        battle.opponent.active.item != constants.UNKNOWN_ITEM or
        'prankster' in [normalize_name(a) for a in pokedex[battle.opponent.active.name][constants.ABILITIES].values()]
    ):
        return

    moves = [get_move_information(m) for m in msg_lines if m.startswith('|move|')]
    if len(moves) != 2 or moves[0][0].startswith(battle.user.name)or moves[0][1][constants.PRIORITY] != moves[1][1][constants.PRIORITY]:
        return

    battle_copy = deepcopy(battle)
    if battle.battle_type == constants.RANDOM_BATTLE:
        battle_copy.opponent.active.set_spread('serious', '85,85,85,85,85,85')  # random battles have known spreads
    else:
        if battle.trick_room:
            battle_copy.opponent.active.set_spread('quiet', '0,0,0,0,0,0')  # assume as slow as possible in trickroom
        else:
            battle_copy.opponent.active.set_spread('jolly', '0,0,0,0,0,252')  # assume as fast as possible
    state = battle_copy.create_state()
    opponent_effective_speed = get_effective_speed(state, state.opponent)
    bot_effective_speed = get_effective_speed(state, state.self)

    if battle.trick_room:
        has_scarf = opponent_effective_speed > bot_effective_speed
    else:
        has_scarf = bot_effective_speed > opponent_effective_speed

    if has_scarf:
        logger.debug("Opponent {} could not have gone first - setting it's item to choicescarf".format(battle.opponent.active.name))
        battle.opponent.active.item = 'choicescarf'


async def update_battle(battle, msg):
    msg_lines = msg.split('\n')

    check_choicescarf(battle, msg_lines)

    action = None
    for line in msg_lines:
        split_msg = line.split('|')
        if len(split_msg) < 2:
            continue

        action = split_msg[1].strip()

        battle_modifiers_lookup = {
            'request': request,
            'inactive': inactive,
            'switch': switch_or_drag,
            'faint': faint,
            'drag': switch_or_drag,
            '-heal': heal_or_damage,
            '-damage': heal_or_damage,
            'move': move,
            '-boost': boost,
            '-unboost': unboost,
            '-status': status,
            '-start': start_volatile_status,
            '-end': end_volatile_status,
            '-curestatus': curestatus,
            '-cureteam': cureteam,
            '-weather': weather,
            '-fieldstart': fieldstart,
            '-fieldend': fieldend,
            '-sidestart': sidestart,
            '-sideend': sideend,
            '-item': set_item,
            '-enditem': remove_item,
            '-immune': set_opponent_ability,
            '-ability': set_opponent_ability_from_ability_tag,
            'detailschange': form_change,
            'replace': form_change,
            '-formechange': form_change,
            '-mega': mega,
            '-zpower': zpower,
            '-clearnegativeboost': clearnegativeboost,
            '-singleturn': singleturn,
            'upkeep': upkeep
        }

        function_to_call = battle_modifiers_lookup.get(action)
        if function_to_call is not None:
            function_to_call(battle, split_msg)

        if action in ['turn', 'upkeep']:
            return True

    if action == 'inactive':
        return False

    if action != "request":
        return battle.force_switch
