import logging
from copy import deepcopy

from data.team_datasets import TeamDatasets
from showdown.battle import Battle
from ..helpers import pick_safest_move_from_battles
from ..helpers import format_decision

logger = logging.getLogger(__name__)


def set_most_likely_pokemon_from_team_datasets(pkmn):
    """
    Modifies the pkmn object to set the most likely moves/item/ability
    Uses the TeamDatasets, but will default to Smogon Usage data if a set cannot be found
    """

    predicted_set = TeamDatasets.predict_set(pkmn)
    if predicted_set is not None:
        pkmn.moves = []
        for mv in predicted_set.moves:
            pkmn.add_move(mv)
        pkmn.ability = predicted_set.ability
        pkmn.item = predicted_set.item
        pkmn.set_spread(predicted_set.nature, predicted_set.evs)
        logger.debug(
            "Assumed set for opponent's {}:\t{} {} {} {} {}".format(
                pkmn.name, pkmn.nature, pkmn.evs, pkmn.ability, pkmn.item, pkmn.moves)
        )
        return

    predicted_set = TeamDatasets.predict_set(pkmn, match_item=False, match_ability=False)
    if predicted_set is not None:
        pkmn.set_most_likely_ability_unless_revealed()
        pkmn.set_most_likely_item_unless_revealed()
        pkmn.moves = []
        for mv in predicted_set.moves:
            pkmn.add_move(mv)
        pkmn.set_spread(predicted_set.nature, predicted_set.evs)
        logger.debug(
            "Assumed set for opponent's {}:\t{} {} {} {} {}".format(
                pkmn.name, pkmn.nature, pkmn.evs, pkmn.ability, pkmn.item, pkmn.moves)
        )
        return

    pkmn.guess_most_likely_attributes()

    logger.debug(
        "Assumed set for opponent's {}:\t{} {} {} {} {}".format(
            pkmn.name, pkmn.nature, pkmn.evs, pkmn.ability, pkmn.item, pkmn.moves)
        )


def prepare_battles(battle):
    battle_copy = deepcopy(battle)

    for pkmn in filter(lambda x: x.is_alive(), battle_copy.opponent.reserve):
        if not pkmn.moves:
            pkmn.guess_most_likely_attributes()
        else:
            set_most_likely_pokemon_from_team_datasets(pkmn)

    if not battle_copy.opponent.active.moves:
        battles = battle_copy.prepare_battles(join_moves_together=True)
    else:
        set_most_likely_pokemon_from_team_datasets(battle_copy.opponent.active)
        battles = [battle_copy]

    for b in battles:
        b.opponent.lock_moves()

    return battles


class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)

    def during_team_preview(self):
        opponent_pkmn_names = [p.name for p in self.opponent.reserve]
        TeamDatasets.set_pokemon_sets(opponent_pkmn_names)

        exact_team = TeamDatasets.get_exact_team(opponent_pkmn_names)
        if exact_team is not None:
            logger.info("Found an exact team")
            for pkmn, pkmn_info in exact_team.items():
                for pkmn_obj in self.opponent.reserve:
                    if pkmn_obj.name == pkmn:
                        split_info = pkmn_info.split("|")
                        pkmn_obj.ability = split_info[1]
                        pkmn_obj.item = split_info[2]
                        pkmn_obj.set_spread(
                            split_info[3],
                            split_info[4]
                        )
                        for m in split_info[5:]:
                            pkmn_obj.add_move(m)

    def find_best_move(self):
        battles = prepare_battles(self)
        safest_move = pick_safest_move_from_battles(battles)
        return format_decision(self, safest_move)
