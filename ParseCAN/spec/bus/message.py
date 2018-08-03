from ... import spec, data, meta, parse, helper, plural
from math import ceil


class Message(meta.message):
    '''
    A specification describing an arbitrary CAN Message's format and contents.
    '''

    def __init__(self, name, id, period=None, segments=None):
        self.name = str(name)
        self.id = int(id)

        if period:
            self.period = parse.number(period)

            # Make sure period is in a time unit
            self.period.to('s')

        self.segments = segments

    @property
    def segments(self):
        return self._segments

    @segments.setter
    def segments(self, segments):
        self._segments = plural.Unique('name', type=spec.segment)

        for segnm in segments or ():
            if isinstance(segments[segnm], dict):
                try:
                    seg = spec.segment(name=segnm, **segments[segnm])
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
                seg = spec.segment.from_string(segnm, segments[segnm])
            else:
                seg = segments[segnm]

            self.segments.safe_add(seg)

            intersections = self.segment_intersections(seg)
            if intersections:
                raise ValueError(
                    'segment {} intersects with {}'
                    .format(seg.name, ', '.join(intersections))
                )

    def segment_intersections(self, seg):
        '''
        Returns a list of the segments in self
        with which `seg` intersects.
        '''
        assert isinstance(seg, spec.segment)

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

    __str__ = helper.csv_by_attrs(('name', 'id', 'period'))
