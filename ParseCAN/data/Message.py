from .. import parse, meta

__all__ = ['message', 'messageTimed']


class message(meta.message):

    attributes = ('can_id', 'data')

    def __init__(self, can_id, data):
        # Store our attributes in the format we want them.
        self.can_id = parse.number(can_id)
        self.data = parse.number(data)

    def __getitem__(self, index):
        '''
        Returns the bit or range of bits within data.
        '''
        return int('0b0' + bin(self.data)[2:][index], 2)
        # TODO: Sue python for negative step not working for no reason.

    def __str__(self):
        '''
        A comma separated representation of self's values.
        In the same order as self.attributes.
        '''
        return ', '.join(str(getattr(self, x)) for x in self.attributes)

    def __iter__(self):
        return (getattr(self, x) for x in self.attributes)

    def interpret(self, spec):
        return spec.interpret(self)


class messageTimed(message):
    '''
    Represents a logged CAN message with well defined time, ID, and data.
    '''
    attributes = ('can_id', 'data', 'time')

    def __init__(self, can_id, data, time):
        '''
        Expects can_id, data in a string of capital hex format.
        '''
        # Store our attributes in the format we want them (numbers).
        self.can_id = parse.number(can_id)
        self.data = parse.number(data)
        self.time = parse.number(time)
