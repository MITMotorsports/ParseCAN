from dataclasses import dataclass, field
from typing import Any, Dict

from ... import plural
from ..protocol import Protocol
from .participation import Participation


ParticipationUnique = plural.Unique[Participation].make('ParticipationUnique', ['name'], main='name')


@dataclass
class Computer:
    name: str
    architecture: str
    location: Any = None
    # protocol: Dict[Protocol, Participation] = field(default_factory=dict)  # once everything is hashable can do that
    participation: ParticipationUnique = field(default_factory=ParticipationUnique)

    def __post_init__(self):
        print(self.participation)
        self.participation = ParticipationUnique(self.participation)
