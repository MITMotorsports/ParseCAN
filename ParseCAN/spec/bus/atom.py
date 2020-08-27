from dataclasses import dataclass, field
from warnings import warn

from ... import parse
from ...helper import Slice
from .type import Type
from ...data import evil_macros
# from ...data.frame import Frame # circular import with FrameBus

# TODO: Figure out why this breaks dict generation.
# class Unit(str):
#     def pint(self):
#         return parse.ureg[self]
Unit = str

@dataclass
class Atom:
    name: str
    slice: Slice
    type: Type = ''
    unit: Unit = field(default_factory=Unit)

    def __post_init__(self):
        self.slice = Slice.from_general(self.slice)
        if self.slice.start < 0 or self.slice.stop > 64:
            raise ValueError(f'{self.slice} out of bounds')

        # TODO: Get a multiple dispatch here too.
        if isinstance(self.type, str):
            self.type = Type.from_str(self.type)
        elif isinstance(self.type, dict):
            self.type = Type.from_dict(self.type)
        elif not isinstance(self.type, Type):
            raise ValueError('unparseable type: {}'.format(self.type))

        if self.slice.length < self.type.bits():
            if self.type.isenum():  # is annoying for anything other than enum
                raise ValueError(f'have {self.slice.length} and need {self.type.bits()} '
                                 f'bits to represent {self.type}')

        if self.slice.length > self.type.bits():
            warn('slice allocated {0} bits is bigger than type expressed of {1} bits'.format(self.slice.length, self.type.bits()))

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
        # assert isinstance(frame, Frame)

        raw = frame[self.slice.start, self.slice.length]

        if self.type.isenum():
            if not self.type.endianness.isbig():
                corrected = evil_macros.REVERSE_BITS(raw, self.slice.length)
            else:
                corrected = raw
            try:
                retval = self.type.enum['value'][corrected].name
            except KeyError as e:
                e.args = (f'on {self.name} got exception {e.__repr__()}',)
                warn(str(e))
                retval = 'INVALID_ENUM_{}'.format(corrected)

            # REMOVED: now return object in frame
            # if kwargs.get('segtuple', False):
            #     return retval, self

            if kwargs.get('unittuple', False):
                return retval, self.unit

            return retval

        clean = self.type.clean(raw)
        if kwargs.get('segtuple', False):
            return clean, self

        return clean
