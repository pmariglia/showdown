from enum import Enum, auto, IntEnum


class CalcType(Enum):
    average = auto()
    min = auto()
    max = auto()
    min_max = auto()
    min_max_average = auto()
    all = auto()
    random = auto()

CHALLENGE_USER = "CHALLENGE_USER"
ACCEPT_CHALLENGE = "ACCEPT_CHALLENGE"
SEARCH_LADDER = "SEARCH_LADDER"
BOT_MODES = [CHALLENGE_USER, ACCEPT_CHALLENGE, SEARCH_LADDER]

STANDARD_BATTLE = "standard_battle"
RANDOM_BATTLE = "random_battle"

NO_TEAM_PREVIEW_GENS = {
    "gen1",
    "gen2",
    "gen3",
    "gen4"
}

PICK_SAFEST = "safest"
PICK_NASH_EQUILIBRIUM = "nash"

START_STRING = "|start"
RQID = 'rqid'
TEAM_PREVIEW_POKE = "poke"
START_TEAM_PREVIEW = "clearpoke"

MOVES = "moves"
ABILITIES = "abilities"
ITEMS = "items"
COUNT = "count"
SETS = "sets"

UNKNOWN_ITEM = "unknown_item"

UNKOWN_POKEMON_FORMES = ['silvally', 'arceus', 'genesect', 'urshifu']

SMOGON_HAS_STATS_PAGE_SUFFIXES = ["ubers", "ou", "uu", "ru", "nu", "pu", "lc", "oublitz", "nationaldexbeta", "nationaldex", "monotype"]

# a lookup for the opponent's name given the bot's name
# this has to do with the Pokemon-Showdown PROTOCOL
ID_LOOKUP = {
    "p1": "p2",
    "p2": "p1"
}

# mutator strings
MUTATOR_SWITCH = "switch"
MUTATOR_APPLY_VOLATILE_STATUS = "apply_volatile_status"
MUTATOR_REMOVE_VOLATILE_STATUS = "remove_volatile_status"
MUTATOR_DAMAGE = "damage"
MUTATOR_HEAL = "heal"
MUTATOR_BOOST = "boost"
MUTATOR_BOOST_MULTIPLE ="boosts"
MUTATOR_UNBOOST = "unboost"
MUTATOR_UNBOOST_MULTIPLE = "unboosts"
MUTATOR_APPLY_STATUS = "apply_status"
MUTATOR_REMOVE_STATUS = "remove_status"
MUTATOR_SIDE_START = "side_start"
MUTATOR_SIDE_END = "side_end"
MUTATOR_WISH_START = "wish_start"
MUTATOR_WISH_DECREMENT = "wish_decrement"
MUTATOR_FUTURESIGHT_START = "futuresight_start"
MUTATOR_FUTURESIGHT_DECREMENT = "futuresight_decrement"
MUTATOR_DISABLE_MOVE = "disable_move"
MUTATOR_ENABLE_MOVE = "enable_move"
MUTATOR_WEATHER_START = "weather_start"
MUTATOR_WEATHER_END = "weather_end"
MUTATOR_FIELD_START = "field_start"
MUTATOR_FIELD_END = "field_end"
MUTATOR_TOGGLE_TRICKROOM = "toggle_trickroom"
MUTATOR_CHANGE_TYPE = "change_type"
MUTATOR_CHANGE_ITEM = "change_item"
MUTATOR_CHANGE_STATS = "change_stats"


DAMAGE = 'damage'
HEAL = "heal"
HEAL_TARGET = "heal_target"

FORCE_SWITCH = 'forceSwitch'
REVIVING = 'reviving'
WAIT = 'wait'
TRAPPED = "trapped"
MAYBE_TRAPPED = "maybeTrapped"
ITEM = "item"

CONDITION = "condition"
DISABLED = "disabled"
PP = "pp"
CURRENT_PP = 'current_pp'

SELF = "self"
USER = "user"
NORMAL = 'normal'
OPPONENT = "opponent"
ALLY_SIDE = "allySide"
ALL_ADJACENT_FOES = "allAdjacentFoes"
FOESIDE = "foeSide"
ALL_ADJACENT = "allAdjacent"
ALL = "all"
RANDOM_NORMAL = "randomNormal"

REFLECTABLE = "reflectable"

FLAGS = 'flags'

