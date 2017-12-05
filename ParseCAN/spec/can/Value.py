class ValueSpec:
    attributes = ('name', 'value')

    def __init__(self, name, value):
        self.name = str(name)
        self.value = int(value)
        if self.value < 0 or self.value > 1.8446744e+19:
            raise ValueError('incorrect value: {}'.format(self.value))

    def __contains__(self, data):
        return self.value == data

    def __str__(self):
        '''
        A comma separated representation of a spec.value's values.
        In the same order as spec.value.attributes.
        '''
        return ', '.join(str(getattr(self, x)) for x in self.attributes)
