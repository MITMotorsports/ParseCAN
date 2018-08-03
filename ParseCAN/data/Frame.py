from .. import parse, data, meta, helper

__all__ = ['Frame', 'FrameTimed']


class Frame(meta.Message):
    attributes = ('id', 'data')
    __slots__ = ('id', '_data', '_raw_data')

    def __init__(self, id, data):
        # Store our attributes in the format we want them.
        self.id = int(id)
        self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, x):
        if not isinstance(x, (bytes, bytearray)):
            raise TypeError('data must be of type bytes or bytearray')

        self._data = x
        self._raw_data = int.from_bytes(x, byteorder='big', signed=False) << 8 * (8 - len(x))

    def __getitem__(self, index):
        '''
        Returns the bit or range of bits within data.
        '''
        if isinstance(index, int):
            position = index
            length = 1
        elif isinstance(index, tuple):
            position, length = index
        else:
            raise TypeError('frame indices must be integers or tuples, not {}'
                            .format(type(index).__name__))

        return data.evil_macros.EXTRACT(self._raw_data, position, length)

    __str__ = helper.csv_by_attrs(attributes, mapdict={
        'time': int,
        'can_id': hex,
        'data': hex
    })

    def __iter__(self):
        return (getattr(self, x) for x in self.attributes)

    def unpack(self, spec, **kwargs):
        return spec.unpack(self, **kwargs)


class FrameTimed(Frame):
    attributes = ('time', 'can_id', 'data')
    __slots__ = Frame.__slots__ + ('time',)

    def __init__(self, *args, time, **kwargs):
        super().__init__(*args, **kwargs)
        self.time = time
