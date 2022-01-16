# Showdown  ![umbreon](https://play.pokemonshowdown.com/sprites/xyani/umbreon.gif)
A Pokémon battle-bot that can play battles on [Pokemon Showdown](https://pokemonshowdown.com/).

The bot can play single battles in generations 3 through 8 however some of the battle mechanics assume it is gen8.

![badge](https://action-badges.now.sh/pmariglia/showdown)

## Python version
Developed and tested using Python 3.6.3.

## Getting started

* python 3.6 or greater
* Install requirements with `pip install -r requirements.txt`
* Codebase is not installable as a python package 

### Config

This project uses `environs` to load environment variable from a `.env` file.
**Do not add the .env to source control.**
The following environment variables are accepted

```
BATTLE_BOT              default = safest
SAVE_REPLAY
USE_RELATIVE_WEIGHTS
GAMBIT_PATH
MAX_SEARCH_DEPTH
DYNAMIC_SEARCH_DEPTH
GREETING_MESSAGE
WEBSOCKET_URI           sim.smogon.com:8000
PS_USERNAME
BOT_MODE
TEAM_NAME               None
POKEMON_MODE
RUN_COUNT               1
ROOM_NAME
```
### Docker

The project uses Docker to build a maintainable environment for the project, using python:3.6-slim as a base image.
The container uses ENV variables `PYTHONIOENCODING=utf-8`, `GAMBIT_PATH=gambit-enummixed`.
The entrypoint to the Docker container is `run.py`:

It runs an asynchronous function `run.showdown`:
It creates a configuration file from system environment variables.
It runs a loop which challenges a user or accepts a match
and runs a pokemon battle.
The loop tracks the number of wins, losses, and battles run.
The loop breaks if more battles are run than the config value.
Raises a ValueError if the bot mode is invalid.

### Developers

* Unit tests are stored in `tests/` (uses unittest)
* There are no specific developer requirements
* The project uses GitHub Actions for CI/CD.

| CI File | Purpose |
|:--------|:--------|
| `.github/workflows/pythonapp.yml` | Runs unit tests. Executes on push to branch `master` and pull request to branch `master` |

## Code Overview

### Entrypoints

There are 0 source code entrypoints in top-level `__main__`/`__init__` files.
The codebase has a flat structure with no central package.
Source code is in:
`data/`,
`showdown/`,
`teams/`.

### Class structure

#### showdown.battle.Battle

The `showdown.battle.Battle` base class has 4 child classes:
* `showdown.battle_bots.most_damage.main.BattleBot`
* `showdown.battle_bots.nash_equilibrium.main.BattleBot`
* `showdown.battle_bots.ou_scraped_teams.main.BattleBot`
* `showdown.battle_bots.safest.main.BattleBot`

```python
class showdown.battle.Battle(self, battle_tag)
```

```python
    def prepare_battles(self, guess_mega_evo_opponent=True, join_moves_together=False)
```

Returns a list of battles based on this one
The battles have the opponent's reserve pokemon's unknowns filled in
The opponent's active pokemon in each of the battles has a different set.

#### showdown.battle_bots.most_damage.main.BattleBot

```python
class showdown.battle_bots.most_damage.main.BattleBot(*args, **kwargs)
```

```python
    def find_best_moves(self)
```

### Examples:

#### The Pokemon Object

```python
from showdown.engine import Pokemon
pokemon = Pokemon(
    # mandatory upon initialization
    identifier='pikachu',
    level=100,
    types=['electric'],
    hp=100,
    maxhp=100,
    ability='static',
    item='lightball',
    attack=100,
    defense=100,
    special_attack=100,
    special_defense=100,
    speed=100,
    
    # the remaining attributes are optional and have default values if not specified
    
    # nature is a string, evs are a tuple
    nature="serious",
    evs=(85,) * 6,

    # boosts: integer value between -6 and 6
    attack_boost=0,
    defense_boost=0,
    special_attack_boost=0,
    special_defense_boost=0,
    speed_boost=0,
    accuracy_boost=0,
    evasion_boost=0,
    
    # status: <string> or None
    status=None,
    
    # volatile_status: <set>
    volatile_status=set(),
    
    # moves: <list> of <dict>
    moves=[
        {'id': 'volttackle', 'disabled': False, 'current_pp': 8},
    ]
)
```

#### The Side Object


```python
from showdown.engine import Side
from showdown.engine import Pokemon
side = Side(
    active=Pokemon(...),
    reserve={
        'caterpie': Pokemon(...),
        'pidgey': Pokemon(...),
        ...
    },
    wish=(0, 0),
    side_conditions={
        'stealth_rock': 1,
        'spikes': 3,
        'toxic_spikes': 2,
        'tailwind': 1
    }
)
```

#### The State Object

This object represents the entire battle.

```python
from showdown.engine import State
from showdown.engine import Side
state = State(
    self=Side(...),
    opponent=Side(...),
    weather='sunnyday',
    field='electricterrain',
    trick_room=False
)
```

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

## Questions? Wanna Chat?
Send me a message on discord: pmariglia#5568
