from dataclasses import dataclass, field
from typing import Any, Dict

from .. import plural
from . import Bus


Controller = Any  # Whatever controller type the generator will use

class BusMapping(Dict[Bus, Controller]):
    pass


@dataclass
class BusMember:
    publish: Any = field(default_factory=list)
    subscribe: Any = field(default_factory=list)


@dataclass
class Computer:
    name: str
    architecture: str
    protocol: Any = 1
    location: Any = None
    publish: Any = field(default_factory=list)
    subscribe: Any = field(default_factory=list)
