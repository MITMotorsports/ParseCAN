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
