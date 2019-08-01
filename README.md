# Showdown  ![umbreon](https://play.pokemonshowdown.com/sprites/xyani/umbreon.gif)
Showdown is a Pokémon battle-bot that can play battles on [Pokemon Showdown](https://pokemonshowdown.com/).

The bot can play games in generations 4 through 7 however some of the evaluation logic is assuming gen7 mechanics.

## Python version
Developed and testing using Python 3.6.3.

## Getting Started


### Configuration
Environment variables are used for configuration

The configurations available are:
```
SAVE_REPLAY: (bool, default False) Specifies whether or not to save replays of the battles
LOG_TO_FILE: (bool, default False) Specifies whether or not to save for each battle to a file in {PWD}/logs/
LOG_LEVEL: (string, default "DEBUG") The Python logging level 
WEBSOCKET_URI: (string, default is the official PokemonShowdown websocket address: "sim.smogon.com:8000") The address to use to connect to the Pokemon Showdown websocket 
PS_USERNAME: (string, required) Pokemon Showdown username
PS_PASSWORD: (string) Pokemon Showdown password
DECISION_METHOD: (string, default "safest") The decision making method. Options are "safest" and "nash". More on this in the Decision Logic section
BOT_MODE: (string, required) The mode the the bot will operate in. Options are "CHALLENGE_USER", "SEARCH_LADDER", or "ACCEPT_CHALLENGE"
USER_TO_CHALLENGE: (string, required if BOT_MODE is "CHALLENGE_USER") The user to challenge
POKEMON_MODE: (string, required) The type of game this bot will play games in
TEAM_NAME: (string, required if POKEMON_MODE is one where a team is required) The name of the JSON file that contains the team you want to use. More on this below in the Specifying Teams section.
RUN_COUNT: (integer, required) The amount of games this bot will play before quitting
```

### Running without Docker

#### Clone

Clone the repository with `git clone https://github.com/pmariglia/showdown.git`

Install the requirements with `pip install -r requirements.txt`.

Be sure to use a virtual environment to isolate your packages.

#### Tests
Run all tests with `python -m unittest discover -s tests/ -t .`

#### Run
Running with `python run.py` will start the bot with configurations specified by environment variables in a file named `.env`

Here is a sample `.env` file, this configuration will log-in and search for a gen7randombattle:
```
WEBSOCKET_URI=sim.smogon.com:8000
PS_USERNAME=MyCoolUsername
PS_PASSWORD=MySuperSecretPassword
BOT_MODE=SEARCH_LADDER
POKEMON_MODE=gen7randombattle
RUN_COUNT=1
```

### Running with Docker

#### Clone the repository
`git clone https://github.com/pmariglia/showdown.git`

#### Build the Docker image
`docker build . -t showdown`

#### Run with an environment variable file
`docker run --env-file .env showdown`


## Decision Logic

The bot searches through the game-tree for two turns and can make a decision in two different ways. Decisions can be made using Minimax or a Nash-Equilibrium

For decisions with random outcomes a weighted average is taken for all possible end states.
For example: If using draco meteor versus some arbitrary other move results in a score of 1000 if it hits (90%) and a score of 900 if it misses (10%), the overall score for using
draco meteor is (0.9 * 1000) + (0.1 * 900) = 990.

Most aspects of Pokémon are accounted for, such as:

1. Damage Rolls

2. Spreads

3. Move-Sets

4. Abilities

5. Items

6. Hazards

7. Weather

### Minimax
use DECISION_LOGIC=safest (default unless otherwise specified)

[Minimax](https://en.wikipedia.org/wiki/Minimax) means that the bot will make a move that minimizes the possible loss for a turn. 

This decision type is deterministic - the bot will always make the same move given the same situation again.

### Nash-Equilibrium
use DECISION_LOGIC=nash

Using the information it has, plus some assumptions about the opponent, the bot will calculate the [Nash-Equilibrium](https://en.wikipedia.org/wiki/Nash_equilibrium) with the highest payoff
and select a move from that distribution.

The Nash Equilibrium is calculated using command-line tools provided by the [Gambit](http://www.gambit-project.org/) project.
This decision method should only be used when running with Docker and will fail otherwise.

This decision method is **not** deterministic. The bot **may** make a different move if presented with the same situation again.

## Performance

In general the bot will perform much better in random battles and when using the "safest" decision making method.

These are the bot's rankings after several hundred games in each of the OU, PU, and RandomBattle formats:
 
 ![SafestRankings](https://i.imgur.com/CkNzN8v.png)


The non-deterministic Nash-Equilibrium decision making has similar results for standard formats,
but poorer results for random battles:

![NashRankings](https://i.imgur.com/T6973FO.png)

## Specifying Teams
The user can specify teams in JSON format to be used for non-random battles. Examples can be found in `teams/team_jsons/`.

The name of the `.json` file must used as `TEAM_NAME` in the configuration file.

For example, this repository contains two sample teams: `ou_sample.json`, and `pu_sample.json`.

Those teams can be used with the configuration `TEAM_NAME=ou_sample` or `TEAM_NAME=pu_sample` respectively.
