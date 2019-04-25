from dataclasses import dataclass, field
from typing import Sequence, Union, Mapping

from ... import spec, plural
from .frame import SingleFrame, MultiplexedFrame, FrameUnique, _frame_constr


@dataclass
class Bus:
    name: str
    id: int
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

    def unpack(self, frame, **kwargs):
        return self.frame['key'][frame.id].unpack(frame, **kwargs)
