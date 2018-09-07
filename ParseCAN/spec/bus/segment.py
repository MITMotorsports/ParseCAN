from dataclasses import dataclass
import numpy as np

from ... import data, plural, parse
from ...helper import Slice
from . import Enumeration


class Type:
    def __init__(self, x):
        self.dtype = np.dtype(x)

        if x[0] not in ('>', '<') and self.dtype.byteorder != '|':
            raise TypeError(f'endianness not specified: {x}')


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
