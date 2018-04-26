import struct

fmttolen = {
    'h': 2,
    'H': 2,
    'i': 4,
    'I': 4,
    'q': 8,
    'Q': 8
}


def REVERSE(type, num):
    return struct.unpack('<' + type, num.to_bytes(fmttolen[type], 'big'))[0]


def reverse_gen(type):
    def closure(num):
        return REVERSE(type, num)

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
