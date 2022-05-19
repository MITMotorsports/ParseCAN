from types import MappingProxyType


class unique:
    def __init__(self, *attributes: str, init=None, type=None):
        assert len(attributes) >= 1
        # assert all(isinstance(attr, str) for attr in attributes)
        # Unnecessary check. Error will get raised in dict comprehension.
        self.__store = {attrnm: {} for attrnm in attributes}
        self.__type = type if type else object

        if init:
            for x in init:
                self.safe_add(x)

    @property
    def attributes(self):
        return iter(self.__store.keys())

    def add(self, item, safe=False):
        '''
        Add `item` to the internal representation.

        Will raise ValuError if `safe` is True and there exists a conflict.
        '''
        assert isinstance(item, self.__type)

        removal = None
        remattr = None
        for attrnm in self.attributes:
            attr = getattr(item, attrnm)

            if attr in self.__store[attrnm]:
                removal = self.__store[attrnm][attr]
                remattr = attrnm

                self.remove(removal)

                if safe:
                    raise ValueError(
                        '{} and {} have equal \'{}\' attributes'
                        .format(item, removal, remattr)
                    )

            self.__store[attrnm][attr] = item

        return None

    def safe_add(self, item):
        self.add(item, safe=True)

    # def find(self, item):
    #   return next(self[attrnm] for attrnm in self.attributes, None)

    def remove(self, item):
        assert isinstance(item, self.__type)

        for attrnm in self.attributes:
            attr = getattr(item, attrnm)

            if attr in self.__store[attrnm]:
                del self.__store[attrnm][attr]

    def __getitem__(self, attrnm: str):
        if attrnm not in self.__store:
            raise KeyError('there is no mapping by {}'.format(attrnm))

        return MappingProxyType(self.__store[attrnm])

    __getattr__ = __getitem__

    def __len__(self):
        return len(next(iter(self.__store.values())))

    def __contains__(self, item):
        '''
        True if the exact instance of `item` is in `self`,
        False otherwise.
        '''
        return any(self.__store[attrnm][vars(item)[attrnm]] == item
                   for attrnm in self.attributes
                   if getattr(item, attrnm) in self.__store[attrnm])

    def __iter__(self):
        return iter(next(iter(self.__store.values())).values())

    def __repr__(self):
        return str(self.__store)


if __name__ == '__main__':
    class ValueType:
        attributes = ('name', 'value')

        def __init__(self, name, value):
            self.name = str(name)
            self.value = int(value)
            if self.value < 0 or self.value > 1.8446744e+19:
                raise ValueError('incorrect value: {}'.format(self.value))

    a = unique('name', 'value')
    b = ValueType('w', 2)
    c = ValueType('1', 4)
    print(a.add(b))
    print(a.safe_add(c))
    print(a['name'])
    print(a.name)
    print(a)
