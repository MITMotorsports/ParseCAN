from dataclasses import dataclass, field
from typing import Sequence, Union

from ... import spec, plural
from .frame import Frame, FrameCollection, FrameUnique


def _frame_constr(key, frame):
    if isinstance(frame, dict):
        try:
            return Frame(name=key, **frame)
        except Exception as e:
            e.args = ('in frame {}: {}'.format(key, e),)

            raise

    raise ValueError(f'malformed frame representation {key}: {frame}')


@dataclass
class Bus:
    name: str
    baudrate: int
    extended: bool = False
    frames: FrameUnique = field(default_factory=FrameUnique)

    def __post_init__(self):
        frames = self.frames
        self.frames = FrameUnique()

        if isinstance(frames, dict):
            frames = [_frame_constr(k, v) for k, v in frames.items()]

        self.frames.extend(frames)


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
                    self.bus.frames.id[interest]
                elif isinstance(interest, str):
                    self.bus.frames.name[interest]
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
    def frames(self):
        return filter(self.interested, self.bus.frames)

    def __getattr__(self, attr):
        return getattr(self.bus, attr)
