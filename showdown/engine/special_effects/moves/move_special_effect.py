import constants


def trickroom(mutator, attacking_side, attacking_pokemon, defending_pokemon):
    return [
        (constants.MUTATOR_TOGGLE_TRICKROOM,)
    ]


def trick(mutator, attacking_side, attacking_pokemon, defending_pokemon):
    instructions = []
    if (
            (defending_pokemon.item_can_be_removed() or defending_pokemon.item is None) and
            not (defending_pokemon.item is None and attacking_pokemon.item is None)
    ):
        instructions.append(
            (
                constants.MUTATOR_CHANGE_ITEM,
                constants.SELF,
                mutator.state.opponent.active.item,
                mutator.state.self.active.item
            )
        )
        instructions.append(
            (
                constants.MUTATOR_CHANGE_ITEM,
                constants.OPPONENT,
                mutator.state.self.active.item,
                mutator.state.opponent.active.item
            )
        )
        return instructions


switcheroo = trick


def weather_move(mutator, weather_move_name):
    if mutator.state.weather != weather_move_name and mutator.state.weather not in constants.IRREVERSIBLE_WEATHER:
        return [
            (constants.MUTATOR_WEATHER_START, weather_move_name, mutator.state.weather)
        ]


def raindance(mutator, attacking_side, attacking_pokemon, defending_pokemon):
    return weather_move(mutator, constants.RAIN)


def sunnyday(mutator, attacking_side, attacking_pokemon, defending_pokemon):
    return weather_move(mutator, constants.SUN)


def sandstorm(mutator, attacking_side, attacking_pokemon, defending_pokemon):
    return weather_move(mutator, constants.SAND)


def hail(mutator, attacking_side, attacking_pokemon, defending_pokemon):
    return weather_move(mutator, constants.HAIL)


def junglehealing(mutator, attacking_side, attacking_pokemon, defending_pokemon):
    if attacking_pokemon.status is not None:
        return [
            (constants.MUTATOR_REMOVE_STATUS, attacking_side, attacking_pokemon.status)
        ]
