from dataclasses import dataclass, field
from typing import Any, List, Union

from ... import plural
from ...helper import Slice
from . import Atom


def _atom_pre_add(self, item):
    intersections = self.intersections(item)

    if intersections:
        formatted = ', '.join(map(str, intersections))
        raise ValueError(f'{item} intersects with {formatted}')


def _atom_constr(key, atom):
    try:
        if isinstance(atom, str):
            return Atom.from_str(name=key, string=atom)

        return Atom(name=key, **atom)
    except Exception as e:
        e.args = ('in atom {}: {}'.format(key, e),)

        raise


AtomUnique = plural.Unique[Atom].make('AtomUnique', ['name'], main='name')


def _atom_intersections(self: AtomUnique, atom: Atom) -> List[Atom]:
    '''
    a list of the atom in self with which `atom` intersects.

    An intersection is defined as an overlap between
    the start and stop of slices.
    '''
    def half(a, b):
        'True if `b` overlaps in `a`\'s range'
        a = a.slice
        b = b.slice

        head = a.start <= b.start <= a.stop
        tail = a.start <= b.stop <= a.stop
        return head or tail

    # half isn't commutative so let's apply it twice instead of defining full
    return [x for x in self if atom is not x and (half(x, atom) or half(atom, x))]


AtomUnique.intersections = _atom_intersections

_atom_ruleset = plural.RuleSet(dict(add=dict(pre=_atom_pre_add)))
_atom_ruleset.apply(AtomUnique)


@dataclass
class Frame:
    name: str
    key: int


FrameUnique = plural.Unique[Frame].make('FrameUnique',
                                        ['name', 'key'],
                                        main='name')


def _frame_constr(key, frame):
    if isinstance(frame, dict):
        try:
            if 'atom' in frame:
                return SingleFrame(name=key, **frame)

            if 'frame' in frame:
                return FrameCollection(name=key, **frame)

            raise ValueError('invalid frame definition has neither `atom` nor `frame` field')
        except Exception as e:
            e.args = ('in frame {}: {}'.format(key, e),)

            raise

    raise ValueError(f'malformed frame representation {key}: {frame}')


@dataclass
class SingleFrame(Frame):
    period: Any = None
    atom: AtomUnique = field(default_factory=AtomUnique)

    atom_ruleset = _atom_ruleset

    def __post_init__(self):
        atom = self.atom
        self.atom = AtomUnique()

        if isinstance(atom, dict):
            atom = [_atom_constr(k, v) for k, v in atom.items()]

        self.atom.extend(atom)

    def unpack(self, frame, **kwargs):
        return {atom.name: atom.unpack(frame, **kwargs) for atom in self.atom}

    def pack(self):
        raise NotImplementedError()


@dataclass
class FrameCollection(Frame):
    slice: Slice
    frame: FrameUnique = field(default_factory=FrameUnique)

    def __post_init__(self):
        frame = self.frame
        self.frame = FrameUnique()

        if isinstance(frame, dict):
            frame = [_frame_constr(k, v) for k, v in frame.items()]

        self.frame.extend(frame)

    def pack(self):
        raise NotImplementedError()
