from typing import List, Dict, Set, Optional, Tuple
from copy import deepcopy
import logging
from collections import defaultdict
import math
import random

import constants
from fp.battle import Pokemon, Battle, Move
from data.pkmn_sets import RandomBattleTeamDatasets
from fp.helpers import normalize_name

logger = logging.getLogger(__name__)

class TeamSampler:
    """Handles sampling complete teams given partial opponent information"""

    def __init__(self, battle_type: str):
        self.battle_type = battle_type

    def get_legal_pokemon(self, known_pokemon: Set[str]) -> Set[str]:
        """Get Pokemon that could legally fill remaining team slots"""
        return RandomBattleTeamDatasets.pkmn_sets.keys() - known_pokemon

    def get_consistent_sets(self, pokemon: Pokemon) -> List:
        """Filter sets to find those consistent with observed traits"""
        all_sets = RandomBattleTeamDatasets.get_pkmn_sets_from_pkmn_name(pokemon.name, pokemon.base_name)
        consistent_sets = []

        for p_set in all_sets:
            if p_set.full_set_pkmn_can_have_set(pokemon):
                consistent_sets.append(p_set)

        if not consistent_sets:
            logger.info(f"No consistent sets found for {pokemon.name} based on observations.")
            consistent_sets = all_sets
        return consistent_sets
    
    def get_pokemon_level(self, pokemon: Pokemon) -> int:
        levels_dict = RandomBattleTeamDatasets.pkmn_levels
        if pokemon.name in levels_dict:
            return levels_dict[pokemon.name]
        elif pokemon.base_name in levels_dict:
            return levels_dict[pokemon.base_name]

        # Fallback: check for a partial match
        for p in levels_dict:
            if pokemon.name.startswith(p) or p.startswith(pokemon.name):
                return levels_dict[p]
        return 80

    def sample_set_for_known_pokemon(self, pokemon: Pokemon) -> Tuple[Pokemon, float]:
        """Sample a set for a known Pokemon, ensuring consistency"""
        consistent_sets = self.get_consistent_sets(pokemon)
        if not consistent_sets:
            return None, float('-inf')

        # Weighted random sampling based on set counts
        total_count = sum(p.pkmn_set.count for p in consistent_sets)
        weights = [p.pkmn_set.count / total_count for p in consistent_sets]
        chosen_set = random.choices(consistent_sets, weights=weights, k=1)[0]

        # Create a Pokemon instance from the chosen set
        pkmn_set = chosen_set.pkmn_set
        moveset = chosen_set.pkmn_moveset.moves

        new_pokemon = Pokemon(pokemon.name, self.get_pokemon_level(pokemon))
        new_pokemon.ability = pkmn_set.ability
        new_pokemon.item = pkmn_set.item
        new_pokemon.moves = [m for m in moveset]
        new_pokemon.tera_type = pkmn_set.tera_type

        # Calculate log probability
        log_prob = math.log(chosen_set.pkmn_set.count) - math.log(total_count)

        logger.debug(f"Sampled consistent set for {pokemon.name}: {chosen_set} with log_prob {log_prob:.4f}")
        return new_pokemon, log_prob

    def sample_team(self, battle: Battle, known_pokemon: Dict[str, Pokemon]) -> Tuple[List[Pokemon], float]:
        """Sample a complete team consistent with observations"""
        team = []
        total_log_prob = 0.0

        # Handle known Pokemon first
        for name, pokemon in known_pokemon.items():
            new_pokemon, log_prob = self.sample_set_for_known_pokemon(pokemon)
            if new_pokemon is None:
                logger.warning(f"Failed to sample a consistent set for {name}, skipping team.")
                return [], float('-inf')

            # Deep copy to avoid shared references
            team.append(deepcopy(new_pokemon))
            total_log_prob += log_prob

        # Fill in remaining slots with random legal Pokémon
        num_needed = 6 - len(known_pokemon)
        legal_pool = list(self.get_legal_pokemon(set(known_pokemon.keys())))

        for _ in range(num_needed):
            name = random.choice(legal_pool)
            predicted_sets = RandomBattleTeamDatasets.pkmn_sets.get(name, [])
            if not predicted_sets:
                logger.debug(f"No sets available for {name}, skipping.")
                continue

            chosen_set = max(predicted_sets, key=lambda x: x.pkmn_set.count)

            new_pokemon = Pokemon(name, RandomBattleTeamDatasets.pkmn_levels.get(name))
            new_pokemon.ability = chosen_set.pkmn_set.ability
            new_pokemon.item = chosen_set.pkmn_set.item
            new_pokemon.moves = [Move(m) if isinstance(m, str) else m for m in chosen_set.pkmn_moveset.moves]
            new_pokemon.tera_type = chosen_set.pkmn_set.tera_type

            # Deep copy to ensure uniqueness
            team.append(deepcopy(new_pokemon))

        logger.info(f"Sampled team: {[p.name for p in team]} with log_prob {total_log_prob:.4f}")
        return team, total_log_prob



    def sample_teams(self, battle: Battle, num_teams: int = 4) -> List[Tuple[List[Pokemon], float]]:
        """Sample multiple unique teams with their probabilities"""
        known_pokemon = {
            battle.opponent.active.name: battle.opponent.active
        } if battle.opponent.active else {}
        known_pokemon.update({p.name: p for p in battle.opponent.reserve if p})

        generated_teams = set()
        teams = []
        attempts = 0
        max_attempts = num_teams * 3

        while len(teams) < num_teams and attempts < max_attempts:
            attempts += 1
            team, log_prob = self.sample_team(battle, known_pokemon)
            if log_prob == float('-inf'):
                continue

            # Ensure team uniqueness
            team_key = tuple(sorted(
                (p.name, str(p.ability), str(p.item), tuple(sorted(m if isinstance(m, str) else m.name for m in p.moves)))
                for p in team
            ))

            if team_key not in generated_teams:
                generated_teams.add(team_key)
                teams.append((team, log_prob))

        # Normalize probabilities
        if teams:
            max_log_prob = max(lp for _, lp in teams)
            probs = [math.exp(lp - max_log_prob) for _, lp in teams]
            total = sum(probs)
            if total > 0:
                teams = [(t, p / total) for (t, _), p in zip(teams, probs)]

        logger.info(f"Generated {len(teams)} unique teams out of {num_teams} requested.")
        return teams

