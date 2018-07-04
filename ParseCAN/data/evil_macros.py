import struct

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


def CAST(type, num, endianness):
    d = '>' if endianness == 'big' else '<'

    inbytes = num.to_bytes(fmttolen[type], endianness)
    return struct.unpack(d + type, inbytes)[0]


def cast_gen(type):
    def closure(x, **kwargs):
        return CAST(type, num=x, **kwargs)

    return closure


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
