from data import pokedex
import constants
from showdown.engine.helpers import calculate_stats


def stancechange(state, attacking_side, attacking_move, attacking_pokemon, defending_pokemon):
    if attacking_pokemon.id in ['aegislash', 'aegislashblade']:
        if attacking_move[constants.CATEGORY] in constants.DAMAGING_CATEGORIES:
            change_stats_into = 'aegislashblade'
        elif attacking_move[constants.ID] == 'kingsshield':
            change_stats_into = 'aegislash'
        else:
            return None

        new_stats = calculate_stats(
            pokedex[change_stats_into][constants.BASESTATS],
            attacking_pokemon.level,
            nature=attacking_pokemon.nature,
            evs=attacking_pokemon.evs
        )

        return [
            (
                constants.MUTATOR_CHANGE_STATS,
                attacking_side,
                (
                    attacking_pokemon.maxhp,
                    new_stats[constants.ATTACK],
                    new_stats[constants.DEFENSE],
                    new_stats[constants.SPECIAL_ATTACK],
                    new_stats[constants.SPECIAL_DEFENSE],
                    attacking_pokemon.speed
                ),
                (
                    attacking_pokemon.hp,
                    attacking_pokemon.attack,
                    attacking_pokemon.defense,
                    attacking_pokemon.special_attack,
                    attacking_pokemon.special_defense,
                    attacking_pokemon.speed
                )
            )

        ]
    return None


def protean(state, attacking_side, attacking_move, attacking_pokemon, defending_pokemon):
    if [attacking_move[constants.TYPE]] != attacking_pokemon.types:
        return [(
            constants.MUTATOR_CHANGE_TYPE,
            attacking_side,
            [attacking_move[constants.TYPE]],
            attacking_pokemon.types
        )]


libero = protean


def ability_before_move(ability_name, state, attacking_side, attacking_move, attacking_pokemon, defending_pokemon):
    try:
        return globals()[ability_name](state, attacking_side, attacking_move, attacking_pokemon, defending_pokemon)
    except KeyError:
        return None
