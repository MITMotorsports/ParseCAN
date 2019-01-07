from dataclasses import dataclass, field
from typing import Any

from .. import plural
from .bus import Bus, BusFiltered


def _bus_constr(key, bus):
    try:
        return Bus(name=key, **bus)
    except Exception as e:
        e.args = ('in bus {}: {}'.format(key, e),)

        raise


BusUnique = plural.Unique[Bus].make('BusUnique', ['name'], main='name')
Definition = Any

@dataclass
class Protocol:
    name: str
    definition: Definition  # TODO: Implement this to specialize `Bus`.
    bus: BusUnique = field(default_factory=BusUnique)

    def __post_init__(self):
        bus = self.bus
        self.bus = BusUnique()
        if isinstance(bus, dict):
            bus = [_bus_constr(k, v) for k, v in bus.items()]
        self.bus.extend(bus)

