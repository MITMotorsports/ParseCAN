import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set

from .. import plural
from .board import Board
from .bus import Bus, BusFiltered


def _bus_constr(key, bus):
    try:
        return Bus(name=key, **bus)
    except Exception as e:
        e.args = ('in bus {}: {}'.format(key, e),)

        raise


def _board_constr(self, key, board):
    if board.get('publish', None):
        board['publish'] = [BusFiltered(self.buses.name[busnm], board['publish'][busnm]) for busnm in board['publish']]

    if board.get('subscribe', None):
        board['subscribe'] = [BusFiltered(self.buses.name[busnm], board['subscribe'][busnm]) for busnm in board['subscribe']]

    return Board(name=key, **board)


BusUnique = plural.Unique[Bus].make('BusUnique', ['name'])
BoardUnique = plural.Unique[Board].make('BoardUnique', ['name'])


def _board_pre_add(self, board, metadata):
    if board.architecture:
        if board.architecture not in metadata.architectures:
            raise ValueError('unknown architecture in board {}: {}'
                             .format(board.name, board.architecture))


@dataclass
class Car:
    name: str
    architectures: Set[str]
    units: List
    buses: BusUnique = BusUnique()
    boards: BoardUnique = BoardUnique()

    board_ruleset = plural.RuleSet(dict(add=dict(pre=_board_pre_add)))

    def __post_init__(self):
        buses = self.buses
        self.buses = BusUnique()
        if isinstance(buses, dict):
            buses = [_bus_constr(k, v) for k, v in buses.items()]
        self.buses.extend(buses)

        boards = self.boards
        self.boards = BoardUnique()
        self.board_ruleset.apply(self.boards, metadata=self)

        if isinstance(boards, dict):
            boards = [_board_constr(self, k, v) for k, v in boards.items()]
        self.boards.extend(boards)

    @classmethod
    def from_file(cls, filepath):
        filepath = Path(filepath)
        with filepath.open('r') as f:
            prem = yaml.safe_load(f)

        return cls(**prem)

    def unpack(self, frame, **kwargs):
        ret = {}
        # TODO: Make this a comprehension.
        # TODO: Make busFiltered interests receptive to message type objects.
        for bus in self.buses:
            x = bus.messages.id.get(frame.id, None)

            if x:
                ret[bus.name] = {x.name: x.unpack(frame, **kwargs)}

        return ret
