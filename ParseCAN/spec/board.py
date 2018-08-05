from dataclasses import dataclass, field
from typing import Any

from .. import spec, plural


@dataclass
class Board:
    name: str
    arch: Any = None
    location: Any = None
    publish: plural.Unique[spec.bus.BusFiltered]
    subscribe: plural.Unique[spec.bus.BusFiltered]

    @property
    def publish(self):
        return self._publish

    @publish.setter
    def publish(self, publish):
        self._publish = plural.Unique('name')

        # TODO: Figure out this weird behavior when argument in init is not given
        if isinstance(publish, property):
            return

        for bus in publish or ():
            self._publish.add(bus)

    @property
    def subscribe(self):
        return self._subscribe

    @subscribe.setter
    def subscribe(self, subscribe):
        self._subscribe = plural.Unique('name')

        # TODO: Figure out this weird behavior when argument in init is not given
        if isinstance(subscribe, property):
            return

        for bus in subscribe or ():
            self._subscribe.add(bus)
