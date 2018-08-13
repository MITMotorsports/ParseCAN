from dataclasses import dataclass, field, InitVar


@dataclass
class Enumeration:
    name: str
    value: int
    max_value: InitVar[int] = field(repr=False, compare=False, hash=False, default=2 ** 64)

    def __post_init__(self, max_value):
        self.max_value = max_value
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
            raise ValueError(f'value out of range: {self.value}')

    def __contains__(self, data):
        return self.value == data
