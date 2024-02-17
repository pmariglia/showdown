import logging
from copy import deepcopy

from data.team_datasets import TeamDatasets
from showdown.battle import Battle
from ..helpers import pick_safest_move_from_battles
from ..helpers import format_decision

logger = logging.getLogger(__name__)


class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)

    def during_team_preview(self):
        opponent_pkmn_names = [p.name for p in self.opponent.reserve]

        TeamDatasets.set_pokemon_sets(opponent_pkmn_names)
        for pkmn in self.opponent.reserve:
            pkmn_info = TeamDatasets.pokemon_sets[pkmn.name]
            split_info = pkmn_info.split("|")
            pkmn.ability = split_info[1]
            pkmn.item = split_info[2]
            pkmn.set_spread(
                split_info[3],
                split_info[4]
            )
            for m in split_info[5:]:
                pkmn.add_move(m)

    def find_best_move(self):
        battles = deepcopy(self)
        safest_move = pick_safest_move_from_battles([battles])
        return format_decision(self, safest_move)
