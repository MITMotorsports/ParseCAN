from dataclasses import dataclass, field
from typing import Sequence, Union, Mapping

from ... import spec, plural
from .frame import SingleFrame, MultiplexedFrame, FrameUnique, _frame_constr


@dataclass
class Bus:
    name: str
    baudrate: int
    version: str = '2.0B'
    extended: bool = False
    frame: FrameUnique = field(default_factory=FrameUnique)

    def __post_init__(self):
        last_key = 0
        if isinstance(self.frame, dict):
            extend_frame = []
            for k, v in self.frame.items():
                new_key = v['key']
                if(new_key <= last_key):
                    raise Exception(f'Found out of order CAN IDs: {hex(last_key)}, {hex(new_key)}')
                last_key = new_key
                extend_frame.append(_frame_constr(k, v))
            self.frame = FrameUnique()
            self.frame.extend(extend_frame)
        

    def unpack(self, frame, **kwargs):
        return self.frame['key'][frame.id].unpack(frame, **kwargs)
