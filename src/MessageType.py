import parse
from SegmentType import SegmentType
from CANMessage import CANMessage

class MessageType:
    '''
    A specification describing an arbitrary CAN Message's format and contents.
    '''

    attributes = ('name', 'can_id', 'is_big_endian', 'frequency', 'segments')
    def __init__(self, name, can_id, is_big_endian, frequency=None, segments=None):
        self.name = str(name)
        self.can_id = parse.number(can_id)
        self.is_big_endian = bool(is_big_endian)
        self.frequency = parse.frequency(frequency) if frequency else None
        self.segments = {}

        for segnm in segments:
            if isinstance(segments[segnm], dict):
                self.upsert_segmenttype(SegmentType(name=segnm, **segments[segnm]))
            else:
                self.upsert_segmenttype(segments[segnm])

    def get_segmenttype(self, seg):
        '''
        Given a SegmentType return the corresponding
        SegmentType in self MessageType.
        '''
        assert isinstance(seg, SegmentType)
        return self.segments[seg.name]

    def upsert_segmenttype(self, segtype):
        '''
        Attach, via upsert, a SegmentType to self MessageType.
        '''
        assert isinstance(segtype, SegmentType)
        self.segments[segtype.name] = segtype

    def interpret(self, message):
        assert isinstance(message, CANMessage)

        return (self.name, {seg.name : seg.interpret(message) for seg in self.segments.values()})

    def __str__(self):
        '''
        A comma separated representation of a MessageTypes's values.
        In the same order as MessageTypes.attributes.
        '''
        return ', '.join(str(getattr(self, x)) for x in self.attributes)
