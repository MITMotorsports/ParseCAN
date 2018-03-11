from ... import spec, data, helper, plural
from typing import Iterable

class SegmentType:
    '''
    A specification for a segment of a larger data string.
    '''

    attributes = ('name', 'c_type', 'unit', 'position', 'length', 'signed', 'values')

    def __init__(self, name, c_type='', unit='', position=None, length=None, signed=False, enum=None):
        self.name = str(name)
        self.c_type = str(c_type)
        self.unit = str(unit)
        self.position = int(position)
        if self.position < 0 or self.position > 64:
            raise ValueError('incorrect position: {}'.format(self.position))

        self.length = int(length)
        if self.length < 1:
            raise ValueError('length too small: {}'.format(self.length))
        if self.position + self.length > 64:
            raise ValueError('length overflows: {}'.format(self.length))

        self.signed = bool(signed)
        self.__values = plural.unique('name', 'value', type=spec.value)
        # values synonymous to enum

        if enum:
            if isinstance(enum, list):
                enum = {valnm: idx for idx, valnm in enumerate(enum)}

            for valnm in enum:
                if isinstance(enum[valnm], int):
                    try:
                        self.values.safe_add(spec.value(valnm, enum[valnm]))
                    except Exception as e:
                        e.args = (
                            'in value {}: {}'
                            .format(
                                valnm,
                                e
                            ),
                        )

                        raise

                elif isinstance(enum[valnm], spec.value):
                    self.safe_add(enum[valnm])
                else:
                    raise TypeError('value given is not int or spec.value')

    @property
    def values(self):
        return self.__values

    def interpret(self, message: data.message):
        assert isinstance(message, data.message)
        msgdata = str(message[self.position:(self.position + self.length)]) + self.unit

        if self._values:
            return (self.data_name(msgdata), msgdata)

        return msgdata

    def data_name(self, data):
        '''
        Returns the first contained spec.value in which data is contained
        '''
        incl = (value for value in self.values if data in self.value)
        return next(incl, None)

    def __str__(self):
        '''
        A comma separated representation of a spec.segment's values.
        In the same order as spec.segment.attributes.
        '''
        return ', '.join(str(getattr(self, x)) for x in self.attributes)
