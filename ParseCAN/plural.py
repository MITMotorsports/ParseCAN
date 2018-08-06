from copy import deepcopy
from dataclasses import dataclass
from functools import wraps
from inspect import isclass
from types import MappingProxyType
from typing import Collection, T


@dataclass
class RuleSet:
    # TODO: Fix type definition.
    rules: dict

    _supported = ('pre', 'post')

    _application_fmt = """\
old = receiver.{function}

@wraps(old)
def new(*args, **kwargs):
    {pre}
    old(*args, **kwargs)
    {post}

receiver.{function} = new
"""

    # TODO: Consider a better model for this.
    # This ensures that the receiver (class or instance) gets passed to the callback.
    _default_callback_fmtdict = {fn: '' for fn in _supported}
    _instance_callback_fmt = '{}(receiver, *args, {} **kwargs)'
    _class_callback_fmt = '{}(*args, {} **kwargs)'

    def apply(self, receiver, extension=None):
        '''
        Apply this ruleset to `receiver`.
        The callback must take [self, extension, *args, **kwargs].
        '''

        # HACK: Applicable to class or instance with the same callback signature.
        if isclass(receiver):
            callback_fmt = self._class_callback_fmt
        else:
            callback_fmt = self._instance_callback_fmt

        for fn in self.rules:
            callbacks = self._default_callback_fmtdict.copy()
            for rule in self.rules[fn]:
                extension_part = 'extension,' if extension is not None else ''
                callbacks[rule] = callback_fmt.format(rule, extension_part)

            ruleset_application = self._application_fmt.format(function=fn, **callbacks)

            namespace = dict(
                __name__='RuleSet_apply_{}'.format(fn),
                receiver=receiver,
                wraps=wraps,
                extension=extension,
                **self.rules[fn],
            )

            exec(ruleset_application, namespace)

        return receiver


class Plural:
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

        Will raise ValueError if `safe` and there exists an attribute conflict.
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

    # __getattr__ = __getitem__

    def __len__(self):
        return len(next(iter(self.__store.values())))

    def __contains__(self, item):
        '''
        True if the exact instance of `item` is in `self`,
        False otherwise.
        '''
        return any(self.__store[attrnm][vars(item)[attrnm]] is item
                   for attrnm in self.attributes
                   if getattr(item, attrnm) in self.__store[attrnm])

    def __iter__(self):
        return iter(next(iter(self.__store.values())).values())

    def __repr__(self):
        # Slice it to remove dict_keys( and the last parenthesis
        listview = repr(next(iter(self.__store.values())).values())[12:-1]
        attrview = ', '.join(map(repr, self.attributes))

        return 'Plural(' + attrview + ', init=' + listview + ')'


class Unique(Plural, Collection[T]):
    def add(self, *args, **kwargs):
        super().add(*args, safe=True, **kwargs)

    def __repr__(self):
        return 'Unique' + super().__repr__()[6:]


if __name__ == '__main__':
    @dataclass
    class Enumeration:
        name: str
        value: int

    container = Unique('name', 'value')
    a = Enumeration('w', 2)
    b = Enumeration('1', 4)
    c = Enumeration('q', 4)

    def post_add(instance, item, extension=None, **kwargs):
        print('Added {} to {} with {}!'.format(item, instance, kwargs))
        print('Extension is {}.'.format(extension))
        print('\n\n')

    ruleset = RuleSet({'add': {'post': post_add}})

    # Apply to all Unique instances
    ruleset.apply(Unique)

    new_container = Unique('name', 'value')
    new_container.add(a)

    # Apply once more to container
    # Expect a dual printout
    ruleset.apply(container, extension=34)

    container.add(a)
    container.add(b)
    container.add(c)
