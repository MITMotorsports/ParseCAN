import re
import datetime as dt
import time
from ParseCAN import parse, data


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


def pcantrc_parser(line):
    m = re.search(r'([0-9]+)\)\s+([0-9\.]+)\s+([a-zA-Z]+)\s+([0-9A-F]+)\s+([0-9]+)\s+([0-9A-F\s]+)', line)

    if not m:
        return None

    timestr = m.group(2)
    idstr = m.group(4)
    datastr = m.group(6).replace(' ', '')

    return data.FrameTimed(
               time=int(timestr) / 1000,  # in seconds
               id=int(idstr, 16),
               data=bytes.fromhex(datastr)
           )


@static_vars(inittime=None)
def tsvlog_parser(line):
    m = line.rstrip().split('\t')

    if not m:
        raise UserWarning('invalid line found `{}`'.format(line))
        return None

    if line.startswith('~'):
        ms, datestr, timestr = m
        ms = ms.lstrip('~')
        us = 1000 * int(ms)

        dtstr = '{} {}'.format(datestr, timestr)
        datetime = dt.datetime.strptime(dtstr, '%Y%m%d %H%M%S')
        idx = dt.timedelta(microseconds=us)

        datetime = datetime - idx

        tsvlog_parser.inittime = time.mktime(datetime.timetuple())
        return None

    timestr, busstr, idstr, datastr = m

    return data.FrameTimed(
               time=int(timestr) / 1000 + tsvlog_parser.inittime,  # POSIX time
               id=int(idstr, 16),
               data=bytes.fromhex(datastr)
           )
