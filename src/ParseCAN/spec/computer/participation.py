from typing import Any, Dict, List
from dataclasses import dataclass, field

from ..bus import Bus, Frame
from ..protocol import Protocol

Controller = Any  # Whatever controller type the generator will use


class ControllerMapping(Dict[str, Controller]):
    pass


class PubSub(Dict[str, List[Frame]]):  # TODO: Make it Dict[Bus, Set[Frame]]?
    pass


@dataclass
class Participation:
    name: str
    protocol: Protocol
    mapping: ControllerMapping = field(default_factory=ControllerMapping)
    publish: PubSub = field(default_factory=PubSub)
    subscribe: PubSub = field(default_factory=PubSub)

    def validate_busdict(self, busdict):
        for busnm in busdict:
            if busnm not in self.protocol.bus['name']:
                raise ValueError(f'bus {busnm} does not exist')

        return True

    def validate_pubsub(self, pubsub):
        self.validate_busdict(pubsub)

        framedict = {}
        for busnm, frames in pubsub.items():
            for framenm in set(frames):  # TODO: maybe warn about duplicates
                if framenm not in self.protocol.bus['name'][busnm].frame['name']:
                    raise ValueError(f'frame {framenm} does not exist in bus {busnm}')

                frame = self.protocol.bus['name'][busnm].frame['name'][framenm]
                if busnm in framedict:
                    framedict[busnm].append(frame)
                else:
                    framedict[busnm] = [frame]

        return framedict


    def __post_init__(self):
        self.validate_busdict(self.mapping)
        self.publish = self.validate_pubsub(self.publish)
        self.subscribe = self.validate_pubsub(self.subscribe)

