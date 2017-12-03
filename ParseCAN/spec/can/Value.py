class ValueSpec:
    attributes = ('name', 'range')

    def __init__(self, name, value):
        assert isinstance(value, (tuple, list, int))
        self.name = str(name)
        self._range = tuple(value) if isinstance(value, list) else (value, value)

    def __contains__(self, data):
        if self.is_enum():
            return data >> (data.bit_length() - self._range[0].bit_length()) == self._range[0]

        return self._range[0] <= data <= self._range[1]

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