def sample_opponent_teams(battle: Battle, num_teams: int = 4) -> List[Tuple[Battle, float]]:
    """Generate multiple complete battle states with team probabilities"""
    sampler = TeamSampler(battle.battle_type)
    sampled_teams = sampler.sample_teams(battle, num_teams)

    battles = []
    for team, prob in sampled_teams:
        new_battle = deepcopy(battle)
        
        # Ensure all Pokemon moves are properly instantiated as Move objects
        for pokemon in team:
            pokemon.moves = [Move(m) if isinstance(m, str) else m for m in pokemon.moves]
        
        # Handle active Pokemon first
        if new_battle.opponent.active:
            active_name = new_battle.opponent.active.name
            active_pokemon = next((p for p in team if p.name == active_name), None)
            if active_pokemon:
                active_hp = new_battle.opponent.active.hp  # Store original HP
                active_maxhp = new_battle.opponent.active.max_hp
                active_status = new_battle.opponent.active.status
                
                # Copy sampled properties to the active Pokemon
                new_battle.opponent.active.ability = active_pokemon.ability
                new_battle.opponent.active.item = active_pokemon.item
                new_battle.opponent.active.moves = active_pokemon.moves
                new_battle.opponent.active.tera_type = active_pokemon.tera_type
                
                # Restore original HP and status
                new_battle.opponent.active.hp = active_hp
                new_battle.opponent.active.max_hp = active_maxhp
                new_battle.opponent.active.status = active_status
        
        # Set reserve Pokemon (excluding active)
        reserve_pokemon = []
        for p in team:
            if not new_battle.opponent.active or p.name != new_battle.opponent.active.name:
                # Check if this Pokemon exists in original battle's reserve
                original = next((op for op in battle.opponent.reserve if op.name == p.name), None)
                if original:
                    # Copy HP and status from original
                    p.hp = original.hp
                    p.max_hp = original.max_hp
                    p.status = original.status
                reserve_pokemon.append(p)
                
        new_battle.opponent.reserve = reserve_pokemon
        battles.append((new_battle, prob))

    return battles