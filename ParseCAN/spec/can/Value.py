class ValueSpec:
    attributes = ('name', 'range')

    def __init__(self, name, value):
        self.name = str(name)
        self.value = int(value)
        if self.value < 0:
            raise ValueError('incorrect value: {}'.format(self.value))

    def __contains__(self, data):
        return self.value == data

    def __str__(self):
        '''
        A comma separated representation of a spec.value's values.
        In the same order as spec.value.attributes.
        '''
        return ', '.join(str(getattr(self, x)) for x in self.attributes)

    def is_enum(self):
        '''
        Returns true if this spec.value is not a range.
        '''
        return self._range[0] == self._range[1]
