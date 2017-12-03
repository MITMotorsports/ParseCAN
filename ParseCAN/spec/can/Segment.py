from ... import spec, data


class SegmentSpec:
    '''
    A specification for a segment of a larger data string.
    '''

    attributes = ('name', 'c_type', 'position', 'length', 'signed', 'values')

    def __init__(self, name, c_type='', unit='', position=None, length=None, signed=False , enum=None):
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
        self.values = {}
        # values synonymous to enum

        if enum:
            for valnm in enum:
                if isinstance(enum[valnm], int):
                    try:
                        self.upsert_value(spec.value(valnm, enum[valnm]))
                    except Exception as e:
                        raise ValueError(
                            'in value {}: {}'
                            .format(
                                valnm,
                                e
                            )
                        )
                elif isinstance(enum[valnm], spec.value):
                    self.upsert_value(enum[valnm])

    def get_value(self, val):
        '''
        Given a spec.value return the corresponding
        spec.value in this spec.segment.
        '''
        assert isinstance(val, spec.value)
        return self.values[val.name]

    def upsert_value(self, valtype):
        '''
        Attach, via upsert, a spec.value to this segment spec.
        '''
        assert isinstance(valtype, spec.value)
        self.values[valtype.name] = valtype

    def interpret(self, message):
        assert isinstance(message, data.message)
        msgdata = str(message[self.position:(self.position + self.length)]) + self.unit

        if self.values:
            return (self.data_name(msgdata), msgdata)

        return msgdata

    def data_name(self, data):
        '''
        Returns the first contained spec.value in which data is contained.
        '''
        incl = (value for value in self.values if data in self.values[value])
        return next(incl, None)

    def __str__(self):
        '''
        A comma separated representation of a spec.segment's values.
        In the same order as spec.segment.attributes.
        '''
        return ', '.join(str(getattr(self, x)) for x in self.attributes)
