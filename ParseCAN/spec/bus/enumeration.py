from dataclasses import dataclass, field


@dataclass
class Enumeration:
    name: str
    value: int
    max_value: int = field(repr=False, compare=False, hash=False, default=2 ** 64)

    def __post_init__(self):
        self.value = self.value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val
        self.check()

    def check(self):
        if self.value < 0 or self.value > self.max_value:
            raise ValueError('value {} out of range: {}'.format(self.name, self.value))

    def __contains__(self, data):
        return self.value == data
