from ParseCAN import spec, meta


class SegmentSpec:
    '''
    A specification for a segment of a larger data string.
    '''

    attributes = ('name', 'c_type', 'position', 'values')

    def __init__(self, name, c_type, unit, position, values=None):
        self.name = str(name)
        self.c_type = str(c_type)
        self.unit = str(unit)
        self.position = tuple(position)
        self.values = {}

        if values:
            for valnm in values:
                if isinstance(values[valnm], (int, list)):
                    self.upsert_value(spec.value(valnm, values[valnm]))
                else:
                    self.upsert_value(values[valnm])

    def get_value(self, val):
        '''
        Given a spec.value return the corresponding
        spec.value in self SegmentSpec.
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
        assert isinstance(message, meta.message)

        data = message[self.position[0]:self.position[1] + 1]
        return (self.data_name(data), data)

    def data_name(self, data):
        '''
        Returns the first contained spec.value in which data is contained.
        '''
        try:
            name = next(value for value in self.values if data in self.values[value])
        except StopIteration:
            # Not found corresponding spec.value
            name = None
        return name

    def __str__(self):
        '''
        A comma separated representation of a SegmentSpec's values.
        In the same order as SegmentSpec.attributes.
        '''
        return ', '.join(str(getattr(self, x)) for x in self.attributes)
