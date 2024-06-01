# Showdown  ![umbreon](https://play.pokemonshowdown.com/sprites/xyani/umbreon.gif)
A Pokémon battle-bot that can play battles on [Pokemon Showdown](https://pokemonshowdown.com/).

The bot can play single battles in generations 3 through 8.

![badge](https://github.com/pmariglia/showdown/actions/workflows/pythonapp.yml/badge.svg)

## Python version
Developed and tested using Python 3.8.

## Getting Started

### Configuration
Environment variables are used for configuration.
You may either set these in your environment before running,
or populate them in the [env](https://github.com/pmariglia/showdown/blob/master/env) file.

The configurations available are:

| Config Name | Type | Required | Description |
|---|:---:|:---:|---|
| **`BATTLE_BOT`** | string | yes | The BattleBot module to use. More on this below in the Battle Bots section |
| **`WEBSOCKET_URI`** | string | yes | The address to use to connect to the Pokemon Showdown websocket |
| **`PS_USERNAME`** | string | yes | Pokemon Showdown username |
| **`PS_PASSWORD`** | string | yes | Pokemon Showdown password  |
| **`BOT_MODE`** | string | yes | The mode the the bot will operate in. Options are `CHALLENGE_USER`, `SEARCH_LADDER`, or `ACCEPT_CHALLENGE` |
| **`POKEMON_MODE`** | string | yes | The type of game this bot will play: `gen8ou`, `gen7randombattle`, etc. |
| **`USER_TO_CHALLENGE`** | string | only if `BOT_MODE` is `CHALLENGE_USER` | If `BOT_MODE` is `CHALLENGE_USER`, this is the name of the user you want your bot to challenge |
| **`RUN_COUNT`** | int | no | The number of games the bot will play before quitting |
| **`TEAM_NAME`** | string | no | The name of the file that contains the team you want to use. More on this below in the Specifying Teams section. |
| **`ROOM_NAME`** | string | no | If `BOT_MODE` is `ACCEPT_CHALLENGE`, the bot will join this chatroom while waiting for a challenge. |
| **`SAVE_REPLAY`** | boolean | no | Specifies whether or not to save replays of the battles (`True` / `False`) |
| **`LOG_LEVEL`** | string | no | The Python logging level (`DEBUG`, `INFO`, etc.) |

### Running without Docker

**1. Clone**

Clone the repository with `git clone https://github.com/pmariglia/showdown.git`

**2. Install Requirements**

Install the requirements with `pip install -r requirements.txt`.

**3. Configure your [env](https://github.com/pmariglia/showdown/blob/master/env) file**

Here is a sample:
```
BATTLE_BOT=safest
WEBSOCKET_URI=wss://sim3.psim.us/showdown/websocket
PS_USERNAME=MyUsername
PS_PASSWORD=MyPassword
BOT_MODE=SEARCH_LADDER
POKEMON_MODE=gen7randombattle
RUN_COUNT=1
```

**4. Run**

Run with `python run.py`

### Running with Docker
This requires Docker 17.06 or higher.

**1. Clone the repository**

`git clone https://github.com/pmariglia/showdown.git`

**2. Build the Docker image**

`docker build . -t showdown`

**3. Run with an environment variable file**

`docker run --env-file env showdown`

## Battle Bots

This project has a few different battle bot implementations.
Each of these battle bots use a different method to determine which move to use.

### Safest
use `BATTLE_BOT=safest`

The bot searches through the game-tree for two turns and selects the move that minimizes the possible loss for a turn.

For decisions with random outcomes a weighted average is taken for all possible end states.
For example: If using draco meteor versus some arbitrary other move results in a score of 1000 if it hits (90%) and a score of 900 if it misses (10%), the overall score for using
draco meteor is (0.9 * 1000) + (0.1 * 900) = 990.

This is equivalent to the [Expectiminimax](https://en.wikipedia.org/wiki/Expectiminimax) strategy.

This decision type is deterministic - the bot will always make the same move given the same situation again.

### Nash-Equilibrium (experimental)
use `BATTLE_BOT=nash_equilibrium`

Using the information it has, plus some assumptions about the opponent, the bot will attempt to calculate the [Nash-Equilibrium](https://en.wikipedia.org/wiki/Nash_equilibrium) with the highest payoff
and select a move from that distribution.

The Nash Equilibrium is calculated using command-line tools provided by the [Gambit](http://www.gambit-project.org/) project.
This decision method should only be used when running with Docker and will fail otherwise.

This decision method is **not** deterministic. The bot **may** make a different move if presented with the same situation again.

### Team Datasets (experimental)

use `BATTLE_BOT=team_datasets`

Using a file of sets & teams, this battle-bot is meant to have a better
understanding of Pokeon sets that may appear.
Populate this dataset by editing `data/team_datasets.json`.

Still uses the `safest` decision making method for picking a move, but in theory the knowledge of sets should
result in better decision making.

### Most Damage
use `BATTLE_BOT=most_damage`

Selects the move that will do the most damage to the opponent

Does not switch

## Write your own bot
Create a package in [showdown/battle_bots](https://github.com/pmariglia/showdown/tree/master/showdown/battle_bots) with
a module named `main.py`. In this module, create a class named `BattleBot`, override the Battle class,
and implement your own `find_best_move` function.

Set the `BATTLE_BOT` environment variable to the name of your package and your function will be called each time PokemonShowdown prompts the bot for a move

## The Battle Engine
The bots in the project all use a Pokemon battle engine to determine all possible transpositions that may occur from a pair of moves.

For more information, see [ENGINE.md](https://github.com/pmariglia/showdown/blob/master/ENGINE.md) 

## Specifying Teams
You can specify teams by setting the `TEAM_NAME` environment variable.
Examples can be found in `teams/teams/`.

Passing in a directory will cause a random team to be selected from that directory.

The path specified should be relative to `teams/teams/`.

#### Examples

Specify a file:
```
TEAM_NAME=gen8/ou/clef_sand
```

Specify a directory:
```
TEAM_NAME=gen8/ou
```
