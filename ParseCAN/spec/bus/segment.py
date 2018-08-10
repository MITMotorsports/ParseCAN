from dataclasses import dataclass, field
from typing import Union, Tuple
import numpy as np

from ... import data, plural, parse
from . import Enumeration


class Type:
    def __init__(self, x):
        self.dtype = np.dtype(x)

        if x[0] not in ('>', '<') and self.dtype.byteorder != '|':
            raise TypeError(f'endianness not specified: {x}')


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
                raise ValueError(f'start out of bounds: {self.start}')

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, val):
        self._length = int(val)
        if self.length < 1:
            raise ValueError(f'length too small: {self.length}')
        if self.start + self.length > 64:
            raise ValueError(f'length overflows: {self.start} + {self.length}')

    @property
    def size(self):
        '= 2 ** length = the number of combinations this slice can represent'
        return 1 << self.length

    @property
    def stop(self):
        'the stop value of the slice (inclusive)'
        return self.start + self.length - 1

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

    def __iter__(self):
        return iter((self.start, self.length))

    def __slice__(self):
        return slice(self.start, self.start + self.length)


def _enumeration_pre_add(self, item):
    # This was also ensured through Enumeration.max_value and the
    # value uniqueness predicate, but this is a clearer error message.

    slice = self.segment.slice
    max_len = slice.size
    if len(self) + 1 > max_len:
        raise ValueError(f'too many enumerations for segment of length {slice.length}')

    # enforce the max value
    item.max_value = slice.size - 1  # zero-based enumeration
    item.check()


def _enumeration_constr(key, enumeration):
    if isinstance(enumeration, int):
        try:
            return Enumeration(key, enumeration)
        except Exception as e:
            e.args = ('in enumeration {}: {}'.format(key, e),)

            raise
    elif isinstance(enumeration, Enumeration):
        return enumeration
    else:
        raise TypeError('enumeration given is not int or Enumeration')


EnumerationUnique = plural.Unique[Enumeration].make('EnumerationUnique',
                                                    ['name', 'value'],
                                                    main='name')

_enumeration_ruleset = plural.RuleSet(dict(add=dict(pre=_enumeration_pre_add)))
_enumeration_ruleset.apply(EnumerationUnique)


@dataclass
class Segment:
    name: str
    slice: Slice
    type: Type = ''
    unit: str = ''
    enumerations: EnumerationUnique = tuple()  # = field(default_factory=EnumerationUnique)

    def __post_init__(self):
        self.slice = Slice.from_general(self.slice)

        enumerations = self.enumerations
        self.enumerations = EnumerationUnique()
        self.enumerations.segment = self

        if isinstance(enumerations, (list, tuple)):
            # implicitly assign values to enumerations elements given as a list
            enumerations = {key: idx for idx, key in enumerate(enumerations)}
            # make the dictionary and fall through to the list creation

        if isinstance(enumerations, dict):
            enumerations = [_enumeration_constr(k, v) for k, v in enumerations.items()]

        self.enumerations.extend(enumerations)

    @classmethod
    def from_string(cls, name, string, **kwargs):
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

    @property
    def np_dtype(self):
        if self.enumerations:
            '''
            Return a unicode string with length equal to the maximum possible
            length of any of the contained value names.
            '''
            return 'U' + str(max(len(val.name) for val in self.enumerations))

        return np_dtypes.get(self.c_type, None)

    def unpack(self, frame, **kwargs):
        raise NotImplementedError('not updated yet')

        raw = frame[self.start, self.length]

        if self.enumerations:
            retval = self.enumerations.value[raw].name

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
