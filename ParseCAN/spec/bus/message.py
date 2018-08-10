from dataclasses import dataclass
from math import ceil
from typing import Any

from ... import data, meta, plural
from . import Segment


def _segment_pre_add(self, item, metadata):
    intersections = metadata.segment_intersections(item)

    if intersections:
        formatted = ', '.join(intersections)
        raise ValueError(f'segment {item} intersects with {formatted}')


def _segment_constr(key, segment):
    try:
        if isinstance(segment, str):
            return Segment.from_string(name=key, string=segment)

        return Segment(name=key, **segment)
    except Exception as e:
        e.args = ('in segment {}: {}'.format(key, e),)

        raise


SegmentUnique = plural.Unique[Segment].make('SegmentUnique', ['name'])


@dataclass
class Message(meta.Message):
    '''
    A specification describing an arbitrary CAN Message's format and contents.
    '''

    name: str
    id: int
    period: Any = None
    segments: SegmentUnique = SegmentUnique()

    segment_ruleset = plural.RuleSet(dict(add=dict(pre=_segment_pre_add)))

    def __post_init__(self):
        segments = self.segments
        self.segments = SegmentUnique()
        # TODO: Find a good way to apply to SegmentUnique but keep metadata.
        self.segment_ruleset.apply(self.segments, metadata=self)

        if isinstance(segments, dict):
            segments = [_segment_constr(k, v) for k, v in segments.items()]

        self.segments.extend(segments)

    def segment_intersections(self, seg: Segment):
        '''
        Returns a list of the segments in self with which `seg` intersects.
        '''
        def w(x, s):
            return x.slice.start <= s.slice.start <= x.slice.start + x.slice.length - 1 or x.slice.start <= s.slice.start + s.slice.length - 1 <= x.slice.start + x.slice.length - 1

        # w should be commutative so let's apply it twice instead of redefining
        return [x for x in self.segments if seg != x and (w(x, seg) or w(seg, x))]

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
