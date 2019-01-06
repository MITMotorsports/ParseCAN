from dataclasses import dataclass, field

from ... import data, parse
from ...helper import Slice
from .type import Type


# TODO: Specify a forbidden region (claiomed by multiplex).

@dataclass
class Atom:
    name: str
    slice: Slice
    type: Type
    unit: str = ''

    def __post_init__(self):
        self.slice = Slice.from_general(self.slice)

        if not isinstance(self.type, Type):
            self.type = Type.from_str(self.type)

    @classmethod
    def from_str(cls, name, string, **kwargs):
        '''
        Constructs an instance from a string of format
        `START + LEN | RAWTYPE | *SCALE | -OFFSET | *UNIT`
        `LEN | RAWTYPE | TYPE | *SCALE | -OFFSET | log10 | exp2 | *UNIT`
        '''
        pipe = string.split('|')
        slice, type, *unit = map(str.strip, pipe)

        return cls(name=name, slice=slice, type=type, unit=unit, **kwargs)

    @property
    def pint_unit(self):
        return parse.ureg[self.unit]

    def unpack(self, frame, **kwargs):
        raise NotImplementedError('not updated yet')


casts = {
    'bool': lambda x, **kw: bool(x),
    'int8_t': data.evil_macros.cast_gen('b'),
    'uint8_t': data.evil_macros.cast_gen('B'),
    'int16_t': data.evil_macros.cast_gen('h'),
    'uint16_t': data.evil_macros.cast_gen('H'),
    'int32_t': data.evil_macros.cast_gen('i'),
    'uint32_t': data.evil_macros.cast_gen('I'),
    'int64_t': data.evil_macros.cast_gen('q'),
    'uint64_t': data.evil_macros.cast_gen('Q'),
}
