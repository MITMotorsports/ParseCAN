from ... import spec, data, meta, parse, helper, plural


class MessageType(meta.message):
    '''
    A specification describing an arbitrary CAN Message's format and contents.
    '''

    attributes = ('name', 'can_id', 'is_big_endian', 'period', 'segments')

    def __init__(self, name, can_id, is_big_endian, period=None, segments=None):
        self.name = str(name)
        self.can_id = parse.number(can_id)
        self.is_big_endian = bool(is_big_endian)

        if period:
            self.period = parse.SI(period, 's')

        self.__segments = plural.unique('name', type=spec.segment)

        for segnm in segments:
            if isinstance(segments[segnm], dict):
                try:
                    seg = spec.segment(name=segnm, is_big_endian=self.is_big_endian, **segments[segnm])
                    self.segments.safe_add(seg)
                except Exception as e:
                    e.args = (
                        'in segment {}: {}'
                        .format(
                            segnm,
                            e
                        ),
                    )

                    raise
            else:
                seg = segments[segnm]
                self.segments.safe_add(seg)

            intersections = self.segment_intersections(seg)
            if intersections:
                raise ValueError(
                    'segment {} intersects with {}'
                    .format(seg.name, ', '.join(intersections))
                )

    @property
    def segments(self):
        return self.__segments

    def segment_intersections(self, seg):
        '''
        Returns a list of the segments in self
        with which `seg` intersects.
        '''
        assert isinstance(seg, spec.segment)

        def w(x, s):
            return x.position <= s.position <= x.position + x.length - 1 or x.position <= s.position + s.length - 1 <= x.position + x.length - 1

        # w should be commutative so let's apply it twice instead of redefining
        return [x.name for x in self.segments if seg != x and (w(x, seg) or w(seg, x))]

    def unpack(self, message):
        assert isinstance(message, data.message)
        names = self._segments.values()

        return (self.name, {seg.name: seg.unpack(message) for seg in names})

    def __str__(self):
        '''
        A comma separated representation of a spec.message's values.
        In the same order as spec.message.attributes.
        '''
        return ', '.join(str(getattr(self, x)) for x in self.attributes)

    def pack(self, by='name', **kwargs):
        bitstring = 0
        for segnm in kwargs:
            seg = self.segments.name[segnm]
            bitstring = data.INSERT(kwargs[segnm], bitstring,
                                    seg.position, seg.length)

        return data.message(self.can_id, bitstring)

    def unpack(self, frame):
        return {seg.name: seg.unpack(frame) for seg in self.segments}

    def swap_endianness(val, length, signed):
        if signed:
            if length == 16:
                return (val << 8) | ((val >> 8) & 0xFF)
            elif length == 32:
                val = ((val << 8) & 0xFF00FF00) | ((val >> 8) & 0xFF00FF)
                return (val << 16) | ((val >> 16) & 0xFFFF)
            else:
                raise ValueError
        else:
            if length == 16:
                return (val << 8) | (val >> 8)
            elif length == 32:
                val = ((val << 8) & 0xFF00FF00) | ((val >> 8) & 0xFF00FF)
                return (val << 16) | (val >> 16)
            else:
                raise ValueError
