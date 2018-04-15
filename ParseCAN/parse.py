'''
A module containing all the specifics about each file format.
'''
import re
import struct


def SI(value, expunit):
    '''
    Extract frequency of CAN Message from spec.
    '''
    if isinstance(value, (int, float)):
        return value

    SI_MOD = {
        'p': 1e-12,
        'n': 1e-9,
        'u': 1e-6,
        'm': 1e-3,
        'c': 1e-2,
        'd': 1e-1,
        '': 1,
        'da': 1e1,
        'h': 1e2,
        'k': 1e3,
        'M': 1e6,
        'G': 1e9,
        'T': 1e12,
    }

    match = re.search(r'(\d\.*\d*)*([A-Za-z]*)', value)
    unit = match.group(2)
    num = float(match.group(1))
    if unit.endswith(expunit):
        return num * SI_MOD[unit[:-len(expunit)]]
    elif len(unit) == 0:
        raise ValueError(
            'no unit given - expected multiple of {}'
            .format(expunit)
        )
    else:
        raise ValueError(
            'unrecognized unit {} - expected multiple of {}'
            .format(unit, expunit)
        )


def number(num, reverse_endian=False):
    '''
    Parses a number. Reverses its endianess if `reverse_endian`.
    '''
    assert isinstance(num, (int, float, str))

    if isinstance(num, (int, float)):
        return num
    if reverse_endian:
        return struct.unpack("<I", struct.pack(">I", i))[0]

    return float(num) if '.' in num else int(num, 0)


def node(obj, attributes, nodesrc):
    '''
    Extract specifid attributed from a node and set them to an object.
    '''
    for attr in attributes:
        setattr(obj, attr, nodesrc[attr])
