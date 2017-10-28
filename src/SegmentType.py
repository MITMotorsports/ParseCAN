from ValueType import ValueType
from CANMessage import CANMessage

class SegmentType:
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
                    self.upsert_valuetype(ValueType(valnm, values[valnm]))
                else:
                    self.upsert_valuetype(values[valnm])

    def get_valuetype(self, val):
        '''
        Given a ValueType return the corresponding
        ValueType in self SegmentType.
        '''
        assert isinstance(val, ValueType)
        return self.values[val.name]

    def upsert_valuetype(self, valtype):
        '''
        Attach, via upsert, a ValueType to self SegmentType.
        '''
        assert isinstance(valtype, ValueType)
        self.values[valtype.name] = valtype

    def interpret(self, message):
        assert isinstance(message, CANMessage)

        data = message[self.position[0]:self.position[1] + 1]
        return (self.data_name(data), data)

    def data_name(self, data):
        '''
        Returns the first contained ValueType in which data is contained.
        '''
        try:
            name = next(value for value in self.values if data in self.values[value])
        except StopIteration:
            # Not found corresponding ValueType
            name = None
        return name

    def __str__(self):
        '''
        A comma separated representation of a SegmentType's values.
        In the same order as SegmentType.attributes.
        '''
        return ', '.join(str(getattr(self, x)) for x in self.attributes)
