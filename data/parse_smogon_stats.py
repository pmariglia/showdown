import ntpath
import re
from datetime import datetime
from dateutil import relativedelta

import requests

import constants
from showdown.engine.helpers import normalize_name

OTHER_STRING = "other"
MOVES_STRING = "moves"
ITEM_STRING = "items"
SPREADS_STRING = "spreads"
ABILITY_STRING = "abilities"

PERCENTAGES_REGEX = '(\d+\.\d+%)'


def get_smogon_stats_file_name(game_mode, month_delta=1):
    """
    Gets the smogon stats url based on the game mode
    Uses the previous-month's statistics
    """

    # blitz comes and goes - use the non-blitz version
    if game_mode.endswith('blitz'):
        game_mode = game_mode[:-5]

    # always use the `-0` file - the higher ladder is for noobs
    smogon_url = "https://www.smogon.com/stats/{}-{}/chaos/{}-0.json"

    previous_month = datetime.now() - relativedelta.relativedelta(months=month_delta)
    year = previous_month.year
    month = "{:02d}".format(previous_month.month)

    return smogon_url.format(year, month, game_mode)


def get_pokemon_information(smogon_stats_url):
    spreads = []
    items = []
    moves = []
    abilities = []
    r = requests.get(smogon_stats_url)
    infos = r.json()['data']
    final_infos = {}
    for x in infos.keys():
        final_infos[x] = {}
        for t in infos[x]['Spreads']:
<<<<<<< HEAD
            if float("{:.16f}".format(float(infos[x]['Spreads'][t]))) != 0:
                spreads.append((normalize_name(t.split(':')[0]), normalize_name(t.split(':')[1].replace('/', ',')), float("{:.16f}".format(float(infos[x]['Spreads'][t])))))
        for j in infos[x]['Items']:
            if infos[x]['Items'][j] != 0:
                items.append((j, infos[x]['Items'][j]))
        for k in infos[x]['Moves']:
            if infos[x]['Moves'][k] != 0:
                moves.append((k, infos[x]['Moves'][k]))
        for l in infos[x]['Abilities']:
            if infos[x]['Abilities'][l] != 0:
                abilities.append((l, infos[x]['Abilities'][l]))
        final_infos[x][SPREADS_STRING] = spreads
        final_infos[x][ITEM_STRING] = items
        final_infos[x][MOVES_STRING] = moves
        final_infos[x][ABILITY_STRING] = abilities
        spreads.clear()
        items.clear()
        moves.clear()
        abilities.clear()
    return final_infos
=======
            spreads.append((t.split(':')[0], t.split(':')[1].replace('/', ','), float("{:.16f}".format(float(infos[x]['Spreads'][t])))))
        for j in infos[x]['Items']:
            items.append((j, infos[x]['Items'][j]))
        for k in infos[x]['Moves']:
            moves.append((k, infos[x]['Moves'][k]))
        for l in infos[x]['Abilities']:
            abilities.append((l, infos[x]['Abilities'][l]))
        final_infos[x]['spreads'] = spreads
        final_infos[x]['items'] = items
        final_infos[x]['moves'] = moves
        final_infos[x]['abilities'] = abilities
    return final_infos

>>>>>>> 21002806d8bb5c90d71f0aaf4679186a2fa9ef6d