MOVE_TARGET_SELF = [SELF, ALLY_SIDE, ALL]
MOVE_TARGET_OPPONENT = [NORMAL, OPPONENT, ALL_ADJACENT, ALL_ADJACENT_FOES, ALL, RANDOM_NORMAL]

DO_NOTHING_MOVE = 'splash'

ID = "id"
BASESTATS = "baseStats"
LEVEL = "level"
NAME = "name"
STATUS = "status"
TYPES = "types"
TYPE = "type"
BASE_POWER = "basePower"
WEIGHT = "weightkg"
NATURE = "nature"
EVS = "evs"
IVS = "ivs"
TERASTALLIZED = "terastallized"

SIDE = "side"
POKEMON = "pokemon"
FNT = "fnt"

SWITCH_STRING = "switch"
WIN_STRING = "|win|"
TIE_STRING = "|tie"
CHAT_STRING = "|c|"
TIME_LEFT = "Time left:"
DETAILS = "details"
IDENT = "ident"

MEGA_EVOLVE_GENERATIONS = [
    "gen6",
    "gen7"
]
CAN_MEGA_EVO = "canMegaEvo"
CAN_ULTRA_BURST = "canUltraBurst"
CAN_DYNAMAX = "canDynamax"
CAN_TERASTALLIZE = "canTerastallize"
CAN_Z_MOVE = "canZMove"
ZMOVE = "zmove"
ULTRA_BURST = "ultra"
MEGA = "mega"

ACTIVE = "active"
RESERVE = "reserve"
SIDE_CONDITIONS = "side_conditions"
LAST_USED_MOVE = "last_used_move"
WEATHER = "weather"
FIELD = "field"

PRIORITY = "priority"
STATS = "stats"
MAXHP = "maxhp"
BOOSTS = "boosts"
TARGET = "target"


class StatEnum(IntEnum):
    HITPOINTS = 0
    ATTACK = 1
    DEFENSE = 2
    SPECIAL_ATTACK = 3
    SPECIAL_DEFENSE = 4
    SPEED = 5
    ACCURACY = 6
    EVASION = 7



# TODO: these are deprecated
HITPOINTS = "hp"
ATTACK = "attack"
DEFENSE = "defense"
SPECIAL_ATTACK = "special-attack"
SPECIAL_DEFENSE = "special-defense"
SPEED = "speed"
ACCURACY = "accuracy"
EVASION = "evasion"

STAT_LOOKUP = STAT_ABBREVIATION_REVERSE_LOOKUPS = {
    HITPOINTS: StatEnum.HITPOINTS,
    ATTACK: StatEnum.ATTACK,
    DEFENSE: StatEnum.DEFENSE,
    SPECIAL_ATTACK: StatEnum.SPECIAL_ATTACK,
    SPECIAL_DEFENSE: StatEnum.SPECIAL_DEFENSE,
    SPEED: StatEnum.SPEED,
    ACCURACY: StatEnum.ACCURACY,
    EVASION: StatEnum.EVASION
}

STAT_ABBRV_LOOKUP = {
    'hp': StatEnum.HITPOINTS,
    'atk': StatEnum.ATTACK,
    'def': StatEnum.DEFENSE,
    'spa': StatEnum.SPECIAL_ATTACK,
    'spd': StatEnum.SPECIAL_DEFENSE,
    'spe': StatEnum.SPEED,
    'accuracy': StatEnum.ACCURACY,
    'evasion': StatEnum.EVASION
}
STAT_ABBRV_REVERSE_LOOKUP = dict((v,k) for k,v in STAT_ABBRV_LOOKUP.items())

ATTACK_BOOST = "attack_boost"
DEFENSE_BOOST = "defense_boost"
SPECIAL_ATTACK_BOOST = "special_attack_boost"
SPECIAL_DEFENSE_BOOST = "special_defense_boost"
SPEED_BOOST = "speed_boost"
ACCURACY_BOOST = "accuracy_boost"
EVASION_BOOST = "evasion_boost"

ABILITY = 'ability'
REQUEST_DICT_ABILITY = ABILITY

MAX_BOOSTS = 6

STAT_ABBREVIATION_LOOKUPS = {
    "atk": ATTACK,
    "def": DEFENSE,
    "spa": SPECIAL_ATTACK,
    "spd": SPECIAL_DEFENSE,
    "spe": SPEED,
    "accuracy": ACCURACY,
    "evasion": EVASION
}


