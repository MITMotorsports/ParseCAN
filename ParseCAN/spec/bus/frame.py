from dataclasses import dataclass, field
from math import ceil
from typing import Any, List

from ... import data, meta, plural
from . import Segment


def _segment_pre_add(self, item):
    intersections = self.intersections(item)

    if intersections:
        formatted = ', '.join(map(str, intersections))
        raise ValueError(f'segment {item} intersects with {formatted}')


def _segment_constr(key, segment):
    try:
        if isinstance(segment, str):
            return Segment.from_string(name=key, string=segment)

        return Segment(name=key, **segment)
    except Exception as e:
        e.args = ('in segment {}: {}'.format(key, e),)

        raise


SegmentUnique = plural.Unique[Segment].make('SegmentUnique', ['name'], main='name')


def _segment_intersections(self: SegmentUnique, seg: Segment) -> List[Segment]:
    '''
    a list of the segments in self with which `seg` intersects.

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


SegmentUnique.intersections = _segment_intersections

_segment_ruleset = plural.RuleSet(dict(add=dict(pre=_segment_pre_add)))
_segment_ruleset.apply(SegmentUnique)


@dataclass
class Frame:
    '''
    A specification describing an arbitrary CAN Message's format and contents.
    '''

    name: str
    id: int
    period: Any = None
    segments: SegmentUnique = field(default_factory=SegmentUnique)

    segment_ruleset = _segment_ruleset

    def __post_init__(self):
        segments = self.segments
        self.segments = SegmentUnique()

        if isinstance(segments, dict):
            segments = [_segment_constr(k, v) for k, v in segments.items()]

        self.segments.extend(segments)

    def __len__(self):
        return ceil(max(seg.slice.start + seg.slice.length for seg in self.segments) / 8)

    def pack(self, by='name', **kwargs):
        bitstring = 0
        for segnm in kwargs:
            seg = self.segments[by][segnm]
            bitstring = data.evil_macros.INSERT(kwargs[segnm], bitstring,
                                                seg.slice.start, seg.slice.length)

        byteobj = bitstring.to_bytes(len(self), 'big')
        return data.Frame(self.id, byteobj)

    def unpack(self, frame, **kwargs):
        return {seg.name: seg.unpack(frame, **kwargs) for seg in self.segments}
