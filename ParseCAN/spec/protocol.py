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


class Protocol:
    name: str
    definition: Definition  # TODO: Implement this to specialize `Bus`.
    buses: BusUnique = field(default_factory=BusUnique)

    def __post_init__(self):
        buses = self.buses
        self.buses = BusUnique()
        if isinstance(buses, dict):
            buses = [_bus_constr(k, v) for k, v in buses.items()]
        self.buses.extend(buses)

