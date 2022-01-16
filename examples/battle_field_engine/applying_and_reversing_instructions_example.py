from showdown.engine import State
from showdown.engine import StateMutator

state = State(...)  # initialize your state

state.self.active.hp = 100
print(state.self.active.hp)  # prints '100'

mutator = StateMutator(state)

instructions = [
    ('damage', 'self', 1)
]

mutator.apply(instructions)
print(state.self.active.hp)  # prints '99'

mutator.reverse(instructions)
print(state.self.active.hp)  # prints '100'