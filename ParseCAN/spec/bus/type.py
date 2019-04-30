from dataclasses import dataclass, field
from enum import Enum
import numpy as np

from ... import plural, data


@dataclass
class Enumerator:
    name: str
    value: int

def _enumerator_pre_add(self, item):
    # TODO: Change when support C++11 enum with type.
    # if item.value not in self.type.range():
    #     raise ValueError(f'enumerator\'s value too large for {self.type}')
    pass


def _enumerator_post_add(self, item):
    if len(self) > len(self.type.range()):
        raise ValueError(f'too many enumerators for {self.type}')


def _enumerator_constr(key, enumerator):
    if isinstance(enumerator, int):
        try:
            return Enumerator(key, enumerator)
        except Exception as e:
            e.args = ('in enumerator {}: {}'.format(key, e),)

            raise
    elif isinstance(enumerator, Enumerator):
        return enumerator
    else:
        raise TypeError('enumerator given is not int or Enumerator')


EnumeratorUnique = plural.Unique[Enumerator].make('EnumeratorUnique',
                                                    ['name', 'value'],
                                                    main='name')

_enumerator_ruleset = plural.RuleSet(dict(add=dict(pre=_enumerator_pre_add,
                                                    post=_enumerator_post_add)))
_enumerator_ruleset.apply(EnumeratorUnique)


class Endianness(Enum):
    BIG = 'big'
    LITTLE = 'little'

    def isbig(self):
        return self == self.BIG

    def islittle(self):
        return self == self.LITTLE


@dataclass
class Type:
    endianness: Endianness
    type: str = ''
    enum: EnumeratorUnique = field(default_factory=EnumeratorUnique)

    valid_types = {
        'bool',
        'int8',
        'uint8',
        'int16',
        'uint16',
        'int32',
        'uint32',
        'int64',
        'uint64',
    }

    casts = {
        'bool': lambda x, **kw: bool(x),
        'int8': data.evil_macros.cast_gen('b'),
        'uint8': data.evil_macros.cast_gen('B'),
        'int16': data.evil_macros.cast_gen('h'),
        'uint16': data.evil_macros.cast_gen('H'),
        'int32': data.evil_macros.cast_gen('i'),
        'uint32': data.evil_macros.cast_gen('I'),
        'int64': data.evil_macros.cast_gen('q'),
        'uint64': data.evil_macros.cast_gen('Q'),
    }

    def __post_init__(self):
        enum = self.enum
        self.enum = EnumeratorUnique()
        self.enum.type = self

        if isinstance(enum, (list, tuple)):
            # implicitly assign values to enumerators elements given as a list
            enum = {key: idx for idx, key in enumerate(enum)}
            # make the dictionary and fall through to the list creation

        if isinstance(enum, dict):
            enum = [_enumerator_constr(k, v) for k, v in enum.items()]

        self.enum.extend(enum)

        if not self.enum:  # TODO: Change when support C++11 enum with type.
            if self.type not in self.valid_types:
                raise ValueError('given type is not a recognized typename')

        if not isinstance(self.endianness, Endianness):
            self.endianness = Endianness(self.endianness)


    @classmethod
    def from_str(cls, string: str):
        try:
            type, endianness = string.split(' ')
        except ValueError:
            raise ValueError(f'endianess missing from type string {string}')

        endianness = Endianness(endianness)
        return cls(type=type, endianness=endianness)

    @classmethod
    def from_dict(cls, dictionary: dict):
        if 'endianness' not in dictionary:
            raise ValueError('endianness must be explicit in dict form')
        return cls(**dictionary)

    def isinteger(self) -> bool:
        return self.type.startswith('int') or self.type.startswith('uint')

    def isbool(self) -> bool:
        return self.type == 'bool'

    def isenum(self) -> bool:
        return bool(self.enum)

    def issigned(self) -> bool:
        if self.type.startswith('int'):
            return True

        if self.type.startswith('uint'):
            return False

        return None

    def ctype(self) -> str:
        if 'int' in self.type:
            return self.type + '_t'

        return self.type

    def dtype(self): # -> np.dtype:
        if self.isenum():
            '''
            Return a unicode string with length equal to the maximum possible
            length of any of the contained value names.
            '''
            return 'U' + str(max(len(val.name) for val in self.enum))

        return self.type

    def bits(self) -> int:
        '''Size, in bits, of this type.'''
        if self.isenum():
            maxval = max(enum.value for enum in self.enum)

            return maxval.bit_length()

        if self.type == 'bool':
            return 1

        if self.isinteger():
            num = self.type[-2:]
            if not num[0].isdigit():
                return int(num[1])

            return int(num)

    __len__ = bits

    def range(self):
        '''
        Returns a range object with the full integer
        interpreted range this type can represent.

        Assumes two's complement low level implementation.
        '''

        start = 0
        stop = 2 ** self.bits()  # no -1 since python range is [,)

        if self.isinteger():
            if self.issigned():
                start = -stop >> 1
                stop = stop >> 1

        return range(start, stop)

    def clean(self, raw):
        return self.casts[self.type](raw, endianness='big' if self.endianness.isbig() else 'little')
