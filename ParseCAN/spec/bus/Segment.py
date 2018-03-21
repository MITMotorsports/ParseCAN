from ... import spec, data, plural


class SegmentType:
    '''
    A specification for a segment of a larger data string.
    '''

    attributes = ('name', 'c_type', 'unit', 'position', 'length', 'signed', 'values')

    def __init__(self, name, c_type='', unit='', position=None, length=None, signed=False, enum=None):
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
        self.__values = plural.unique('name', 'value', type=spec.value)
        # values synonymous to enum

        if enum:
            if isinstance(enum, list):
                enum = {valnm: idx for idx, valnm in enumerate(enum)}

            for valnm in enum:
                if isinstance(enum[valnm], int):
                    try:
                        self.values.safe_add(spec.value(valnm, enum[valnm]))
                    except Exception as e:
                        e.args = (
                            'in value {}: {}'
                            .format(
                                valnm,
                                e
                            ),
                        )

                        raise

                elif isinstance(enum[valnm], spec.value):
                    self.safe_add(enum[valnm])
                else:
                    raise TypeError('value given is not int or spec.value')

    @property
    def values(self):
        return self.__values

    def unpack(self, frame):
        assert isinstance(frame, data.message)
        # raw = str(message[self.position:(self.position + self.length)]) + self.unit
        # TODO: Move this to data.message.__getitem__
        raw = data.EXTRACT(frame.data, self.position, self.length)

        if self.values:
            return self.values.value[raw]

        # TODO: Deal with two's complement signed numbers.
        def c_to_py(val):
            t = {
                'bool': bool
            }

            if 'int' in self.c_type:
                return int(val)

            return t[self.c_type](val)

        clean = c_to_py(raw)

        return (clean, self.unit) if self.unit else clean

    def __str__(self):
        '''
        A comma separated representation of a spec.segment's values.
        In the same order as spec.segment.attributes.
        '''
        return ', '.join(str(getattr(self, x)) for x in self.attributes)
