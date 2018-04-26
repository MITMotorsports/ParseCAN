from .. import parse, data, meta, helper

__all__ = ['Frame', 'FrameTimed']

datamodule = data

class Frame(meta.message):

    attributes = ('can_id', 'data')

    def __init__(self, can_id, data):
        # Store our attributes in the format we want them.
        self.can_id = int(can_id)

        if isinstance(data, (bytes, bytearray)):
            self.data = datamodule.evil_macros.bytestoint(data, 64)
        else:
            self.data = int(data)

    def __getitem__(self, index):
        '''
        Returns the bit or range of bits within data.
        '''
        if isinstance(index, int):
            position = index
            length = 1
        elif isinstance(index, tuple):
            position = index[0]
            length = index[1]
        else:
            raise TypeError('frame indices must be integers or tuples, not {}'
                            .format(type(index).__name__))

        return data.EXTRACT(self.data, position, length)

    __str__ = helper.csv_by_attrs(attributes, mapdict={
        'time': parse.number_in('ms'),
        'can_id': hex,
        'data': hex
    })

    def __iter__(self):
        return (getattr(self, x) for x in self.attributes)

    def unpack(self, spec):
        return spec.unpack(self)


class FrameTimed(Frame):
    attributes = ('time', 'can_id', 'data')

    def __init__(self, *args, time, **kwargs):
        super().__init__(*args, **kwargs)
        self.time = parse.number(time, True)

        # Make sure time is in a time unit
        self.time.to('s')
