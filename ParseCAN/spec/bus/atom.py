from dataclasses import dataclass, field

from ... import parse
from ...helper import Slice
from .type import Type

# TODO: Figure out why this breaks dict generation.
# class Unit(str):
#     def pint(self):
#         return parse.ureg[self]
Unit = str

@dataclass
class Atom:
    name: str
    slice: Slice
    type: Type
    unit: Unit = field(default_factory=Unit)

    def __post_init__(self):
        self.slice = Slice.from_general(self.slice)

        # TODO: Get a multiple dispatch here too.
        if isinstance(self.type, str):
            self.type = Type.from_str(self.type)

        if isinstance(self.type, dict):
            self.type = Type.from_dict(self.type)

        if self.slice.length > self.type.bits():
            raise ValueError('slice allocated is bigger than type expressed')

    @classmethod
    def from_str(cls, name, string, **kwargs):
        '''
        Constructs an instance from a string of format
        `START + LEN | RAWTYPE | *SCALE | -OFFSET | *UNIT`
        `LEN | RAWTYPE | TYPE | *SCALE | -OFFSET | log10 | exp2 | *UNIT`
        '''
        pipe = string.split('|')
        # TODO: change unit to *unit when you convert it to a list thing
        slice, type, unit = map(str.strip, pipe)

        return cls(name=name, slice=slice, type=type, unit=unit, **kwargs)

    def unpack(self, frame, **kwargs):
        raise NotImplementedError('not updated yet')
