import constants


def grassyseed(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.field == constants.GRASSY_TERRAIN and attacking_pokemon.defense_boost < 6:
        return [
            (constants.MUTATOR_BOOST, attacking_side, constants.DEFENSE, 1),
            (constants.MUTATOR_CHANGE_ITEM, attacking_side, None, attacking_pokemon.item)
        ]


def mistyseed(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.field == constants.MISTY_TERRAIN and attacking_pokemon.special_defense_boost < 6:
        return [
            (constants.MUTATOR_BOOST, attacking_side, constants.SPECIAL_DEFENSE, 1),
            (constants.MUTATOR_CHANGE_ITEM, attacking_side, None, attacking_pokemon.item)
        ]


def psychicseed(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.field == constants.PSYCHIC_TERRAIN and attacking_pokemon.special_defense_boost < 6:
        return [
            (constants.MUTATOR_BOOST, attacking_side, constants.SPECIAL_DEFENSE, 1),
            (constants.MUTATOR_CHANGE_ITEM, attacking_side, None, attacking_pokemon.item)
        ]


def electricseed(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if state.field == constants.ELECTRIC_TERRAIN and attacking_pokemon.defense_boost < 6:
        return [
            (constants.MUTATOR_BOOST, attacking_side, constants.DEFENSE, 1),
            (constants.MUTATOR_CHANGE_ITEM, attacking_side, None, attacking_pokemon.item)
        ]


def boosterenergy(state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if attacking_pokemon.ability in ["quarkdrive", "protosynthesis"]:
        highest_stat = attacking_pokemon.get_highest_stat()
        return [
            (constants.MUTATOR_APPLY_VOLATILE_STATUS, attacking_side, attacking_pokemon.ability + constants.STAT_ABBREVIATION_REVERSE_LOOKUPS[highest_stat]),
            (constants.MUTATOR_CHANGE_ITEM, attacking_side, None, attacking_pokemon.item)
        ]


def item_on_switch_in(item_name, state, attacking_side, attacking_pokemon, defending_side, defending_pokemon):
    if attacking_pokemon.hp:
        try:
            return globals()[item_name](state, attacking_side, attacking_pokemon, defending_side, defending_pokemon)
        except KeyError:
            pass
