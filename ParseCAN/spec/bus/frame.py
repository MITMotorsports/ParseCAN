from dataclasses import dataclass, field
from typing import Any, List
from intervaltree import Interval, IntervalTree  # TODO: Replace it with a simpler local implementation.
from math import ceil

from ... import plural
from ...helper import Slice
from . import Atom, Endianness, Type
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
        return (self, [(atom, atom.unpack(frame, **kwargs)) for atom in self.atom])

    def pack(self, bitstring = 0, by='name', **kwargs):
        # TODO: add support for FrameTimedBus and parents
        length = len(self)
        bitstring = self.to_bitstring(bitstring, **kwargs) >> (64 - length*8)
        byteobj = bitstring.to_bytes(length, byteorder='big')
        return data.frame.Frame(self.key, byteobj)

    def to_bitstring(self, bitstring=0, by='name', **kwargs):
        for atom_id in kwargs:
            atom = self.atom[by][atom_id]
            bitstring = data.evil_macros.INSERT(
                kwargs[atom_id],
                bitstring,
                atom.slice.start,
                atom.slice.length
            )
        return bitstring

    def __len__(self):
        return ceil(max(atom.slice.start + atom.slice.length for atom in self.atom) / 8)


def _check_interval(item: Frame, interval: Interval):
    if isinstance(item, SingleFrame):
        for x in item.atom.intervaltree[interval.begin : interval.end]:
            yield x.data
    elif isinstance(item, MultiplexedFrame):
        # Why doesn't TestMultiplexEnum trigger this
        sliceoverlap = interval.overlaps(item.slice.start, item.slice.start + item.slice.length)
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
    type: Type = None
    frame: FrameUnique = field(default_factory=FrameUnique)

    def __post_init__(self):
        self.slice = Slice.from_general(self.slice)

        frame = self.frame
        self.frame = FrameUnique()
        _mux_frame_ruleset.apply(self.frame, metadata=self)

        if isinstance(frame, dict):
            frame = [_frame_constr(k, v) for k, v in frame.items()]

        self.frame.extend(frame)

        if self.type is None:
            self.type = Type.from_str('uint8 big')
        elif isinstance(self.type, str):
            self.type = Type.from_str(self.type)
        elif isinstance(self.type, dict):
            self.type = Type.from_dict(self.type)
        elif not isinstance(self.type, Type):
            if len(self.slice) > 8:
                raise ValueError('unparseable type: {}'.format(self.type))

    def unpack(self, frame, **kwargs):
        raw = frame[self.slice.start, self.slice.length]
        mux_id = data.evil_macros.CASTS[self.type.type](raw, endianness=self.type.endianness)
        return (self,
                self.frame['key'][mux_id].unpack(frame, **kwargs))

    def pack(self, id_tup, by='name', **kwargs):
        # TODO: add support for FrameTimedBus and parents
        # Currently, 'by' applies to both frame_id and atom_id args
        bitstring = 0
        frame = self

        while isinstance(frame, MultiplexedFrame):
            id = id_tup[0]
            id_tup = id_tup[1]
            bitstring = data.evil_macros.INSERT(
                    frame.frame[by][id].key,
                    bitstring,
                    frame.slice.start,
                    frame.slice.length
                )
            frame = frame.frame[by][id]

        length = len(self)
        bitstring = frame.to_bitstring(bitstring=bitstring, **kwargs) >> (64 - length*8)
        byteobj = bitstring.to_bytes(length, byteorder='big')
        return data.frame.Frame(self.key, byteobj)

    def __len__(self):
        return max( ceil( (self.slice.start+self.slice.length)/8),
                    max( len(frame) for frame in self.frame )
                )
