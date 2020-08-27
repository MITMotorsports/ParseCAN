import struct
from ..spec.bus.type import Endianness

fmttolen = {
    'b': 1,
    'B': 1,
    'h': 2,
    'H': 2,
    'i': 4,
    'I': 4,
    'q': 8,
    'Q': 8
}


def cast(type, num, endianness):
    d = '>' if endianness == Endianness.BIG or endianness == 'big' else '<'
    inbytes = num.to_bytes(fmttolen[type], 'big')
    return struct.unpack(d + type, inbytes)[0]


def cast_gen(type):
    def closure(x, **kwargs):
        return cast(type, num=x, **kwargs)

    return closure


CASTS = {
    'bool': lambda x, **kw: bool(x),
    'int8': cast_gen('b'),
    'uint8': cast_gen('B'),
    'int16': cast_gen('h'),
    'uint16': cast_gen('H'),
    'int32': cast_gen('i'),
    'uint32': cast_gen('I'),
    'int64': cast_gen('q'),
    'uint64': cast_gen('Q'),
}


def RPAD(n, l):
    '''
    Pads an integer `n` with zeros until it's `l` bits long.
    '''
    return n << (l - n.bit_length())


def ONES(leng):
    return ((1 << (leng)) - 1)


def START_IDX(start, leng):
    return (64 - (start) - (leng))


def ZEROES_MASK(start, leng):
    return (~(ONES(leng) << START_IDX(start, leng)))


def INPUT_MASK(inp, start, leng):
    return (((inp) & ONES(leng)) << START_IDX(start, leng))


def INSERT(inp, out, start, leng):
    return (((out) & (ZEROES_MASK(start, leng))) | INPUT_MASK(inp, start, leng))


def EXTRACT(inp, start, leng):
    return (((inp) >> START_IDX(start, leng)) & ONES(leng))

def REVERSE_BITS(raw, leng):
    format = '{{:0{}b}}'.format(leng)
    return int(format.format(raw)[::-1], 2)
