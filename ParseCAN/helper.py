from dataclasses import dataclass
from typing import Union, Tuple


@dataclass
class Slice:
    _START_T = Union[int, type(None)]  # use the field to get the type for fn args

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
            str: cls.from_str,
            tuple: cls.from_tuple,
        }[type(val)](val)

    @classmethod
    def from_tuple(cls, val: Tuple[_START_T, int]):
        return cls(*val)

    @classmethod
    def from_slice(cls, val: slice):
        return cls(val.start, val.stop - val.start)

    @classmethod
    def from_str(cls, val: str):
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


def attr_extract(obj, attrs, mapdict=None):
    if mapdict:
        return (mapdict[attr](getattr(obj, attr, None)) for attr in attrs)
    else:
        return (getattr(obj, attr, None) for attr in attrs)


def csv_by_attrs(attrs, mapdict=None):
    def csv(obj):
        return ','.join(map(str, attr_extract(obj, attrs, mapdict)))

    return csv
