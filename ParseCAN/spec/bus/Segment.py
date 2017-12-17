from ... import spec, data, helper
from typing import Iterable

class SegmentSpec:
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
        self._values = {}
        # values synonymous to enum

        if enum:
            for valnm in enum:
                if isinstance(enum[valnm], int):
                    try:
                        self.upsert_value(spec.value(valnm, enum[valnm]))
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
                    self.upsert_value(enum[valnm])
                else:
                    raise TypeError('value given is not int or spec.value')

    @property
    def values(self): # Iterable[spec.values]:
        return self._values.values()

    def get_value(self, val):
        '''
        Returns the spec.value synonymous to `val` in this spec.segment.
        '''
        assert isinstance(val, spec.value)
        return self._values[val.name]

    def upsert_value(self, val) -> bool:
        '''
        Attach, via upsert, a spec.value to this segment spec.
        Returns true if replacement occured.
        '''
        assert isinstance(val, spec.value)
        rep = helper.dict_key_populated(self._values, val.name, val)
        self._values[val.name] = val

        return rep

    def interpret(self, message: data.message):
        assert isinstance(message, data.message)
        msgdata = str(message[self.position:(self.position + self.length)]) + self.unit

        if self._values:
            return (self.data_name(msgdata), msgdata)

        return msgdata

    def data_name(self, data):
        '''
        Returns the first contained spec.value in which data is contained.
        '''
        incl = (value for value in self._values if data in self._values[value])
        return next(incl, None)

    def __str__(self):
        '''
        A comma separated representation of a spec.segment's values.
        In the same order as spec.segment.attributes.
        '''
        return ', '.join(str(getattr(self, x)) for x in self.attributes)
