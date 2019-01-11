from dataclasses import dataclass, field
from typing import Any, Dict

from ..protocol import Protocol
from .protocol import Participation


@dataclass
class Computer:
    name: str
    architecture: str
    location: Any = None
    # protocol: Dict[Protocol, Participation] = field(default_factory=dict)  # once everything is hashable can do that
    protocol: Dict[str, Participation] = field(default_factory=dict)
