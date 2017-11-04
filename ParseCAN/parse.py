'''
A module containing all the specifics about each file format.
'''
import re

SI_MOD = {
    'u': 1e-6,
    'm': 1e-3,
    '': 1,
    'k': 1e3,
    'K': 1e3,
    'M': 1e6,
}


def frequency(freq):
    '''
    Extract frequency of CAN Message from spec.
    '''
    if isinstance(freq, (int, float)):
        return freq

    match = re.search(r'(\d\.*\d*)*([A-Za-z]*)', freq)
    unit = match.group(2)
    num = float(match.group(1))
    if unit.lower().endswith('hz'):
        return num * SI_MOD[unit[:-2]]
    elif len(unit) == 0:
        return num # Assuming no unit implies Hz
    else:
        raise ValueError('Unrecognized frequency unit {}.'.format(unit))


def number(num, reverse_endian=False):
    '''
    Parses a number. Reverses its endianess if `reverse_endian`.
    '''
    assert isinstance(num, (int, float, str))

    if isinstance(num, (int, float)):
        return num
    if reverse_endian:
        return int(bin(int(num, 0))[-1:1:-1], 2)

    return float(num) if '.' in num else int(num, 0)


def log(line):
    return {
        'time': re.search(r'\(([0-9]+(.[0-9]+)?)\)', line).group(1),
        'can_id': '0x' + re.search(r'([0-9]+)#', line).group(1),
        'data': '0x' + re.search(r'#([0-9, A-F]+)', line).group(1),
    }


def node(obj, attributes, nodesrc):
    '''
    Extract specifid attributed from a node and set them to an object.
    '''
    for attr in attributes:
        setattr(obj, attr, nodesrc[attr])
