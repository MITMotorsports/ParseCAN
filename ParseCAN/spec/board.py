from dataclasses import dataclass
from typing import Any

from .. import plural
from .bus import BusFiltered


@dataclass
class Board:
    name: str
    arch: Any = None
    location: Any = None
    publish: plural.Unique[BusFiltered] = plural.Unique('name')
    subscribe: plural.Unique[BusFiltered] = plural.Unique('name')

    def __post_init__(self):
        pass
