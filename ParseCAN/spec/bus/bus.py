from dataclasses import dataclass, field
from typing import Sequence, Union, Mapping

from ... import spec, plural
from .frame import SingleFrame, FrameCollection, FrameUnique, _frame_constr


@dataclass
class Bus:
    name: str
    baudrate: int
    version: str = '2.0B'
    extended: bool = False
    frame: FrameUnique = field(default_factory=FrameUnique)

    def __post_init__(self):
        frame = self.frame
        self.frame = FrameUnique()

        if isinstance(frame, dict):
            frame = [_frame_constr(k, v) for k, v in frame.items()]

        self.frame.extend(frame)


class BusFiltered(Bus):
    def __init__(self, bus: Bus, interests: Sequence[Union[int, str]]):
        self.bus = bus
        self.interests = interests

    @property
    def interests(self):
        return self._interests

    @interests.setter
    def interests(self, interests):
        for interest in interests:
            try:
                if isinstance(interest, int):
                    self.bus.frame.id[interest]
                elif isinstance(interest, str):
                    self.bus.frame.name[interest]
                else:
                    raise ValueError(f'in bus {self.bus}: '
                                     f'in interest {interest}: '
                                     'must be of type int or str')
            except KeyError:
                raise KeyError(f'in bus {self.bus}: '
                               f'in interest {interest}: '
                               'does not exist in the bus')

        self._interests = interests

    def interested(self, msg):
        assert isinstance(msg, spec.frame)
        return msg.name in self.interests or msg.id in self.interests

    @property
    def frame(self):
        return filter(self.interested, self.bus.frame)

    def __getattr__(self, attr):
        return getattr(self.bus, attr)
