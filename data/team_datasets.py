from __future__ import annotations

from dataclasses import dataclass
import os
import json
import logging
import typing
from typing import Tuple
from typing import Optional

import constants
from showdown.engine.helpers import calculate_stats

if typing.TYPE_CHECKING:
    from showdown.battle import Pokemon

logger = logging.getLogger(__name__)

PWD = os.path.dirname(os.path.abspath(__file__))


@dataclass(frozen=True)
class PokemonMoveset:
    moves: Tuple[str, ...]

    def pkmn_can_have_moves(self, pkmn: Pokemon) -> bool:
        for mv in pkmn.moves:
            if mv.name not in self.moves:
                return False
        return True

    def __iter__(self):
        yield from self.moves


@dataclass(frozen=True)
class PokemonSet:
    tera_type: str
    ability: str
    item: str
    nature: str
    evs: Tuple[int, int, int, int, int, int]
    moves: PokemonMoveset

    def item_check(self, pkmn: Pokemon) -> bool:
        if self.item == "lifeorb" and not pkmn.can_have_life_orb:
            return False
        elif self.item == "heavydutyboots" and not pkmn.can_have_heavydutyboots:
            return False
        elif self.item == "assaultvest" and not pkmn.can_have_assaultvest:
            return False
        elif self.item in constants.CHOICE_ITEMS and not pkmn.can_have_choice_item:
            return False
        elif self.item == "choiceband" and pkmn.can_not_have_band:
            return False
        elif self.item == "choicespecs" and pkmn.can_not_have_specs:
            return False
        else:
            return self.item == pkmn.item or pkmn.item is None or pkmn.item == constants.UNKNOWN_ITEM

    def speed_check(self, pkmn: Pokemon):
        """
        The only non-observable speed modifier that should allow a
        Pokemon's speed_range to be set is choicescarf
        """
        stats = calculate_stats(pkmn.base_stats, pkmn.level, evs=self.evs, nature=self.nature)
        speed = stats[constants.SPEED]
        if self.item == "choicescarf":
            speed = int(speed * 1.5)

        return pkmn.speed_range.min <= speed <= pkmn.speed_range.max

    def pkmn_can_contain_set(self, pkmn: Pokemon, match_ability=True, match_item=True, speed_check=True) -> bool:
        ability_check = not match_ability or (
            self.ability == pkmn.ability or pkmn.ability is None
        )
        item_check = not match_item or self.item_check(pkmn)
        speed_check = not speed_check or self.speed_check(pkmn)

        return ability_check and item_check and speed_check and self.moves.pkmn_can_have_moves(pkmn)


class _TeamDatasets:
    def __init__(self):
        self.pokemon_sets = {}

    def set_pokemon_sets(self, pkmn_names):
        """
        To not have to hold the entire `team_datasets.json` in memory,
        this allows you to only populate team_datasets with only the
        sets of the pokemon you provide. Ideally this is called during
        team preview
        """
        self.pokemon_sets = {}
        self.append_to_team_datasets(pkmn_names)

    def append_to_team_datasets(self, pkmn_names):
        sets = os.path.join(PWD, 'team_datasets.json')
        with open(sets, 'r') as f:
            sets_dict = json.load(f)["pokemon"]

        for pkmn in pkmn_names:
            try:
                self.pokemon_sets[pkmn] = sets_dict[pkmn]
            except KeyError:
                logger.warning("No pokemon information being added for {}".format(pkmn))

    @staticmethod
    def get_exact_team(pkmn_names):
        sets = os.path.join(PWD, 'team_datasets.json')
        with open(sets, 'r') as f:
            teams_dict = json.load(f)["teams"]

        pkmn_lookup = "|".join(pkmn_names)
        try:
            return teams_dict[pkmn_lookup][0]
        except KeyError:
            return None

    @staticmethod
    def to_pokemon_set(pkmn_set_str: str) -> PokemonSet:
        tera_type, ability, item, nature, evs, *moves = pkmn_set_str.split("|")
        split_evs = evs.split(",")
        return PokemonSet(
            tera_type,
            ability,
            item,
            nature,
            (
                int(split_evs[0]),
                int(split_evs[1]),
                int(split_evs[2]),
                int(split_evs[3]),
                int(split_evs[4]),
                int(split_evs[5]),
            ),
            PokemonMoveset(tuple(moves))
        )

    def predict_set(self, pkmn: Pokemon, match_ability=True, match_item=True) -> Optional[PokemonSet]:
        """
        Finds the most likely PokemonSet that this Pokemon can have from self.team_datasets

        Returns None if a PokemonSet cannot be found
        """
        if not self.pokemon_sets:
            logger.warning("Called `predict_set` when team_datasets was empty")

        try:
            pkmn_data = self.pokemon_sets[pkmn.name]
        except KeyError:
            pkmn_data = {}

        for pkmn_set, _ in sorted(pkmn_data.items(), key=lambda x: x[1], reverse=True):
            pkmn_set = self.to_pokemon_set(pkmn_set)
            if pkmn_set.pkmn_can_contain_set(pkmn, match_ability=match_ability, match_item=match_item):
                return pkmn_set

        return None


TeamDatasets = _TeamDatasets()
