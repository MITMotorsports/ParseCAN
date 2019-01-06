from dataclasses import dataclass, field
from typing import Any, List, Union

from ... import plural
from ...helper import Slice
from . import Atom


def _atom_pre_add(self, item):
    intersections = self.intersections(item)

    if intersections:
        formatted = ', '.join(map(str, intersections))
        raise ValueError(f'atom {item} intersects with {formatted}')


def _atom_constr(key, atom):
    try:
        if isinstance(atom, str):
            return Atom.from_str(name=key, string=atom)

        return Atom(name=key, **atom)
    except Exception as e:
        e.args = ('in atom {}: {}'.format(key, e),)

        raise


AtomUnique = plural.Unique[Atom].make('AtomUnique', ['name'], main='name')


def _atom_intersections(self: AtomUnique, seg: Atom) -> List[Atom]:
    '''
    a list of the atoms in self with which `seg` intersects.

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
    return [x for x in self if seg is not x and (half(x, seg) or half(seg, x))]


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


@dataclass
class SingleFrame(Frame):
    period: Any = None
    atoms: AtomUnique = field(default_factory=AtomUnique)

    atom_ruleset = _atom_ruleset

    def __post_init__(self):
        atoms = self.atoms
        self.atoms = AtomUnique()

        if isinstance(atoms, dict):
            atoms = [_atom_constr(k, v) for k, v in atoms.items()]

        self.atoms.extend(atoms)

    def unpack(self, frame, **kwargs):
        return {seg.name: seg.unpack(frame, **kwargs) for seg in self.atoms}

    def pack(self):
        raise NotImplementedError()


@dataclass
class FrameCollection(Frame):
    slice: Slice
    frames: FrameUnique = field(default_factory=FrameUnique)

    def __post_init__(self):
        frames = self.frames
        self.frames = FrameUnique()

        if isinstance(frames, dict):
            atoms = [_atom_constr(k, v) for k, v in atoms.items()]

        self.frames.extend(atoms)

    def pack(self):
        raise NotImplementedError()
