from dataclasses import dataclass
from typing import Union, Tuple
import numpy as np

from ... import data, plural, parse
from . import Enumeration


class Type:
    def __init__(self, x):
        self.dtype = np.dtype(x)

        if x[0] not in ('>', '<') and self.dtype.byteorder != '|':
            raise ValueError('endianness not specified: {}'.format(x))


@dataclass
class Slice:
    _START_T = Union[int, type(None)]

    start: _START_T
    length: int

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, val=None):
        if val is None:
            raise NotImplementedError('unable to handle implicit start yet')
        else:
            self._start = int(val)
            if self.start not in range(0, 65):
                raise ValueError('start out of bounds: {}'.format(self.start))

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, val):
        self._length = int(val)
        if self.length < 1:
            raise ValueError('length too small: {}'.format(self.length))
        if self.start + self.length > 64:
            raise ValueError('length overflows: {}'.format(self.length))

    @classmethod
    def from_general(cls, val):
        return {
            cls: lambda val: val.copy(),
            slice: cls.from_slice,
            str: cls.from_string,
            tuple: cls.from_tuple,
        }[type(val)](val)

    @classmethod
    def from_tuple(cls, val: Tuple[_START_T, int]):
        return cls(*val)

    @classmethod
    def from_slice(cls, val: slice):
        return cls(val.start, val.stop - val.start)

    @classmethod
    def from_string(cls, val: str):
        if '+' in val:
            return cls(*val.split('+'))
        else:
            return cls(length=int(val))

    def copy(self):
        return Slice(start=self.start, length=self.length)


@dataclass
class Segment:
    '''
    A specification for a segment of a larger data string.
    '''

    name: str
    type: Type
    slice: Slice
    unit: str = ''
    enumerations: plural.Unique[Enumeration]

    def __post_init__(self):
        self.slice = Slice.from_general(self.slice)

    @classmethod
    def from_string(cls, name, string, **kwargs):
        '''
        Constructs an instance from a string of format
        `START + LEN | RAWTYPE | *SCALE | -OFFSET | *UNIT`
        `LEN | RAWTYPE | TYPE | *SCALE | -OFFSET | log10 | exp2 | *UNIT`
        '''
        pipe = string.split('|')
        pipe = list(map(str.strip, pipe))
        return cls(name, slice=pipe[0], type=pipe[1],
                   unit='|'.join(pipe[2:]), **kwargs)

    @property
    def enumerations(self):
        return self._enumerations

    @enumerations.setter
    def enumerations(self, enumerations):
        if isinstance(enumerations, plural.Unique):
            self._segments = enumerations.copy()
            # TODO: Make checks happen here too
            return

        self._enumerations = plural.Unique('name', 'value')

        if isinstance(enumerations, list):
            self._enumerations.extend(enumerations)
            return

        # TODO: Figure out this weird behavior when argument in init is not given
        if isinstance(enumerations, property):
            return

        if isinstance(enumerations, list):
            # implicitly assign values to enumerations elements given as a list
            enumerations = {key: idx for idx, key in enumerate(enumerations)}

        for key in enumerations or ():
            if isinstance(enumerations[key], int):
                try:
                    self.enumerations.safe_add(Enumeration(key, enumerations[key]))
                except Exception as e:
                    e.args = (
                        'in enumeration {}: {}'
                        .format(
                            key,
                            e
                        ),
                    )

                    raise
            elif isinstance(enumerations[key], Enumeration):
                self.enumerations.safe_add(enumerations[key])
            else:
                raise TypeError('enumerations given is not int or Enumeration')

    @property
    def pint_unit(self):
        return parse.ureg[self.unit]

    @property
    def np_dtype(self):
        if self.values:
            '''
            Return a unicode string with length equal to the maximum possible
            length of any of the contained value names.
            '''
            return 'U' + str(max(len(val.name) for val in self.values))

        return np_dtypes.get(self.c_type, None)

    def unpack(self, frame, **kwargs):
        assert isinstance(frame, data.Frame)

        raw = frame[self.start, self.length]

        if self.values:
            retval = self.values.value[raw].name

            if kwargs.get('segtuple', False):
                return retval, self

            if kwargs.get('unittuple', False):
                return retval, None

            return retval

        clean = casts[self.c_type](raw, endianness='big' if self.is_big_endian else 'little')

        if kwargs.get('segtuple', False):
            return clean, self

        if kwargs.get('unittuple', False):
            return clean, self.unit

        if self.unit and not kwargs.get('raw', False):
            return parse.number(clean, self.unit)

        return clean


np_dtypes = {
    'bool': 'bool',
    'int8_t': 'int8',
    'uint8_t': 'uint8',
    'int16_t': 'int16',
    'uint16_t': 'uint16',
    'int32_t': 'int32',
    'uint32_t': 'uint32',
    'int64_t': 'int64',
    'uint64_t': 'uint64',
}

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
