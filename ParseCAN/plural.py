'''
Will be a general interface replacing maps of bus names to buses, currently
found  under spec.bus and spec.board in 3 different places.
'''

from ... import spec


class Plural:
    def __iter__(self):
        raise NotImplementedError

    def __contains__(self, x):
        raise NotImplementedError

    def add(self, x):
        raise NotImplementedError

    def upsert(self, x):
        rep = x in self  # and that x is not the same
        self.add(x)
        return rep

    def remove(self, x):
        raise NotImplementedError
