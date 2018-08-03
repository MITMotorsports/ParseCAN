from dataclasses import dataclass


@dataclass
class Enumeration:
    name: str
    value: int

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val
        # TODO: Add awareness of maximum encodeable value based on parent segment.
        if self.value < 0 or self.value > 1.8446744e+19:
            raise ValueError('value out of range: {}'.format(self.value))

    def __contains__(self, data):
        return self.value == data
