import sys
sys.path.append('../ParseCAN')

import re
from ParseCAN import parse, data


def pcantrc_parser(line):
    m = re.search(r'([0-9]+)\)\s+([0-9\.]+)\s+([a-zA-Z]+)\s+([0-9A-F]+)\s+([0-9]+)\s+([0-9A-F\s]+)', line)

    if not m:
        return None

    timestr = m.group(2)
    can_idstr = m.group(4)
    datastr = m.group(6).replace(' ', '')

    return data.FrameTimed(
               time=parse.number(timestr, 'ms'),
               can_id=int(can_idstr, 16),
               data=parse.hexstr_to_bytes(datastr)
           )


def tsvlog_parser(line):
    m = line.rstrip().split('\t')

    if line.startswith('~') or not m:
        return None

    timestr, busstr, can_idstr, datastr = m

    return data.FrameTimed(
               time=parse.number(timestr, 'ms'),
               can_id=int(can_idstr, 16),
               data=parse.hexstr_to_bytes(datastr)
           )
