import copy
import types
import dataclasses
from dataclasses import dataclass, field
from functools import wraps
from inspect import isclass
from typing import ClassVar, Set, Mapping, Callable, Iterable, Dict, T, Any


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


class Plural(Mapping[Any, T]):
    attributes: ClassVar[Set[str]]
    main: str = field(default=None, repr=False, hash=False)

    def __init__(self, init=None):
        if not hasattr(self, 'attributes'):
            raise AttributeError('attributes must be specified through make')

        self._store: Dict[str, Dict[Any, T]]
        self._store = {attrnm: {} for attrnm in self.attributes}

        if init:
            self.extend(init)

    @classmethod
    def make(cls, name, attributes, main=None):
        @classmethod
        def _disable_make(cls, name, attributes, main=None):
            raise TypeError('deep inheritance not necessary')

        attributes = set(attributes)

        if main is not None and main not in attributes:
            raise ValueError('main argument is not in the attributes set')

        nspace = dict(attributes=attributes, main=main, make=_disable_make)

        return types.new_class(name, (cls,), {}, lambda ns: ns.update(nspace))

    def add(self, item: T):
        for attrnm in self.attributes:
            attr = getattr(item, attrnm)

            if attr in self._store[attrnm]:
                self.remove(self._store[attrnm][attr])

            self._store[attrnm][attr] = item

    def extend(self, iterable: Iterable[T], **kwargs):
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

    def _verify_attr(self, attr):
        if attr not in self.attributes:
            raise KeyError(f'{attr} not in declared attributes')

    def keys(self, key=None):
        key = key or self.main
        self._verify_attr(key)
        return self._store[key].keys()

    def values(self, key=None):
        key = key or self.main
        self._verify_attr(key)
        return self._store[key].values()

    def items(self, key=None):
        key = key or self.main
        self._verify_attr(key)
        return self._store[key].items()

    def __getitem__(self, attr: str):
        self._verify_attr(attr)
        return types.MappingProxyType(self._store[attr])

    def __bool__(self):
        return bool(self.values())

    def __iter__(self):
        return iter(self.values())

    def __len__(self):
        return len(next(iter(self._store.values())))

    def __contains__(self, item):
        # Use an assignment expression and a condition on hasattr
        # s.t. this also works in cases when item is None
        return any(self._store[attr].get(getattr(item, attr), None) == item
                   for attr in self.attributes)

    def __repr__(self):
        name = type(self).__name__
        commasep = ', '.join(map(repr, self.values()))
        args = f'[{commasep}]' if len(self) else ''

        return f'{name}({args})'


class Unique(Plural[T]):
    def add(self, item: T):
        for attrnm in self.attributes:
            attr = getattr(item, attrnm)

            if attr in self._store[attrnm]:
                conflict = self._store[attrnm][attr]
                raise ValueError(f'{item} and {conflict} have equal '
                                 f'{attr!r} attributes')

        for attrnm in self.attributes:
            attr = getattr(item, attrnm)
            self._store[attrnm][attr] = item

        return None

    def values(self):
        return next(iter(self._store.values()), {}).values()


def asdict(obj, *, dict_factory=dict):
    if isinstance(obj, Plural):
        return dict_factory((asdict(k, dict_factory=dict_factory),
                             asdict(v, dict_factory=dict_factory))
                            for k, v in obj.items())
    elif dataclasses._is_dataclass_instance(obj):
        result = []
        for f in dataclasses.fields(obj):
            value = asdict(getattr(obj, f.name), dict_factory=dict_factory)
            result.append((f.name, value))
        return dict_factory(result)
    elif isinstance(obj, (list, tuple)):
        return type(obj)(asdict(v, dict_factory=dict_factory) for v in obj)
    elif isinstance(obj, dict):
        return type(obj)((asdict(k, dict_factory=dict_factory),
                          asdict(v, dict_factory=dict_factory))
                         for k, v in obj.items())
    else:
        return copy.deepcopy(obj)


if __name__ == '__main__':
    @dataclass
    class Enumerator:
        name: str
        value: int

    ManyEnum = Unique[Enumerator].make('ManyEnum', ('name', 'value'), 'name')

    a = Enumerator('w', 2)
    b = Enumerator('1', 4)
    c = Enumerator('q', 4)

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
        print('Error is:', e)

    print('\n\n')
    for k, v in container.items():
        print(k, v)

    print(len(container))

    print(asdict(container))
