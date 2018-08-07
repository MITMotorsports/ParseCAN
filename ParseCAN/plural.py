from dataclasses import field, make_dataclass, dataclass
from functools import wraps
from inspect import isclass
from types import MappingProxyType
from typing import ClassVar, Tuple, Mapping, Callable, Collection, Iterable, T


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


class Plural(Collection[T]):
    attributes: ClassVar[Tuple[str]]

    def __post_init__(self):
        if not hasattr(self, 'attributes'):
            raise AttributeError('attributes must be specified through make')

        self.__store = {attrnm: {} for attrnm in self.attributes}

        self.extend(self.items)

    @classmethod
    def make(cls, *attributes):
        new_class = make_dataclass(cls.__name__,
                                   [('items', Iterable[T], field(default=tuple()))],
                                   namespace=cls.__dict__.copy())
        new_class.attributes = attributes

        return new_class

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

    def __getitem__(self, attrnm: str):
        if attrnm not in self.__store:
            raise KeyError('there is no mapping by {}'.format(attrnm))

        return MappingProxyType(self.__store[attrnm])

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


class Unique(Plural):
    def add(self, *args, **kwargs):
        super().add(*args, safe=True, **kwargs)

    def __repr__(self):
        return 'Unique' + super().__repr__()[6:]


if __name__ == '__main__':
    @dataclass
    class Enumeration:
        name: str
        value: int

    Container_class = Unique.make('name', 'value')

    a = Enumeration('w', 2)
    b = Enumeration('1', 4)
    c = Enumeration('q', 4)

    container = Container_class([a])

    def post_add(instance, item, extension=None, **kwargs):
        print('Added {} to {} with {}!'.format(item, instance, kwargs))
        print('Extension is {}.'.format(extension))
        print('\n\n')

    ruleset = RuleSet({'add': {'post': post_add}})

    # Apply to all Container_class instances
    ruleset.apply(Container_class)

    new_container = Container_class([a])

    # Apply once more to container instance
    # Expect a dual printout for adds on container instance
    ruleset.apply(container, extension=34)

    container.add(b)
    container.add(c)
