class ValueSpec:
    attributes = ('name', 'range')

    def __init__(self, name, value):
        assert isinstance(value, (tuple, list, int))
        self.name = str(name)
        self.range = tuple(value) if isinstance(value, list) else (value, value)

    def __contains__(self, data):
        return self.range[0] <= data <= self.range[1]

    def __str__(self):
        '''
        A comma separated representation of a spec.value's values.
        In the same order as spec.value.attributes.
        '''
        return ', '.join(str(getattr(self, x)) for x in self.attributes)
