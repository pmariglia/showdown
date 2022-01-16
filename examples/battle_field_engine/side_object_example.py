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