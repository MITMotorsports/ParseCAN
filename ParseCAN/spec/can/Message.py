from ... import spec, data, meta, parse


class MessageSpec(meta.message):
    '''
    A specification describing an arbitrary CAN Message's format and contents.
    '''

    attributes = ('name', 'can_id', 'is_big_endian', 'frequency', 'segments')

    def __init__(self, name, can_id, is_big_endian, frequency=None, segments=None):
        self.name = str(name)
        self.can_id = parse.number(can_id)
        self.is_big_endian = bool(is_big_endian)
        self.frequency = parse.SI(frequency, 'Hz') if frequency else None
        self.segments = {}

        for segnm in segments:
            if isinstance(segments[segnm], dict):
                try:
                    cand = spec.segment(name=segnm, **segments[segnm])
                except Exception as e:
                    e.args = (
                        'in segment {}: {}'
                        .format(
                            segnm,
                            e
                        ),
                    )

                    raise

                rep = self.upsert_segment(cand)
            else:
                rep = self.upsert_segment(segments[segnm])

            # This is not really possible due to the data coming in through a name dict
            if rep:
                raise ValueError('repeated segments with same name {}'.format(segnm))

    def __iter__(self):
        return iter(self.segments.values())

    def get_segment(self, seg):
        '''
        Given a spec.segment return the corresponding
        spec.segment in this spec.message.
        '''
        assert isinstance(seg, spec.segment)
        return self.segments[seg.name]

    def segment_intersections(self, seg):
        '''
        Returns a list of the segments in self
        with which `seg` intersects.
        '''
        assert isinstance(seg, spec.segment)

        def w(x, s):
            return x.position <= s.position <= x.position + x.length - 1 or x.position <= s.position + s.length - 1 <= x.position + x.length - 1

        # w should be commutative so let's aplpy it twice instead of redefining
        return [x.name for x in self if w(x, seg) or w(seg, x)]

    def upsert_segment(self, seg):
        '''
        Attach, via upsert, a spec.segment to this spec.message.
        `seg` must not intersect other segments
            If it does, a ValueError is raised.
        Returns true if replacement ocurred.
        '''
        assert isinstance(seg, spec.segment)

        intersections = self.segment_intersections(seg)
        if intersections:
            raise ValueError(
                'segment {} intersects with {}'
                .format(seg.name, ', '.join(intersections))
            )

        replacement = seg.name in self.segments and self.segments[seg.name] != seg
        self.segments[seg.name] = seg

        return replacement

    def interpret(self, message):
        assert isinstance(message, data.message)

        names = self.segments.values()
        return (self.name, {seg.name: seg.interpret(message) for seg in names})

    def __str__(self):
        '''
        A comma separated representation of a spec.message's values.
        In the same order as spec.message.attributes.
        '''
        return ', '.join(str(getattr(self, x)) for x in self.attributes)
