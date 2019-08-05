import constants
from showdown.helpers import boost_multiplier_lookup


class Pokemon(object):
    __slots__ = (
        'id',
        'level',
        'hp',
        'maxhp',
        'ability',
        'item',
        'base_stats',
        'attack',
        'defense',
        'special_attack',
        'special_defense',
        'speed',
        'attack_boost',
        'defense_boost',
        'special_attack_boost',
        'special_defense_boost',
        'speed_boost',
        'accuracy_boost',
        'evasion_boost',
        'status',
        'volatile_status',
        'moves',
        'types',
        'can_mega_evo',
        'scoring_multiplier'
    )

    def __init__(self,
                 identifier,
                 level,
                 hp,
                 maxhp,
                 ability,
                 item,
                 base_stats,
                 attack,
                 defense,
                 special_attack,
                 special_defense,
                 speed,
                 attack_boost,
                 defense_boost,
                 special_attack_boost,
                 special_defense_boost,
                 speed_boost,
                 accuracy_boost,
                 evasion_boost,
                 status,
                 volatile_status,
                 moves,
                 types,
                 can_mega_evo,
                 scoring_multiplier=1):
        self.id = identifier
        self.level = level
        self.hp = hp
        self.maxhp = maxhp
        self.ability = ability
        self.item = item
        self.base_stats = base_stats
        self.attack = attack
        self.defense = defense
        self.special_attack = special_attack
        self.special_defense = special_defense
        self.speed = speed
        self.attack_boost = attack_boost
        self.defense_boost = defense_boost
        self.special_attack_boost = special_attack_boost
        self.special_defense_boost = special_defense_boost
        self.speed_boost = speed_boost
        self.accuracy_boost = accuracy_boost
        self.evasion_boost = evasion_boost
        self.status = status
        self.volatile_status = volatile_status
        self.moves = moves
        self.types = types
        self.can_mega_evo = can_mega_evo
        self.scoring_multiplier = scoring_multiplier

    @classmethod
    def from_state_pokemon_dict(cls, d):
        return Pokemon(
            d[constants.ID],
            d[constants.LEVEL],
            d[constants.HITPOINTS],
            d[constants.MAXHP],
            d[constants.ABILITY],
            d[constants.ITEM],
            d[constants.BASESTATS],
            d[constants.STATS][constants.ATTACK],
            d[constants.STATS][constants.DEFENSE],
            d[constants.STATS][constants.SPECIAL_ATTACK],
            d[constants.STATS][constants.SPECIAL_DEFENSE],
            d[constants.STATS][constants.SPEED],
            d[constants.BOOSTS][constants.ATTACK],
            d[constants.BOOSTS][constants.DEFENSE],
            d[constants.BOOSTS][constants.SPECIAL_ATTACK],
            d[constants.BOOSTS][constants.SPECIAL_DEFENSE],
            d[constants.BOOSTS][constants.SPEED],
            d[constants.BOOSTS][constants.ACCURACY],
            d[constants.BOOSTS][constants.EVASION],
            d[constants.STATUS],
            d[constants.VOLATILE_STATUS],
            d[constants.MOVES],
            d[constants.TYPES],
            d[constants.CAN_MEGA_EVO],
            d.get(constants.SCORING_MULTIPLIER, 1)
        )

    @classmethod
    def from_dict(cls, d):
        return Pokemon(
            d[constants.ID],
            d[constants.LEVEL],
            d[constants.HITPOINTS],
            d[constants.MAXHP],
            d[constants.ABILITY],
            d[constants.ITEM],
            d[constants.BASESTATS],
            d[constants.ATTACK],
            d[constants.DEFENSE],
            d[constants.SPECIAL_ATTACK],
            d[constants.SPECIAL_DEFENSE],
            d[constants.SPEED],
            d[constants.ATTACK_BOOST],
            d[constants.DEFENSE_BOOST],
            d[constants.SPECIAL_ATTACK_BOOST],
            d[constants.SPECIAL_DEFENSE_BOOST],
            d[constants.SPEED_BOOST],
            0,
            0,
            d[constants.STATUS],
            set(d[constants.VOLATILE_STATUS]),
            d[constants.MOVES],
            d[constants.TYPES],
            d[constants.CAN_MEGA_EVO],
            d.get(constants.SCORING_MULTIPLIER, 1)
        )

    def calculate_boosted_stats(self):
        return {
            constants.ATTACK: boost_multiplier_lookup[self.attack_boost] * self.attack,
            constants.DEFENSE: boost_multiplier_lookup[self.defense_boost] * self.defense,
            constants.SPECIAL_ATTACK: boost_multiplier_lookup[self.special_attack_boost] * self.special_attack,
            constants.SPECIAL_DEFENSE: boost_multiplier_lookup[self.special_defense_boost] * self.special_defense,
            constants.SPEED: boost_multiplier_lookup[self.speed_boost] * self.speed,
        }

    def is_grounded(self):
        if 'flying' in self.types or self.ability == 'levitate' or self.item == 'airballoon':
            return False
        return True

    def __repr__(self):
        return str({
                constants.ID: self.id,
                constants.LEVEL: self.level,
                constants.HITPOINTS: self.hp,
                constants.MAXHP: self.maxhp,
                constants.ABILITY: self.ability,
                constants.ITEM: self.item,
                constants.BASESTATS: self.base_stats,
                constants.ATTACK: self.attack,
                constants.DEFENSE: self.defense,
                constants.SPECIAL_ATTACK: self.special_attack,
                constants.SPECIAL_DEFENSE: self.special_defense,
                constants.SPEED: self.speed,
                constants.ATTACK_BOOST: self.attack_boost,
                constants.DEFENSE_BOOST: self.defense_boost,
                constants.SPECIAL_ATTACK_BOOST: self.special_attack_boost,
                constants.SPECIAL_DEFENSE_BOOST: self.special_defense_boost,
                constants.SPEED_BOOST: self.speed_boost,
                constants.STATUS: self.status,
                constants.VOLATILE_STATUS: list(self.volatile_status),
                constants.MOVES: self.moves,
                constants.TYPES: self.types,
                constants.CAN_MEGA_EVO: self.can_mega_evo,
                constants.SCORING_MULTIPLIER: self.scoring_multiplier
            })

    def active_hash(self):
        """Unique identifier for a pokemon"""
        return (
            self.id,  # id is used instead of types
            self.hp,
            self.maxhp,
            self.ability,
            self.item,
            self.status,
            frozenset(self.volatile_status),
            self.attack,
            self.defense,
            self.special_attack,
            self.special_defense,
            self.speed,
            self.attack_boost,
            self.defense_boost,
            self.special_attack_boost,
            self.special_defense_boost,
            self.speed_boost,
        )

    def reserve_hash(self):
        """Unique identifier for a pokemon in the reserves
           This exists because it is a lighter calculation than active_hash"""
        return (
            self.hp,
            self.maxhp,
            self.ability,
            self.item,
            self.status,
            self.attack,
            self.defense,
            self.special_attack,
            self.special_defense,
            self.speed,
        )

    def __eq__(self, other):
        return self.active_hash() == other.active_hash()

    def __hash__(self):
        return hash(self.active_hash())
