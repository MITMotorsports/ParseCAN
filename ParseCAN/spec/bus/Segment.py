from ... import spec, data, plural, parse, helper
import numpy as np


def segtype(x):
    if x == 'enum':
        return x

    dtype = np.dtype(x)
    if x[0] not in ('>', '<') and dtype.byteorder != '|':
        raise ValueError('endianness not specified: {}'.format(x))

    return dtype


class SegmentType:
    '''
    A specification for a segment of a larger data string.
    '''

    def __init__(self, name, type='', unit='', position=None, length=None, enum=None):
        self.name = str(name)
        self.type = segtype(type)
        self.unit = str(unit)
        self.position = int(position)
        if self.position not in range(0, 65):
            raise ValueError('position out of bounds: {}'.format(self.position))

        self.length = int(length)
        if self.length < 1:
            raise ValueError('length too small: {}'.format(self.length))
        if self.position + self.length > 64:
            raise ValueError('length overflows: {}'.format(self.length))

        # values synonymous to enum
        self.values = enum

    @classmethod
    def from_string(cls, string):
        '''
        Constructs an instance from a string of format
        `START to STOP as TYPE in UNIT`
        `START + LEN | TYPE | *SCALE | -OFFSET | *UNIT`
        `START : STOP | TYPE | *SCALE | -OFFSET | log10 | exp2 | *UNIT`
        '''
        raise NotImplementedError

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, values):
        self._values = plural.unique('name', 'value', type=spec.value)

        if isinstance(values, list):
            # implicitly assign values to enum elements given as a list
            values = {valnm: idx for idx, valnm in enumerate(values)}

        for valnm in values or ():
            if isinstance(values[valnm], int):
                try:
                    self.values.safe_add(spec.value(valnm, values[valnm]))
                except Exception as e:
                    e.args = (
                        'in value {}: {}'
                        .format(
                            valnm,
                            e
                        ),
                    )

                    raise

            elif isinstance(values[valnm], spec.value):
                self.safe_add(values[valnm])
            else:
                raise TypeError('value given is not int or spec.value')

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

        raw = frame[self.position, self.length]

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

    __str__ = helper.csv_by_attrs(('name', 'c_type', 'unit', 'position', 'length', 'signed', 'values'))


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
