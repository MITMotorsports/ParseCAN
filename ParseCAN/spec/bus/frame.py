from dataclasses import dataclass, field
from typing import Any, List
from intervaltree import Interval, IntervalTree  # TODO: Replace it with a simpler local implementation.
from math import ceil

from ... import plural
from ...helper import Slice
from . import Atom
from ... import data


def interval_from_sliceable(item) -> Interval:
    return Interval(item.slice.start, item.slice.stop, item)


class AtomUnique(plural.Unique[Atom].make('AtomUnique', ['name'], main='name')):
    intervaltree: IntervalTree

    def __init__(self, *args, intervaltree: IntervalTree=None, **kwargs):
        super().__init__(*args, **kwargs)
        if intervaltree is None:
            self.intervaltree = IntervalTree()
        else:
            self.intervaltree = intervaltree

def _atom_pre_add(self: AtomUnique, item: Atom):
    overlaps = [x.data for x in self.intervaltree[item.slice.start : item.slice.stop]]

    if overlaps:
        formatted = ', '.join(map(str, overlaps))
        raise ValueError(f'{item} overlaps with {formatted}')


def _atom_post_add(self: AtomUnique, item: Atom):
    self.intervaltree.add(interval_from_sliceable(item))


def _atom_post_remove(self: AtomUnique, item: Atom):
    self.intervaltree.remove(interval_from_sliceable(item))


def _atom_constr(key, atom):
    try:
        if isinstance(atom, str):
            return Atom.from_str(name=key, string=atom)

        return Atom(name=key, **atom)
    except Exception as e:
        e.args = ('in atom {}: {}'.format(key, e),)

        raise


_atom_ruleset = plural.RuleSet(dict(add=dict(pre=_atom_pre_add,
                                             post=_atom_post_add),
                                    remove=dict(post=_atom_post_remove)))
_atom_ruleset.apply(AtomUnique)


@dataclass(init=False)
class Frame:
    name: str
    key: int


FrameUnique = plural.Unique[Frame].make('FrameUnique', ['name', 'key'], main='name')


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

    def __post_init__(self):
        atom = self.atom
        self.atom = AtomUnique()  # TODO: Add a modifier to the constructor using fields?

        if isinstance(atom, dict):
            atom = [_atom_constr(k, v) for k, v in atom.items()]

        self.atom.extend(atom)

    def unpack(self, frame, **kwargs):
        return {atom.name: atom.unpack(frame, **kwargs) for atom in self.atom}
        # print(self.pack(**{atomnm: ret[atomnm][0] for atomnm in ret}))

    # TODO: Fix janky pack with funny endianness
    def pack(self, by='name', **kwargs):
        raise NotImplementedError
        # print(kwargs)
        # bitstring = 0
        # # print(bitstring)
        # for atomnm in kwargs:
        #     atom = self.atom[by][atomnm]
        #     bitstring = data.evil_macros.INSERT(kwargs[atomnm], bitstring,
        #                                         atom.slice.start, atom.slice.length)
        #     print(kwargs[atomnm], atom.slice.start, atom.slice.length)
        # # TODO: fix
        # print('----------', bitstring, len(self))
        # # figure out why this works when you allocate 2 extra bytes...
        # byteobj = bitstring.to_bytes(len(self)+2, byteorder='big')
        # return data.frame.Frame(self.key, byteobj)

    def __len__(self):
        return ceil(max(atom.slice.start + atom.slice.length for atom in self.atom) / 8)


def _check_interval(item: Frame, interval: Interval):
    if isinstance(item, SingleFrame):
        for x in item.atom.intervaltree[interval.begin : interval.end]:
            yield x.data
    elif isinstance(item, MultiplexedFrame):
        sliceoverlap = interval.overlaps(item.slice.begin, item.slice.end)
        if sliceoverlap:
            yield sliceoverlap

        for frame in item.frame:
            yield from _check_interval(frame, interval)


def _mux_frame_pre_add(self: FrameUnique, item: Frame, metadata):
    overlaps = list(_check_interval(item, interval_from_sliceable(metadata)))

    if overlaps:
        formatted = ', '.join(map(str, overlaps))
        raise ValueError(f'{metadata} overlaps with {formatted}')


def _edit_interval(item: Frame, interval: Interval, add: bool):
    if isinstance(item, SingleFrame):
        if add:  # multiple dispatch >> OOP
            item.atom.intervaltree.add(interval)
        else:
            item.atom.intervaltree.remove(interval)
    elif isinstance(item, MultiplexedFrame):
        for frame in item.frame:
            _edit_interval(frame, interval, add)


def _mux_frame_post_add(self: FrameUnique, item: Frame, metadata):
    _edit_interval(item, interval_from_sliceable(metadata), True)


def _mux_frame_post_remove(self: FrameUnique, item: Frame, metadata):
    _edit_interval(item, interval_from_sliceable(metadata), False)


_mux_frame_ruleset = plural.RuleSet(dict(add=dict(pre=_mux_frame_pre_add,
                                                  post=_mux_frame_post_add),
                                         remove=dict(post=_mux_frame_post_remove)))


@dataclass
class MultiplexedFrame(Frame):
    slice: Slice
    frame: FrameUnique = field(default_factory=FrameUnique)

    def __post_init__(self):
        self.slice = Slice.from_general(self.slice)

        frame = self.frame
        self.frame = FrameUnique()
        _mux_frame_ruleset.apply(self.frame, metadata=self)

        if isinstance(frame, dict):
            frame = [_frame_constr(k, v) for k, v in frame.items()]

        self.frame.extend(frame)

    def unpack(self, frame, **kwargs):
        mux_id = frame[self.slice.start, self.slice.length]
        return (self.frame['key'][mux_id].name, self.frame['key'][mux_id].unpack(frame, **kwargs))

    def pack(self):
        raise NotImplementedError()
