# Battle-Engine
This project contains a Pokemon battle engine for single battles.

It can be used to determine the different types of transpositions a pair of moves will result in.

### This is not a perfect Pokemon Battle Engine!
This battle engine is meant to capture important aspects of Pokemon for the purposes of competitive single battles.
It is nowhere near as complete or robust as the [PokemonShowdown](https://github.com/smogon/pokemon-showdown) battle engine.

This code is always being improved and pull requests are very much welcome!

## Using the Battle Engine
The battle engine operates using State, Side, and Pokemon objects.

Note that any string values used within the engine (pokemon names, move names, ability names, item names, etc) must be stripped of spaces/special characters.

To convert values you can use the `normalize_name` function
```python
>>> from showdown.engine.helpers import normalize_name
>>> normalize_name('Pikachu')
'pikachu'
>>> normalize_name('Choice Scarf')
'choicescarf'
>>> normalize_name('Giratina-Origin')
'giratinaorigin'
>>> normalize_name('Flabébé')
'flabebe'
```

### The Pokemon Object

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

### The Side Object
This object represents one side of battle.
It contains an `active` Pokemon , a dictionary of `reserve` Pokemon, and a dictionary of `side_conditions`

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
    },
    future_sight=(0, 0)
)
```

### The State Object
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


## The StateMutator and Generating Instructions
The primary feature of this battle engine is the ability to generate and apply instructions.

### Applying and Reversing Instructions

Instructions are a list of tuples. They can be applied and reversed to mutate the state.
```python
from showdown.engine import State
from showdown.engine import StateMutator

state = State(...)  # initialize your state

state.user.active.hp = 100
print(state.user.active.hp)  # prints '100'

mutator = StateMutator(state)

instructions = [
    ('damage', 'self', 1)
]

mutator.apply(instructions)
print(state.user.active.hp)  # prints '99'

mutator.reverse(instructions)
print(state.user.active.hp)  # prints '100'
```

### Generating Instructions from a Pair of Moves

Instructions can be generated from a state if a pair of moves are provided.

The generated instructions will represent all possible paths the battle could take given the randomness of the moves.

Calling `get_all_state_instructions` will generate a list of TransposeInstruction objects,
each of which contains a list of instructions, as well as a likelihood (percentage) of its occurrence

#### Some Examples

Keep in mind that these are arbitrary examples, and the State generation is skipped for brevity.
Obviously, changes to the state will affect the generated instructions

Example: tackle being used by both combatants
```python
>> from showdown.engine import State
>> from showdown.engine import StateMutator
>> from showdown.engine import get_all_state_instructions

>> state = State(...)  # initialize your state

>> mutator = StateMutator(state)
>> my_move = 'tackle'
>> your_move = 'tackle'

>> transpose_instructions = get_all_state_instructions(mutator, my_move, your_move)

>> len(transpose_instructions)
>> 1  # no randomness here

>> first_instruction = transpose_instructions[0]

>> print(first_instruction.percentage)
>> 1.0  # 100% chance of happening

>> print(first_instruction.instructions)  
>> [('damage', 'self', 15), ('damage', 'opponent', 15)]
```

Example: thunderbolt being used by both combatants
```python
>> from showdown.engine import State
>> from showdown.engine import StateMutator
>> from showdown.engine import get_all_state_instructions

>> state = State(...)  # initialize your state
>> mutator = StateMutator(state)

>> my_move = 'thunderbolt'
>> your_move = 'thunderbolt'

>> transpose_instructions = get_all_state_instructions(mutator, my_move, your_move)

# randomness with secondary effects (paralysis in this case) means there are 5 different sets of instructions that could happen here
>> len(transpose_instructions)
>> 5

>> first_instruction = transpose_instructions[0]

# The first instruction is when both thunderbolts paralyze
# it has a 0.75 % chance of happening
>> print(first_instruction.percentage)
>> 0.0075000000000000015
>> print(first_instruction.instructions)  
>> [('damage', 'opponent', 45), ('apply_status', 'opponent', 'par'), ('damage', 'self', 45), ('apply_status', 'self', 'par')]

# Looking at another instruction
# this one is when the first thunderbolt paralyzes, and the other pokemon is fully-paralyzed and does not move
# it has a 2.5% chance of happening
>> another_instruction = transpose_instructions[2]
>> print(another_instruction.percentage)
>> 0.025
>> print(another_instruction.instructions)  
>> [('damage', 'opponent', 45), ('apply_status', 'opponent', 'par')]
```

Notice that damage calculations are constant per move. This is done for simplicity - the default behaviour is that only the average damage amount is used.
This behaviour can be changed by setting a global configuration value.

Obviously, if this is done then the number of instructions generated will become very large even for simple pairs of moves

Looking at 'tackle' vs 'tackle' again:
```python
>> import config
>> config.damage_calc_type = 'all'  # other acceptable values are 'min_max', 'min_max_average', and 'average'

>> from showdown.engine import State
>> from showdown.engine import StateMutator
>> from showdown.engine import get_all_state_instructions

>> state = State(...)  # initialize your state

>> mutator = StateMutator(state)
>> my_move = 'tackle'
>> your_move = 'tackle'

>> transpose_instructions = get_all_state_instructions(mutator, my_move, your_move)

>> len(transpose_instructions)
>> 80  # in this contrived example there are 8 possible damage rolls for one tackle, and 10 for the other
```
