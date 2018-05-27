from ... import spec, data, plural, parse, helper


class SegmentType:
    '''
    A specification for a segment of a larger data string.
    '''

    def __init__(self, name, c_type='', unit='', position=None, length=None, signed=False, is_big_endian=True, enum=None):
        self.name = str(name)
        self.c_type = str(c_type)
        self.unit = str(unit)
        self.position = int(position)
        if self.position < 0 or self.position > 64:
            raise ValueError('incorrect position: {}'.format(self.position))

        self.length = int(length)
        if self.length < 1:
            raise ValueError('length too small: {}'.format(self.length))
        if self.position + self.length > 64:
            raise ValueError('length overflows: {}'.format(self.length))

        self.signed = bool(signed)
        self.is_big_endian = bool(is_big_endian)

        # values synonymous to enum
        self.values = enum

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

    def unpack(self, frame, **kwargs):
        assert isinstance(frame, data.Frame)

        raw = frame[self.position, self.length]

        def parsenum(type):
            return data.evil_macros.cast_gen(type, reverse=not self.is_big_endian)

        if self.values:
            retval = self.values.value[raw].name

            if kwargs.get('unittuple', False):
                return (retval, '')

            return retval

        def c_to_py(val):
            return {
                'bool': bool,
                'int8_t': parsenum('b'),
                'uint8_t': parsenum('B'),
                'int16_t': parsenum('h'),
                'uint16_t': parsenum('H'),
                'int32_t': parsenum('i'),
                'uint32_t': parsenum('I'),
                'int64_t': parsenum('q'),
                'uint64_t': parsenum('Q'),
            }[self.c_type](val)

        clean = c_to_py(raw)

        if kwargs.get('unittuple', False):
            return clean, self.unit

        if self.unit and not kwargs.get('raw', False):
            return parse.number(clean, self.unit)

        return clean

    __str__ = helper.csv_by_attrs(('name', 'c_type', 'unit', 'position', 'length', 'signed', 'values'))
