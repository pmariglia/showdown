import logging
from copy import deepcopy

import constants
import data
from data.helpers import get_pokemon_sets
from showdown.battle import Battle
from showdown.battle import Move
from ..helpers import pick_safest_move_from_battles
from ..helpers import format_decision

logger = logging.getLogger(__name__)


def get_pokemon_sets_and_movesets(pkmn):
    exclude_items = []
    if not pkmn.can_have_life_orb:
        exclude_items.append("lifeorb")
    if not pkmn.can_have_heavydutyboots:
        exclude_items.append("heavydutyboots")
    if not pkmn.can_have_heavydutyboots:
        exclude_items.append("heavydutyboots")
    if not pkmn.can_have_assaultvest:
        exclude_items.append("assaultvest")
    if not pkmn.can_have_choice_item:
        exclude_items.append("choicescarf")
        exclude_items.append("choiceband")
        exclude_items.append("choicespecs")
    if pkmn.can_not_have_band:
        exclude_items.append("choiceband")
    if pkmn.can_not_have_specs:
        exclude_items.append("choicespecs")

    full_sets = {}
    movesets = {}
    try:
        pkmn_dict = data.ou_sets[pkmn.name]
    except KeyError:
        return full_sets, movesets

    for team, value in pkmn_dict.items():
        split_team = team.split("|")
        ability = split_team[0]
        item = split_team[1]
        moves = split_team[4:]
        if not all(m.name in moves for m in pkmn.moves):
            continue

        joined_moves = "|".join(moves)
        if joined_moves in movesets:
            movesets[joined_moves] += value
        else:
            movesets[joined_moves] = value

        if pkmn.item is not None and pkmn.item != constants.UNKNOWN_ITEM and item != pkmn.item:
            continue
        elif pkmn.item == constants.UNKNOWN_ITEM and item in exclude_items:
            continue
        elif pkmn.ability is not None and ability != pkmn.ability:
            continue
        else:
            if team in full_sets:
                full_sets[team] += value
            else:
                full_sets[team] = value

    movesets = sorted(movesets.items(), key=lambda x: x[1], reverse=True)
    full_sets = sorted(full_sets.items(), key=lambda x: x[1], reverse=True)

    return full_sets, movesets


def validate_pokemon_set(pkmn):
    pkmn_speed = pkmn.stats[constants.SPEED]
    if pkmn.item == "choicescarf":
        pkmn_speed = int(1.5*pkmn_speed)

    if pkmn.speed_range.min <= pkmn_speed <= pkmn.speed_range.max:
        return True

    return False


def set_most_likely_pokemon_from_api(pkmn):
    """Modifies the pkmn object to set the most likely moves/item/ability"""
    full_sets, move_sets = get_pokemon_sets_and_movesets(pkmn)

    if full_sets:
        logger.debug("Using most likely full set for {}".format(pkmn.name))

        for pkmn_set in full_sets:
            pkmn_copy = deepcopy(pkmn)

            full_set = pkmn_set[0]
            split_set = full_set.split("|")

            if pkmn_copy.ability is None:
                pkmn_copy.ability = split_set[0]

            if pkmn_copy.item == constants.UNKNOWN_ITEM:
                pkmn_copy.item = split_set[1]

            pkmn_copy.set_spread(split_set[2], split_set[3])

            for m in split_set[4:8]:
                if Move(m) not in pkmn_copy.moves:
                    pkmn_copy.add_move(m)

            if validate_pokemon_set(pkmn_copy):
                pkmn.ability = pkmn_copy.ability
                pkmn.item = pkmn_copy.item
                pkmn.moves = pkmn_copy.moves
                pkmn.set_spread(split_set[2], split_set[3])
                break
            else:
                logger.debug("Set {} is invalid for {}".format(full_set, pkmn_copy.name))

    elif move_sets:
        logger.debug("No full set found for {}, using just the most likely move set".format(pkmn.name))

        move_set = move_sets[0][0]
        pkmn.set_most_likely_item_unless_revealed()
        pkmn.set_most_likely_ability_unless_revealed()
        pkmn.set_most_likely_spread()

        split_set = move_set.split("|")
        for m in split_set:
            if Move(m) not in pkmn.moves:
                pkmn.add_move(m)

    else:
        logger.info("Got nothing from the API, using old code")
        try:
            pokemon_sets = get_pokemon_sets(pkmn.name)
        except KeyError:
            logger.warning(
                "No sets for {}, trying to find most likely attributes".format(pkmn.name))
            pkmn.guess_most_likely_attributes()
            return

        possible_abilities = sorted(pokemon_sets["abilities"], key=lambda x: x[1], reverse=True)
        possible_items = sorted(pokemon_sets["items"], key=lambda x: x[1], reverse=True)
        possible_moves = sorted(pokemon_sets["moves"], key=lambda x: x[1], reverse=True)

        items = pkmn.get_possible_items(possible_items)
        abilities = pkmn.get_possible_abilities(possible_abilities)
        expected_moves, chance_moves = pkmn.get_possible_moves(possible_moves)

        all_moves = expected_moves + chance_moves
        for m in all_moves:
            pkmn.add_move(m)
        pkmn.ability = abilities[0]
        pkmn.item = items[0]
        pkmn.set_most_likely_spread()

    logger.debug(
        "Assumed set for opponent's {}:\t{} {} {} {} {}".format(
            pkmn.name, pkmn.nature, pkmn.evs, pkmn.ability, pkmn.item, pkmn.moves)
        )


def prepare_battles(battle):
    from copy import deepcopy
    battle_copy = deepcopy(battle)

    for pkmn in filter(lambda x: x.is_alive(), battle_copy.opponent.reserve):
        if not pkmn.moves:
            pkmn.guess_most_likely_attributes()
        else:
            set_most_likely_pokemon_from_api(pkmn)

    if not battle_copy.opponent.active.moves:
        battles = battle_copy.prepare_battles(join_moves_together=True)
    else:
        set_most_likely_pokemon_from_api(battle_copy.opponent.active)
        battles = [battle_copy]

    for b in battles:
        b.opponent.lock_moves()

    return battles


class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)

    def find_best_move(self):
        battles = prepare_battles(self)
        safest_move = pick_safest_move_from_battles(battles)
        return format_decision(self, safest_move)
