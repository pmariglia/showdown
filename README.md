# Showdown  ![umbreon](https://play.pokemonshowdown.com/sprites/xyani/umbreon.gif)
Showdown is a Pokémon battle-bot that can play battles on [Pokemon Showdown](https://pokemonshowdown.com/).

The bot can play games in generations 4 through 7 however some of the evaluation logic is assuming gen7 mechanics.

## Python version
Developed and testing using Python 3.6.3.

## Getting Started

### Installing
Clone the repository with `git clone https://github.com/pmariglia/showdown.git`

Install the requirements with `pip install -r requirements.txt`.

Be sure to use a virtual environment to isolate your packages.

### Tests
Run all tests with `python -m unittest discover -s tests/ -t .`

### Configuration
Showdown uses environment variables for configuration, which are read from a file named `.env` in the root of the project.

The configurations available are:
```
SAVE_REPLAY: (bool, default False) Specifies whether or not to save replays of the battles
LOG_TO_FILE: (bool, default False) Specifies whether or not to save for each battle to a file in {PWD}/logs/
LOG_LEVEL: (string, default "DEBUG") The Python logging level 
WEBSOCKET_URI: (string, default is the official PokemonShowdown websocket address: "sim.smogon.com:8000") The address to use to connect to the Pokemon Showdown websocket 
PS_USERNAME: (string, required) Pokemon Showdown username
PS_PASSWORD: (string) Pokemon Showdown password
BOT_MODE: (string, required) The mode the the bot will operate in. Options are "CHALLENGE_USER", "SEARCH_LADDER", or "ACCEPT_CHALLENGE"
USER_TO_CHALLENGE: (string, required if BOT_MODE is "CHALLENGE_USER") The user to challenge
POKEMON_MODE: (string, required) The type of game this bot will play games in
TEAM_NAME: (string, required if POKEMON_MODE is one where a team is required) The name of the JSON file that contains the team you want to use. More on this below in the Specifying Teams section.
SEARCH_DEPTH: (integer, default 2) The max search depth that will be used.
RUN_COUNT: (integer, required) The amount of games this bot will play before quitting
```

Here is a sample `.env` file

This configuration will use the Mega-Gardevoir team and search for a gen7ou battle:
```
SAVE_REPLAY=False
LOG_TO_FILE=False
LOG_LEVEL="DEBUG"
WEBSOCKET_URI="sim.smogon.com:8000"
PS_USERNAME="MyCoolUsername"
PS_PASSWORD="MySuperSecretPassword"
BOT_MODE="SEARCH_LADDER"
USER_TO_CHALLENGE="SomeScrub"
POKEMON_MODE="gen7ou"
TEAM_NAME="ou_mega_gard"
RUN_COUNT=1
```


### Running
Running with `python run.py` will start the bot with the settings specified in your `.env` file.


## Decision Logic

Showdown decides which move to make by first simulating all possible transpositions up to the search depth.
An evaluation function is used to score each combination of moves and the safest move is chosen.

MAX_SEARCH_DEPTH may be set in the config to search any depth desired. Leaving this value at the default (2) provides almost instant decisions. 3 is manageable for most machines.

Most aspects of Pokémon are accounted for, such as:

1. Damage Rolls

2. Spreads

3. Move-Sets

4. Abilities

5. Items

6. Hazards

7. Weather

## Specifying Teams
The user can specify teams in JSON format to be used for non-random battles. Examples can be found in `teams/team_jsons/`.

The name of the `.json` file must used as `TEAM_NAME` in the configuration file.
