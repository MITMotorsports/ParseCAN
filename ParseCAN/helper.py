from dataclasses import dataclass
from typing import Union, NamedTuple


@dataclass(init=False)
class Slice:
    _START_T = Union[int, type(None)]  # TODO: use the field to get the type for fn args

    length: int
    start: _START_T = None

    def __init__(self, *, start: int=None, length: int=None, stop: int=None):
        self.start = start
        self.length = length

        if start is None:
            if length is not None:
                if stop is not None:
                    self.start = stop - length
        else:
            if length is None:
                if stop is not None:
                    self.length = stop - start

        if self.length is None:
            raise ValueError('no length can be inferred from arguments')


    def __len__(self):
        return self.length

    def combinations(self):
        '= 2 ** length = the number of combinations this slice can represent'
        return 2 ** self.length

    @property
    def stop(self):
        'the stop value of the slice with range convention of [start, stop)'
        return self.start + self.length

    @classmethod
    def from_general(cls, val):
        if isinstance(val, str):
            return cls.from_str(val)

        if isinstance(val, slice):
            return cls.from_slice(val)

    @classmethod
    def from_slice(cls, val: slice):
        return cls(start=val.start, stop=val.stop)

    @classmethod
    def from_str(cls, val: str):
        if '+' in val:
            start, length = val.split('+')
            return cls(start=int(start), length=int(length))
        else:
            return cls(length=int(val))

    def slice(self):
        return slice(self.start, self.stop)


def attr_extract(obj, attrs, mapdict=None):
    if mapdict:
        return (mapdict[attr](getattr(obj, attr, None)) for attr in attrs)
    else:
        return (getattr(obj, attr, None) for attr in attrs)


def csv_by_attrs(attrs, mapdict=None):
    def csv(obj):
        return ','.join(map(str, attr_extract(obj, attrs, mapdict)))

    return csv
