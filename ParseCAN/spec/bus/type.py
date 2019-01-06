from dataclasses import dataclass, field
from typing import NamedTuple
from ... import plural

Enumeration = NamedTuple('Enumeration', [('name', str), ('value', int)])


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


class Endianness(str):
    BIG = 'big'
    LITTLE = 'little'

    @classmethod
    def from_str(cls, string: str):
        if string.lower() == cls.BIG:
            return cls.BIG

        if string.lower() == cls.LITTLE:
            return cls.LITTLE

        raise ValueError('endianness string must be either `big` or `little`')


@dataclass
class Type:
    type: str
    endianness: Endianness
    enumerations: EnumerationUnique = field(default_factory=EnumerationUnique)

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

    def __post_init__(self):
        if self.type not in self.valid_types:
            raise ValueError(f'{self.type} is not a valid type')

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
    def from_str(cls, string: str):
        type, endianness = string.split(' ')
        endianness = Endianness.from_str(endianness)
        return cls(type, endianness)

    def isinteger(self) -> bool:
        return self.type.startswith('int') or self.type.startswith('uint')

    def isenum(self) -> bool:
        return bool(self.enumerations)

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

    def dtype(self):  # -> np.dtype:
        raise NotImplementedError('not updated yet')

        if self.enumerations:
            '''
            Return a unicode string with length equal to the maximum possible
            length of any of the contained value names.
            '''
            return 'U' + str(max(len(val.name) for val in self.enumerations))

        return np_dtypes.get(self.c_type, None)

    def size(self) -> int:
        '''
        Size, in bits, of this type.
        '''
        if self.type == 'bool':
            return 1

        if self.isinteger():
            num = self.type[-2:]
            if not num[0].isdigit():
                return int(num[1])

            return int(num)

    __len__ = size
