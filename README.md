# Showdown  ![umbreon](https://play.pokemonshowdown.com/sprites/xyani/umbreon.gif)
Showdown is a Pokémon battle-bot that can play battles on [Pokemon Showdown](https://pokemonshowdown.com/).

The bot can play single battles in generations 3 through 8 however some of the battle mechanics assume it is gen8.

![badge](https://action-badges.now.sh/pmariglia/showdown)

## Python version
Developed and tested using Python 3.6.3.

## Getting Started


### Configuration
Environment variables are used for configuration which are by default read from a file named `.env`

The configurations available are:
```
BATTLE_BOT: (string, default "safest") The BattleBot module to use. More on this below
SAVE_REPLAY: (bool, default False) Specifies whether or not to save replays of the battles
LOG_LEVEL: (string, default "DEBUG") The Python logging level 
WEBSOCKET_URI: (string, default is the official PokemonShowdown websocket address: "sim.smogon.com:8000") The address to use to connect to the Pokemon Showdown websocket 
PS_USERNAME: (string, required) Pokemon Showdown username
PS_PASSWORD: (string) Pokemon Showdown password 
BOT_MODE: (string, required) The mode the the bot will operate in. Options are "CHALLENGE_USER", "SEARCH_LADDER", or "ACCEPT_CHALLENGE"
USER_TO_CHALLENGE: (string, required if BOT_MODE is "CHALLENGE_USER") The user to challenge
POKEMON_MODE: (string, required) The type of game this bot will play games in
TEAM_NAME: (string, required if POKEMON_MODE is one where a team is required) The name of the file that contains the team you want to use. More on this below in the Specifying Teams section.
RUN_COUNT: (integer, required) The amount of games this bot will play before quitting
ROOM_NAME: (string, optional) Optionally join a room by this name is BOT_MODE is "ACCEPT_CHALLENGE"
```

Here is a minimal `.env` file. This configuration will log in and search for a gen8randombattle:
```
WEBSOCKET_URI=sim.smogon.com:8000
PS_USERNAME=MyCoolUsername
PS_PASSWORD=MySuperSecretPassword
BOT_MODE=SEARCH_LADDER
POKEMON_MODE=gen8randombattle
RUN_COUNT=1
```

### Running without Docker

#### Clone

Clone the repository with `git clone https://github.com/pmariglia/showdown.git`

#### Install Requirements

Install the requirements with `pip install -r requirements.txt`.

Be sure to use a virtual environment to isolate your packages.

#### Run
Running with `python run.py` will start the bot with configurations specified by environment variables read from a file named `.env`

### Running with Docker
This requires Docker 17.06 or higher.

#### Clone the repository
`git clone https://github.com/pmariglia/showdown.git`

#### Build the Docker image
`docker build . -t showdown`

#### Run with an environment variable file
`docker run --env-file .env showdown`

### Running on Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

After deploying, go to the Resources tab and turn on the worker.

## Battle Bots

### Safest
use `BATTLE_BOT=safest` (default unless otherwise specified)

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

### Most Damage
use `BATTLE_BOT=most_damage`

Selects the move that will do the most damage to the opponent

Does not switch

## Performance

These are the default battle-bot's results in three different formats for roughly 75 games played on a fresh account:

![RelativeWeightsRankings](https://i.imgur.com/eNpIlVg.png)

## Write your own bot
Create a package in `showdown/battle_bots` with a module named `main.py`. In this module, create a class named `BattleBot`, override the Battle class, and implement your own `find_best_move` function.

Set the `BATTLE_BOT` environment variable to the name of your package and your function will be called each time PokemonShowdown prompts the bot for a move

## The Battle Engine
The bots in the project all use a Pokemon battle engine to determine all possible transpositions that may occur from a pair of moves.

For more information, see [ENGINE.md](https://github.com/pmariglia/showdown/blob/master/ENGINE.md) 

## Specifying Teams
You can specify teams by setting the `TEAM_NAME` environment variable.
Examples can be found in `teams/teams/`.

Passing in a directory will cause a random team to be selected from that directory

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
