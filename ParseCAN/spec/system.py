import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set

from .. import plural
from .protocol import Protocol
from .board import Board

def _board_constr(key, board):
    try:
        return Board(name=key, **board)
    except Exception as e:
        e.args = ('in board {}: {}'.format(key, e),)

        raise

BoardUnique = plural.Unique[Board].make('BoardUnique', ['name'], main='name')

def _board_pre_add(self, board, metadata):
    if board.architecture:
        if board.architecture not in metadata.architectures:
            raise ValueError(f'in board {board.name}: '
                             f'unknown architecture: {board.architecture}')

_board_ruleset = plural.RuleSet(dict(add=dict(pre=_board_pre_add)))


ProtocolUnique = plural.Unique[Protocol].make('ProtocolUnique', ['name'], main='name')


@dataclass
class System:
    name: str
    architectures: Set[str]
    units: Set[str]
    board: BoardUnique = field(default_factory=BoardUnique)
    protocol: ProtocolUnique = field(default_factory=ProtocolUnique)

    def __post_init__(self):
        board = self.board
        self.board = BoardUnique()
        _board_ruleset.apply(self.board, metadata=self)

        if isinstance(board, dict):
            board = (_board_constr(key, board) for key, board in self.board.items())
        self.board.extend(board)

    @classmethod
    def from_yaml(cls, stream):
        spec = yaml.safe_load(stream)
        del spec['board']
        return cls(**spec)
