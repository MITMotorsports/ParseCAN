class ValueType:
    attributes = ['name', 'range']
    def __init__(self, name, value):
        assert isinstance(value, (tuple, list, int))
        self.name = str(name)
        self.range = tuple(value) if isinstance(value, list) else (value, value)

    def __contains__(self, data):
        return self.range[0] <= data <= self.range[1]

    def __str__(self):
        '''
        A comma separated representation of a ValueType's values.
        In the same order as ValueType.attributes.
        '''
        return ', '.join(str(getattr(self, x)) for x in self.attributes)