STAT_STRINGS = (ATTACK, DEFENSE, SPECIAL_ATTACK, SPECIAL_DEFENSE, SPEED)
STAT_STRINGS_ALL = (ATTACK, DEFENSE, SPECIAL_ATTACK, SPECIAL_DEFENSE, SPEED, EVASION, ACCURACY)
STAT_BOOST_STRINGS = (ATTACK_BOOST, DEFENSE_BOOST, SPECIAL_ATTACK_BOOST, SPECIAL_DEFENSE_BOOST, SPEED_BOOST)
STAT_BOOST_STRINGS_ALL = (ATTACK_BOOST, DEFENSE_BOOST, SPECIAL_ATTACK_BOOST, SPECIAL_DEFENSE_BOOST,
                          SPEED_BOOST, EVASION_BOOST, ACCURACY_BOOST)

HIDDEN_POWER = 'hiddenpower'
HIDDEN_POWER_TYPE_STRING_INDEX = -1
HIDDEN_POWER_ACTIVE_MOVE_BASE_DAMAGE_STRING = "60"
HIDDEN_POWER_RESERVE_MOVE_BASE_DAMAGE_STRING = ""

FAINTED = "dead"

PHYSICAL = "physical"
SPECIAL = "special"
CATEGORY = "category"

DAMAGING_CATEGORIES = [PHYSICAL, SPECIAL]

CRASH = "crash"
RECOIL = "recoil"
DRAIN = "drain"
CONTACT = "contact"
CHARGE = "charge"
POWDER = "powder"
DRAG = "drag"
SOUND = "sound"

VOLATILE_STATUS = "volatileStatus"
SECONDARY = "secondary"
CHANCE = "chance"
LOCKED_MOVE = "lockedmove"

# Side-Effects
REFLECT = 'reflect'
LIGHT_SCREEN = 'lightscreen'
AURORA_VEIL = 'auroraveil'
SAFEGUARD = 'safeguard'
TAILWIND = 'tailwind'
STICKY_WEB = 'stickyweb'
WISH = "wish"
FUTURE_SIGHT = "futuresight"
HEALING_WISH = 'healingwish'

# weather
RAIN = "raindance"
SUN = "sunnyday"
SAND = "sandstorm"
HAIL = "hail"
SNOW = "snow"
ICE_WEATHER = "snow"
DESOLATE_LAND = "desolateland"
HEAVY_RAIN = "primordialsea"

IRREVERSIBLE_WEATHER = {DESOLATE_LAND, HEAVY_RAIN}
HAIL_OR_SNOW = {HAIL, SNOW}

POKEMON_CANNOT_HAVE_ITEMS_REMOVED = {
    'kyogreprimal',
    'groudonprimal',
    'giratinaorigin',
    'zaciancrowned',
    'zamazentacrowned'
}

# Hazards
STEALTH_ROCK = 'stealthrock'
SPIKES = 'spikes'
TOXIC_SPIKES = 'toxicspikes'
COURT_CHANGE = 'courtchange'

TYPECHANGE = 'typechange'
TYPE_CHANGE_ABILITIES = {
    'protean',
    'libero'
}

FIRST_TURN_MOVES = {
    'fakeout',
    'firstimpression'
}

BOOST_RESET_MOVES = {
    'haze',
    'clearsmog'
}

ABILITY_AFTER_MOVE = {
    "static",
    "flamebody",
    "tanglinghair"
}

WEIGHT_BASED_MOVES = {
    'heavyslam',
    'heatcrash',
    'lowkick',
    'grassknot',
}

SPEED_BASED_MOVES = {
    'gyroball',
    'electroball'
}

COURT_CHANGE_SWAPS = {
    'spikes',
    'toxicspikes',
    'stealthrock',
    'stickyweb',
    'lightscreen',
    'reflect',
    'auroraveil',
    'tailwind'
}

HAZARD_CLEARING_MOVES = ['rapidspin', 'defog', 'courtchange', 'mortalspin', 'tidyup']

SPIN_TIDYUP_CLEARS = [
    STEALTH_ROCK,
    SPIKES,
    TOXIC_SPIKES,
    STICKY_WEB,
]

DEFOG_CLEARS = [
    STEALTH_ROCK,
    SPIKES,
    TOXIC_SPIKES,
    STICKY_WEB,
    REFLECT,
    LIGHT_SCREEN,
    AURORA_VEIL
]

TRICK_ROOM = "trickroom"

