'''
A module containing all the specifics about each file format.
'''
import pint

ureg = pint.UnitRegistry()

# TODO: Multiple specs could define units differently.
#       Make unit definitions spec specific.


def number(num, unit=False):
    '''
    Parses a number into an `int`, `float`, or `Quantity` whenever appropriate.

    - If `unit` is a string or Quantity, a number with the unit described will
    be returned. In that case `num` must be dimensionless.
    '''
    if isinstance(num, ureg.Quantity):
        if isinstance(unit, (str, ureg.Quantity)):
            return num.to(unit)

        return num

    if unit:
        return num * ureg.Quantity(unit)

    if isinstance(num, (int, float)):
        return num

    return ureg.parse_expression(num)


def number_in(unit):
    def in_unit(num):
        return number(num, unit).magnitude

    return in_unit


def hexstr_to_bytes(s):
    '''
    Returns a bytes object corresponding to to the hex string `s` given.
    len(s) must be a multiple of 2.
    '''

    if len(s) % 2 == 1:
        raise ValueError('given hex string is of odd length')

    gen = (int(twostr, 16) for twostr in map(''.join, zip(s[::2], s[1::2])))
    return bytes(gen)
