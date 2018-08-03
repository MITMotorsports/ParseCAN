from ... import helper

class Enum:
    def __init__(self, name, value):
        self.name = str(name)
        self.value = int(value)

        # TODO: Add awareness of maximum encodeable value based on parent segment.
        if self.value < 0 or self.value > 1.8446744e+19:
            raise ValueError('incorrect value: {}'.format(self.value))

    def __contains__(self, data):
        return self.value == data

    __str__ = helper.csv_by_attrs(('name', 'value'))
