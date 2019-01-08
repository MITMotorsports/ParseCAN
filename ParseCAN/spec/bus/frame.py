from dataclasses import dataclass, field
from typing import Any, List, Union
from intervaltree import IntervalTree  # TODO: Replace it with a simpler local implementation.

from ... import plural
from ...helper import Slice
from . import Atom


AtomUnique = plural.Unique[Atom].make('AtomUnique', ['name'], main='name')


def _atom_pre_add(self: AtomUnique, item: Atom):
    overlaps = self.intervaltree[item.slice.start : item.slice.start + item.slice.length]

    if overlaps:
        formatted = ', '.join(map(str, overlaps))
        raise ValueError(f'{item} intersects with {formatted}')


def _atom_post_add(self: AtomUnique, item: Atom):
    self.intervaltree[item.slice.start : item.slice.start + item.slice.length] = item


def _atom_constr(key, atom):
    try:
        if isinstance(atom, str):
            return Atom.from_str(name=key, string=atom)

        return Atom(name=key, **atom)
    except Exception as e:
        e.args = ('in atom {}: {}'.format(key, e),)

        raise


_atom_ruleset = plural.RuleSet(dict(add=dict(pre=_atom_pre_add,
                                             post=_atom_post_add)))
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
                return MultiplexedFrame(name=key, **frame)

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
        self.atom = AtomUnique()  # TODO: Add a modifier to the constructor using fields?
        self.atom.intervaltree = IntervalTree()

        if isinstance(atom, dict):
            atom = [_atom_constr(k, v) for k, v in atom.items()]

        self.atom.extend(atom)

    def unpack(self, frame, **kwargs):
        return {atom.name: atom.unpack(frame, **kwargs) for atom in self.atom}

    def pack(self):
        raise NotImplementedError()


@dataclass
class MultiplexedFrame(Frame):
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
