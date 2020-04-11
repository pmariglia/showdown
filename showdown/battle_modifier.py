import json
from copy import deepcopy
import logging

import constants
from data import all_move_json
from data import pokedex
from showdown.battle import Pokemon
from showdown.battle import LastUsedMove
from showdown.battle import DamageDealt
from showdown.helpers import normalize_name
from showdown.helpers import get_pokemon_info_from_condition
from showdown.helpers import calculate_stats
from showdown.engine.find_state_instructions import get_effective_speed
from showdown.engine.damage_calculator import calculate_damage


logger = logging.getLogger(__name__)


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


def switch_or_drag(battle, split_msg):
    if is_opponent(battle, split_msg):
        side = battle.opponent
        logger.debug("Opponent has switched - clearing the last used move")
    else:
        side = battle.user
        side.side_conditions[constants.TOXIC_COUNT] = 0

    if side.active is not None:
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
    move_name = normalize_name(split_msg[3].strip().lower())

    if is_opponent(battle, split_msg):
        side = battle.opponent
        pkmn = battle.opponent.active
    else:
        side = battle.user
        pkmn = battle.user.active

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


def start_volatile_status(battle, split_msg):
    if is_opponent(battle, split_msg):
        pkmn = battle.opponent.active
    else:
        pkmn = battle.user.active

    volatile_status = normalize_name(split_msg[3].split(":")[-1])
    if volatile_status not in pkmn.volatile_statuses:
        logger.debug("Starting the volatile status {} on {}".format(volatile_status, pkmn.name))
        pkmn.volatile_statuses.append(volatile_status)

    if volatile_status == constants.DYNAMAX:
        pkmn.hp *= 2
        pkmn.max_hp *= 2
        logger.debug("{} started dynamax - doubling their HP to {}/{}".format(pkmn.name, pkmn.hp, pkmn.max_hp))

    if constants.ABILITY in split_msg[3]:
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

    new_pokemon = Pokemon.from_switch_string(split_msg[3])
    new_pokemon.moves = previous_moves
    if new_pokemon in side.reserve:
        side.reserve.remove(new_pokemon)

    side.active = new_pokemon
    side.active.hp = hp_percent * side.active.max_hp
    side.active.boosts = previous_boosts
    side.active.status = previous_status

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


def mega(battle, split_msg):
    if is_opponent(battle, split_msg):
        side = battle.opponent
    else:
        side = battle.user

    side.active.is_mega = True
    logger.debug("Mega-Pokemon: {}".format(side.active.name))


def transform(battle, split_msg):
    if is_opponent(battle, split_msg):
        transformed_into_name = normalize_name(split_msg[3].split(':')[1])

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
    if len(moves) != 2 or moves[0][0].startswith(battle.user.name) or moves[0][1][constants.PRIORITY] != moves[1][1][constants.PRIORITY]:
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
    bot_effective_speed = get_effective_speed(state, state.self)

    if battle.trick_room:
        has_scarf = opponent_effective_speed > bot_effective_speed
    else:
        has_scarf = bot_effective_speed > opponent_effective_speed

    if has_scarf:
        logger.debug("Opponent {} could not have gone first - setting it's item to choicescarf".format(battle.opponent.active.name))
        battle.opponent.active.item = 'choicescarf'


def get_damage_dealt(battle, split_msg, next_messages):
    move_end_strings = {'move', 'switch', 'upkeep', ''}

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
        if len(next_line_split) < 2 or next_line_split[1] in move_end_strings:
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

    max_damage = float('-inf')
    potential_battles = battle.prepare_battles(guess_mega_evo_opponent=False, join_moves_together=True)

    battle_copy = deepcopy(battle)
    battle_copy.user.from_json(battle.request_json)
    for b in potential_battles:
        if b.opponent.active.item != choice_item:
            b.opponent.active.set_spread(*spread)
            b.user.active.stats = battle_copy.user.active.stats

            state = b.create_state()

            damage = calculate_damage(state, constants.OPPONENT, damage_dealt.move, battle.user.last_used_move.move, calc_type='max')[0]
            max_damage = max(max_damage, damage)

    # dont infer if we did not find a damage amount
    if max_damage == float('-inf'):
        return

    if (damage_dealt.percent_damage * battle.user.active.max_hp) > (max_damage * 1.2):  # multiply to avoid rounding errors
        logger.debug("{} has {}".format(battle.opponent.active.name, choice_item))
        battle.opponent.active.item = choice_item


def update_battle(battle, msg):
    msg_lines = msg.split('\n')

    action = None
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
            '-immune': set_ability,
            '-ability': set_opponent_ability_from_ability_tag,
            'detailschange': form_change,
            'replace': form_change,
            '-formechange': form_change,
            '-transform': transform,
            '-mega': mega,
            '-zpower': zpower,
            '-clearnegativeboost': clearnegativeboost,
            '-singleturn': singleturn,
            'upkeep': upkeep,
            'turn': turn
        }

        function_to_call = battle_modifiers_lookup.get(action)
        if function_to_call is not None:
            function_to_call(battle, split_msg)

        if action == 'move' and is_opponent(battle, split_msg):
            check_choicescarf(battle, msg_lines)
            damage_dealt = get_damage_dealt(battle, split_msg, msg_lines[i + 1:])
            if damage_dealt:
                check_choice_band_or_specs(battle, damage_dealt)

        if action == 'turn':
            return True

    if action in ['inactive', 'updatesearch']:
        return False

    if action != "request":
        return battle.force_switch


async def async_update_battle(battle, msg):
    return update_battle(battle, msg)
