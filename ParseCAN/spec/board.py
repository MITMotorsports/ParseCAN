from dataclasses import dataclass, field
from typing import Any

from .. import plural
from .bus import BusFiltered


BusFilteredUnique = plural.Unique[BusFiltered].make('BusFilteredUnique',
                                                    ['name'],
                                                    main='name')


@dataclass
class Board:
    name: str
    architecture: str
    location: Any = None
    publish: BusFilteredUnique = field(default_factory=BusFilteredUnique)
    subscribe: BusFilteredUnique = field(default_factory=BusFilteredUnique)

    def __post_init__(self):
        pass
