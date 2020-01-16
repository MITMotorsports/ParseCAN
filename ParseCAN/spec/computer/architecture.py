from dataclasses import dataclass, field
from typing import Any, Set

from ... import plural
from ..protocol import Protocol

@dataclass
class ParticipationCapabilities:
    name: str
    buses: Set[str]

    def __post_init__(self):
        self.buses = set(self.buses)

ParticipationCapabilitiesUnique = plural.Unique[ParticipationCapabilities].make('ParticipationCapabilitiesUnique', ['name'], main='name')


@dataclass
class Architecture:
    name: str
    participation: ParticipationCapabilitiesUnique = field(default_factory=ParticipationCapabilitiesUnique)

    def __post_init__(self):
        self.participation = ParticipationCapabilitiesUnique([
            ParticipationCapabilities(name=key, **value) for key, value in self.participation.items()
        ])
