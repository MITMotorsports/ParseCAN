from dataclasses import dataclass
from functools import wraps
from types import MappingProxyType
from typing import Collection, T


class Plural:
    pass


@dataclass
class RuleSet:
    rules: dict

    _supported = ('pre', 'post')

    _application_fmt = """
old = cls.{function}

@wraps(old)
def new(*args, **kwargs):
    {pre}
    old(*args, **kwargs)
    {post}

cls.{function} = new
"""

    _callback_fmt = '{}(cls, *args, **kwargs)'
    _default_callback_fmtdict = {fn: '' for fn in _supported}

    def apply(self, cls, verbose=False):
        '''
        A decorator that applies the ruleset to a
        class or to an instance (TODO: decide)?
        '''

        for fn in self.rules:
            callbacks = self._default_callback_fmtdict.copy()
            for rule in self.rules[fn]:
                callbacks[rule] = self._callback_fmt.format(rule)

            ruleset_application = self._application_fmt.format(function=fn, **callbacks)

            namespace = dict(
                __name__='RuleSet_apply_{}'.format(fn),
                cls=cls,
                wraps=wraps,
                **self.rules[fn]
            )
            exec(ruleset_application, namespace)

            if verbose:
                print(ruleset_application)

        return cls


class Unique(Plural, Collection[T]):
    def __init__(self, *attributes: str, init=None):
        assert len(attributes) >= 1
        self.__store = {attrnm: {} for attrnm in attributes}

        if init is not None:
            self.extend(init)

    @property
    def attributes(self):
        return self.__store.keys()

    def add(self, item, safe=False):
        '''
        Add `item` to the internal representation.

        Will raise ValuError if `safe` is True and there exists a conflict.
        '''
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

    def extend(self, iterable, **kwargs):
        for val in iterable:
            self.add(val, **kwargs)

    def remove(self, item):
        for attrnm in self.attributes:
            attr = getattr(item, attrnm)

            if attr in self.__store[attrnm]:
                del self.__store[attrnm][attr]

    def copy(self):
        # TODO: Figure out if ruleset should still apply.
        return Unique(*self.attributes, init=self)

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
        # Slice it to remove dict_keys( and the last parenthesis
        return repr(next(iter(self.__store.values())).values())[12:-1]


if __name__ == '__main__':
    @dataclass
    class Enumeration:
        name: str
        value: int

    container = Unique('name', 'value')
    a = Enumeration('w', 2)
    b = Enumeration('1', 4)
    c = Enumeration('q', 4)

    def post_add(inst, item):
        print('Added {} to {}!'.format(item, inst))

    ruleset = RuleSet({'add': {'post': post_add}})
    ruleset.apply(container, verbose=True)

    container.add(a)
    container.add(b)
    container.safe_add(c)
