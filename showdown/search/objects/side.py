import constants
from collections import defaultdict
from .pokemon import Pokemon


class Side(object):
    __slots__ = ('active', 'reserve', 'side_conditions', 'trapped')

    def __init__(self, active, reserve, side_conditions, trapped):
        self.active = active
        self.reserve = reserve
        self.side_conditions = side_conditions
        self.trapped = trapped

    @classmethod
    def from_dict(cls, side_dict):
        return Side(
            Pokemon.from_dict(side_dict[constants.ACTIVE]),
            {p[constants.ID]: Pokemon.from_dict(p) for p in side_dict[constants.RESERVE].values()},
            defaultdict(int, side_dict[constants.SIDE_CONDITIONS]),
            side_dict[constants.TRAPPED]
        )

    def __repr__(self):
        return str({
                constants.ACTIVE: self.active,
                constants.RESERVE: self.reserve,
                constants.SIDE_CONDITIONS: dict(self.side_conditions),
                constants.TRAPPED: self.trapped
            })

    def __key(self):
        return (
            hash(self.active),
            sum(hash(p.reserve_hash()) for p in self.reserve.values()),
            hash(frozenset(self.side_conditions.items())),
            self.trapped
        )

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())
