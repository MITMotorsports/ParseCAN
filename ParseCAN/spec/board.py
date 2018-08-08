from dataclasses import dataclass
from typing import Any

from .. import plural
from .bus import BusFiltered


BusFilteredUnique = plural.Unique[BusFiltered].make('BusFilteredUnique', ['name'])


@dataclass
class Board:
    name: str
    arch: Any = None
    location: Any = None
    publish: BusFilteredUnique = BusFilteredUnique()
    subscribe: BusFilteredUnique = BusFilteredUnique()

    def __post_init__(self):
        pass
