from types import MappingProxyType


class PluralUnique:
    def __init__(self, *attributes: str):
        assert len(attributes) >= 1
        # Unnecessary check. Error will get raised in dict comprehension.
        # assert all(isinstance(attr, str) for attr in attributes)
        self.__store = {attrnm: {} for attrnm in attributes}

    @property
    def attributes(self):
        return iter(self.__store.keys())

    def add(self, item):
        removal = None
        for attrnm in self.attributes:
            attr = vars(item)[attrnm]

            if attr in self.__store[attrnm]:
                removal = self.__store[attrnm][attr]
                self.remove(removal)

            self.__store[attrnm][attr] = item

        return removal

    def remove(self, item):
        for attrnm in self.attributes:
            attr = vars(item)[attrnm]

            if attr in self.__store[attrnm]:
                del self.__store[attrnm][attr]

    def __getitem__(self, attrnm: str):
        if attrnm not in self.__store:
            raise KeyError('there is no mapping by {}'.format(attrnm))

        return MappingProxyType(self.__store[attrnm])

    def __contains__(self, item):
        '''
        True if the exact instance of `item` is in `self`,
        False otherwise.
        '''
        return any(self.__store[attrnm][vars(item)[attrnm]] == item
                   for attrnm in self.attributes
                   if vars(item)[attrnm] in self.__store[attrnm])

    def __iter__(self):
        return iter(next(iter(self.__store.values())).values())

if __name__ == '__main__':
    class ValueSpec:
        attributes = ('name', 'value')

        def __init__(self, name, value):
            self.name = str(name)
            self.value = int(value)
            if self.value < 0 or self.value > 1.8446744e+19:
                raise ValueError('incorrect value: {}'.format(self.value))

    a = PluralUnique('name', 'value')
    b = ValueSpec('w', 2)
    c = ValueSpec('2', 4)
    print(a.add(b))
    print(a.add(c))
    print(a['name']['w'])
