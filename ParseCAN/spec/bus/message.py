from dataclasses import dataclass
from math import ceil
from typing import Any

from ... import spec, data, meta, plural
from . import Segment


@dataclass
class Message(meta.Message):
    '''
    A specification describing an arbitrary CAN Message's format and contents.
    '''

    name: str
    id: int
    period: Any = None
    segments: plural.Unique[Segment]

    @property
    def segments(self):
        return self._segments

    @segments.setter
    def segments(self, segments):
        if isinstance(segments, plural.Unique):
            self._segments = segments.copy()
            # TODO: Make checks happen here too
            return

        self._segments = plural.Unique('name')
        
        if isinstance(segments, list):
            self._segments.extend(segments)
            return

        for segnm in segments or ():
            if isinstance(segments[segnm], dict):
                try:
                    seg = Segment(name=segnm, **segments[segnm])
                except Exception as e:
                    e.args = (
                        'in segment {}: {}'
                        .format(
                            segnm,
                            e
                        ),
                    )

                    raise
            elif isinstance(segments[segnm], str):
                seg = Segment.from_string(segnm, segments[segnm])
            else:
                seg = segments[segnm]

            self.segments.safe_add(seg)

            intersections = self.segment_intersections(seg)
            if intersections:
                raise ValueError(
                    'segment {} intersects with {}'
                    .format(seg.name, ', '.join(intersections))
                )

    def segment_intersections(self, seg: Segment):
        '''
        Returns a list of the segments in self
        with which `seg` intersects.
        '''
        def w(x, s):
            return x.slice.start <= s.slice.start <= x.slice.start + x.slice.length - 1 or x.slice.start <= s.slice.start + s.slice.length - 1 <= x.slice.start + x.slice.length - 1

        # w should be commutative so let's apply it twice instead of redefining
        return [x.name for x in self.segments if seg != x and (w(x, seg) or w(seg, x))]

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
