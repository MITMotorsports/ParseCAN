from dataclasses import dataclass, field
from ... import plural

@dataclass
class Enumeration:
    name: str
    value: int

def _enumeration_pre_add(self, item):
    if item.value not in self.type.range():
        raise ValueError(f'enumerations value too large for {self.type}')


def _enumeration_post_add(self, item):
    if len(self) > len(self.type.range()):
        raise ValueError(f'too many enumerations for {self.type}')


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

_enumeration_ruleset = plural.RuleSet(dict(add=dict(pre=_enumeration_pre_add,
                                                    post=_enumeration_post_add)))
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
        'enum',  # TODO: Consider if this is good
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
        self.enumerations.type = self

        if isinstance(enumerations, (list, tuple)):
            # implicitly assign values to enumerations elements given as a list
            enumerations = {key: idx for idx, key in enumerate(enumerations)}
            # make the dictionary and fall through to the list creation

        if isinstance(enumerations, dict):
            enumerations = [_enumeration_constr(k, v) for k, v in enumerations.items()]

        self.enumerations.extend(enumerations)

    @classmethod
    def from_str(cls, string: str):
        try:
            type, endianness = string.split(' ')
        except ValueError:
            raise ValueError(f'endianess missing from type string {string}')

        endianness = Endianness.from_str(endianness)
        return cls(type, endianness)

    @classmethod
    def from_dict(cls, dictionary: dict):
        type = dictionary.get('type', 'enum')
        if 'endianess' in dictionary:
            endianness = Endianness.from_str(dictionary['endianess'])
        else:
            raise ValueError('endianness must be explicit in dict form')
        enumerations = dictionary.get('enum', None)
        return cls(type, endianness, enumerations)

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

    def range(self):
        '''
        Returns a range object with the full integer
        interpreted range this type can represent.

        Assumes two's complement low level implementation.
        '''

        start = 0
        stop = 1 << self.size()  # no -1 since python range is [,)

        if self.isinteger():
            if self.issigned():
                start = -stop >> 1
                stop = stop >> 1

        return range(start, stop)