TERRAIN = "terrain"
ELECTRIC_TERRAIN = "electricterrain"
GRASSY_TERRAIN = "grassyterrain"
MISTY_TERRAIN = "mistyterrain"
PSYCHIC_TERRAIN = "psychicterrain"

# switch-out moves
SWITCH_OUT_MOVES = {"uturn", "voltswitch", "partingshot", "teleport", 'flipturn', 'chillyreception'}

# volatile statuses
FLINCH = "flinch"
CONFUSION = "confusion"
LEECH_SEED = "leechseed"
SUBSTITUTE = "substitute"
TAUNT = "taunt"
ROOST = "roost"
PROTECT = "protect"
BANEFUL_BUNKER = "banefulbunker"
SILK_TRAP = "silktrap"
SPIKY_SHIELD = "spikyshield"
DYNAMAX = "dynamax"
TERASTALLIZE = "terastallize"
PARTIALLY_TRAPPED = "partiallytrapped"
TRANSFORM = 'transform'

PROTECT_VOLATILE_STATUSES = [PROTECT, BANEFUL_BUNKER, SPIKY_SHIELD, SILK_TRAP]

# non-volatile statuses
SLEEP = "slp"
BURN = "brn"
FROZEN = "frz"
PARALYZED = "par"
POISON = "psn"
TOXIC = "tox"
TOXIC_COUNT = "toxic_count"
NON_VOLATILE_STATUSES = {SLEEP, BURN, FROZEN, PARALYZED, POISON, TOXIC}

# chances to break out of non-volatile statuses
WAKE_UP_PERCENT = 0.33
THAW_PERCENT = 0.20
FULLY_PARALYZED_PERCENT = 0.25

THAW_IF_USES = {'scald', 'flamewheel', 'sacredfire', 'flareblitz', 'fusionflare', 'steameruption', 'scorchingsands'}
THAW_IF_HIT_BY = {'scald', 'steameruption', 'scorchingsands'}

IMMUNE_TO_STAT_LOWERING_ABILITIES = {
    'clearbody',
    'whitesmoke',
    'fullmetalbody'
}

IMMUNE_TO_STAT_LOWERING_ITEMS = {
    "clearamulet"
}

IMMUNE_TO_SLEEP_ABILITIES = {'insomnia', 'sweetveil', 'vitalspirit'}
IMMUNE_TO_BURN_ABILITIES = {'waterveil', 'waterbubble'}
IMMUNE_TO_FROZEN_ABILITIES = {'magmaarmor'}
IMMUNE_TO_POISON_ABILITIES = {'immunity', 'pastelveil'}
IMMUNE_TO_PARALYSIS_ABILITIES = {'limber'}

ABILITIES_THAT_IGNORE_OTHER_ABILITIES = {
    'moldbreaker',
    'turboblaze',
    'teravolt'
}

BYPASSABLE_ABILITIES = {
    # gen8 (probably)
    'pastelveil',
    'iceface',
    'punkrock',

    # https://pokemondb.net/ability/mold-breaker
    # https://pokemondb.net/ability/turboblaze
    # https://pokemondb.net/ability/teravolt/
    'aromaveil',
    'battlearmor',
    'bigpecks',
    'bulletproof',
    'clearbody',
    'contrary',
    'damp',
    'dazzling',
    'disguise',
    'dryskin',
    'filter',
    'flashfire',
    'flowergift',
    'flowerveil',
    'fluffy',
    'friendguard',
    'furcoat',
    'heatproof',
    'heavymetal',
    'hypercutter',
    'immunity',
    'innerfocus',
    'insomnia',
    'keeneye',
    'leafguard',
    'levitate',
    'lightmetal',
    'lightningrod',
    'limber',
    'magicbounce',
    'magmaarmor',
    'marvelscale',
    'motordrive',
    'multiscale',
    'oblivious',
    'overcoat',
    'owntempo',
    'queenlymajesty',
    'sandveil',
    'sapsipper',
    'shellarmor',
    'shielddust',
    'simple',
    'snowcloak',
    'solidrock',
    'soundproof',
    'stickyhold',
    'stormdrain',
    'sturdy',
    'suctioncups',
    'sweetveil',
    'tangledfeet',
    'telepathy',
    'thickfat',
    'unaware',
    'vitalspirit',
    'voltabsorb',
    'waterabsorb',
    'waterbubble',
    'waterveil',
    'whitesmoke',
    'wonderguard',
    'wonderskin'
}

CHOICE_ITEMS = {'choicescarf', 'choiceband', 'choicespecs'}
