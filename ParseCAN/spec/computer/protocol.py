from typing import Any, Dict
from dataclasses import dataclass, field

from ..bus import Bus, Frame
from ..protocol import BusUnique

Controller = Any  # Whatever controller type the generator will use


class ControllerMapping(Dict[str, Controller]):
    pass


class PubSub(Dict[str, Any]):  # TODO: Make it Dict[Bus, Set[Frame]]?
    pass


@dataclass
class Participation:
    bus: BusUnique
    mapping: ControllerMapping = field(default_factory=ControllerMapping)
    publish: PubSub = field(default_factory=PubSub)
    subscribe: PubSub = field(default_factory=PubSub)

    def validate_busdict(self, busdict):
        for busnm in busdict:
            if busnm not in self.bus['name']:
                raise ValueError(f'bus {busnm} does not exist')

        return True

    def validate_pubsub(self, pubsub):
        self.validate_busdict(pubsub)
        for busnm, frames in pubsub.items():
            for framenm in frames:
                if framenm not in self.bus['name'][busnm].frame['name']:
                    raise ValueError(f'frame {framenm} does not exist in bus {busnm}')


    def __post_init__(self):
        self.validate_busdict(self.mapping)
        self.validate_pubsub(self.publish)
        self.validate_pubsub(self.subscribe)

