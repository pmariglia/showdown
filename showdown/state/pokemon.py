from collections import defaultdict

import constants
from showdown.state.move import Move
from showdown.helpers import normalize_name
from showdown.helpers import calculate_stats
from data import pokedex
from data.helpers import get_all_possible_moves_for_random_battle
from data.helpers import get_most_likely_item_for_random_battle_pokemon
from data.helpers import get_most_likely_ability_for_random_battle
from data.helpers import get_all_possible_moves_for_standard_battle
from data.helpers import get_most_likely_item_for_standard_battle_pokemon
from data.helpers import get_most_likely_ability_for_standard_battle
from data.helpers import get_most_likely_spread_for_standard_battle

from config import logger


class Pokemon:

    def __init__(self, name: str, level: int):
        self.name = normalize_name(name)
        self.base_name = self.name
        self.level = level

        try:
            self.base_stats = pokedex[self.name][constants.BASESTATS]
        except KeyError:
            logger.info("Could not pokedex entry for {}".format(self.name))
            self.name = [k for k in pokedex if self.name.startswith(k)][0]
            logger.info("Using {} instead".format(self.name))
            self.base_stats = pokedex[self.name][constants.BASESTATS]

        self.stats = calculate_stats(self.base_stats, self.level)

        self.max_hp = self.stats.pop(constants.HITPOINTS)
        self.hp = self.max_hp
        if self.name == 'shedinja':
            self.max_hp = 1
            self.hp = 1

        self.ability = None
        self.types = pokedex[self.name][constants.TYPES]
        self.item = constants.UNKNOWN_ITEM

        self.fainted = False
        self.moves = []
        self.status = None
        self.volatile_statuses = []
        self.boosts = defaultdict(lambda: 0)
        self.can_mega_evo = False
        self.can_ultra_burst = True

    def is_alive(self):
        return self.hp > 0

    @classmethod
    def from_switch_string(cls, switch_string):
        details = switch_string.split(',')
        name = details[0]
        try:
            level = int(details[1].replace('L', '').strip())
        except (IndexError, ValueError):
            level = 100
        return Pokemon(name, level)

    def set_spread(self, nature, evs):
        evs = [int(e) for e in evs.split(',')]
        hp_percent = self.hp / self.max_hp
        self.stats = calculate_stats(self.base_stats, self.level, evs=evs, nature=nature)
        self.max_hp = self.stats.pop(constants.HITPOINTS)
        self.hp = self.max_hp * hp_percent

    def add_move(self, move_name: str):
        try:
            new_move = Move(move_name)
            self.moves.append(new_move)
            return new_move
        except KeyError:
            logger.warning("{} is not a known move".format(move_name))
            return None

    def get_move(self, move_name: str):
        for m in self.moves:
            if m.name == normalize_name(move_name):
                return m
        return None

    def update_moves_for_random_battles(self):
        if len(self.moves) == 4:
            logger.debug("{} revealed 4 moves, not guessing any more moves".format(self.name))
            return
        additional_moves = get_all_possible_moves_for_random_battle(self.name, [m.name for m in self.moves])
        logger.debug("Guessing additional moves for {}: {}".format(self.name, additional_moves))
        for m in additional_moves:
            self.moves.append(Move(m))

    def update_ability_for_random_battles(self):
        if self.ability is not None:
            logger.debug("{} has revealed it's ability, not guessing".format(self.name))
            return
        ability = get_most_likely_ability_for_random_battle(self.name)
        logger.debug("Guessing ability={} for {}".format(ability, self.name))
        self.ability = ability

    def update_item_for_random_battles(self):
        if self.item != constants.UNKNOWN_ITEM:
            logger.debug("{} has revealed it's item, not guessing".format(self.name))
            return
        item = get_most_likely_item_for_random_battle_pokemon(self.name)
        logger.debug("Guessing item={} for {}".format(item, self.name))
        self.item = item

    def update_moves_for_standard_battles(self):
        if len(self.moves) == 4:
            logger.debug("{} revealed 4 moves, not guessing any more moves".format(self.name))
            return
        additional_moves = get_all_possible_moves_for_standard_battle(self.name, [m.name for m in self.moves])
        logger.debug("Guessing additional moves for {}: {}".format(self.name, additional_moves))
        for m in additional_moves:
            self.moves.append(Move(m))

    def update_ability_for_standard_battles(self):
        if self.ability is not None:
            logger.debug("{} has revealed it's ability, not guessing".format(self.name))
            return
        ability = get_most_likely_ability_for_standard_battle(self.name)
        logger.debug("Guessing ability={} for {}".format(ability, self.name))
        self.ability = ability

    def update_item_for_standard_battles(self):
        if self.item != constants.UNKNOWN_ITEM:
            logger.debug("{} has revealed it's item, not guessing".format(self.name))
            return
        item = get_most_likely_item_for_standard_battle_pokemon(self.name)
        logger.debug("Guessing item={} for {}".format(item, self.name))
        self.item = item

    def update_spread_for_standard_battles(self):
        nature, evs = get_most_likely_spread_for_standard_battle(self.name)
        logger.debug("Spread assumption for {}: {}, {}".format(self.name, nature, evs))
        self.set_spread(nature, evs)

    def guess_random_battle_attributes(self):
        self.update_ability_for_random_battles()
        self.update_item_for_random_battles()
        self.update_moves_for_random_battles()

    def guess_standard_battle_attributes(self):
        self.update_ability_for_standard_battles()
        self.update_item_for_standard_battles()
        self.update_moves_for_standard_battles()
        self.update_spread_for_standard_battles()

    def to_dict(self):
        return {
            constants.FAINTED: self.fainted,
            constants.ID: self.name,
            constants.LEVEL: self.level,
            constants.HITPOINTS: self.hp,
            constants.MAXHP: self.max_hp,
            constants.ABILITY: self.ability,
            constants.ITEM: self.item,
            constants.BASESTATS: self.base_stats,
            constants.STATS: self.stats,
            constants.BOOSTS: self.boosts,
            constants.STATUS: self.status,
            constants.VOLATILE_STATUS: set(self.volatile_statuses),
            constants.MOVES: [m.to_dict() for m in self.moves],
            constants.TYPES: self.types,
            constants.CAN_MEGA_EVO: self.can_mega_evo
        }

    @classmethod
    def get_dummy(cls):
        p = Pokemon('pikachu', 100)
        p.hp = 0
        p.name = ''
        p.ability = None
        p.fainted = True
        return p

    def __eq__(self, other):
        return self.name == other.name and self.level == other.level

    def __repr__(self):
        return "{}, level {}".format(self.name, self.level)
