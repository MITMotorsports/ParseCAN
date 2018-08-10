import types
from dataclasses import dataclass
from functools import wraps
from inspect import isclass
from typing import ClassVar, Set, Mapping, Callable, Collection, T


@dataclass
class RuleSet:
    rules: Mapping[str, Mapping[str, Callable]]

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

    def apply(self, receiver, metadata=None):
        '''
        Apply this ruleset to `receiver`.
        The callback must take [self, metadata, *args, **kwargs].
        '''

        # HACK: Applicable to class or instance with the same callback signature.
        if isclass(receiver):
            callback_fmt = self._class_callback_fmt
        else:
            callback_fmt = self._instance_callback_fmt

        for fn in self.rules:
            callbacks = self._default_callback_fmtdict.copy()
            for rule in self.rules[fn]:
                metadata_part = 'metadata,' if metadata is not None else ''
                callbacks[rule] = callback_fmt.format(rule, metadata_part)

            ruleset_application = self._application_fmt.format(function=fn, **callbacks)

            namespace = dict(
                __name__='RuleSet_apply_{}'.format(fn),
                receiver=receiver,
                wraps=wraps,
                metadata=metadata,
                **self.rules[fn],
            )

            exec(ruleset_application, namespace)

        return receiver


class Plural(Collection[T]):
    attributes: ClassVar[Set[str]]

    def __init__(self, init=None):
        if not hasattr(self, 'attributes'):
            raise AttributeError('attributes must be specified through make')

        self._store = {attrnm: {} for attrnm in self.attributes}

        if init:
            self.extend(init)

    @classmethod
    def make(cls, name, attributes):
        @classmethod
        def _disable_make(cls, name, attributes):
            raise TypeError('deep inheritance not necessary')

        nspace = dict(attributes=set(attributes), make=_disable_make)

        return types.new_class(name, (cls,), {}, lambda ns: ns.update(nspace))

    def add(self, item: T, safe=False):
        '''
        Add `item` to the internal representation.

        Will raise ValueError if `safe` and there exists an attribute conflict.
        '''
        removal = None
        remattr = None
        for attrnm in self.attributes:
            attr = getattr(item, attrnm)

            if attr in self._store[attrnm]:
                removal = self._store[attrnm][attr]
                remattr = attrnm

                self.remove(removal)

                if safe:
                    raise ValueError(
                        '{} and {} have equal \'{}\' attributes'
                        .format(item, removal, remattr)
                    )

            self._store[attrnm][attr] = item

        return None

    def extend(self, iterable, **kwargs):
        for val in iterable:
            self.add(val, **kwargs)

    def remove(self, item: T):
        for attrnm in self.attributes:
            attr = getattr(item, attrnm)

            if attr in self._store[attrnm]:
                del self._store[attrnm][attr]

    def clean(self):
        del self._store
        self.__init__()

    @property
    def values(self):
        return next(iter(self._store.values())).values()

    def __bool__(self):
        return bool(self.values)

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, attrnm: str):
        if attrnm not in self.attributes:
            raise KeyError('there is no mapping by {}'.format(attrnm))

        return types.MappingProxyType(self._store[attrnm])

    def __len__(self):
        return len(next(iter(self._store.values())))

    def __contains__(self, item):
        '''
        True if the exact instance of `item` is in `self`,
        False otherwise.
        '''
        return any(self._store[attrnm].get(getattr(item, attrnm), None) is item
                   for attrnm in self.attributes)

    def __repr__(self):
        # Slice it to remove dict_keys( and the last parenthesis
        listview = repr(next(iter(self._store.values())).values())[12:-1]

        return type(self).__name__ + '(' + listview + ')'


class Unique(Plural, Collection[T]):
    def add(self, *args, **kwargs):
        super().add(*args, safe=True, **kwargs)


if __name__ == '__main__':
    @dataclass
    class Enumeration:
        name: str
        value: int

    ManyEnum = Unique[Enumeration].make('ManyEnum', ('name', 'value'))

    a = Enumeration('w', 2)
    b = Enumeration('1', 4)
    c = Enumeration('q', 4)

    print(ManyEnum.attributes)

    container = ManyEnum([a])

    def post_add(instance, item, metadata=None, **kwargs):
        print('Added {} to {} with {}!'.format(item, instance, kwargs))
        print('Metadata is {}.'.format(metadata))
        print('\n\n')

    ruleset = RuleSet({'add': {'post': post_add}})

    # Apply to all Container_class instances
    ruleset.apply(ManyEnum)

    new_container = ManyEnum([a])

    # Apply once more to container instance
    # Expect a dual printout for adds on container instance
    ruleset.apply(container, metadata=34)

    container.add(b)

    try:
        container.add(c)
    except ValueError as e:
        print(e)
