import sys
sys.path.append('../ParseCAN')

import scipy.io
import numpy as np
from copy import deepcopy
from pathlib import Path
from ParseCAN import spec, data

from log_parsers import *

car = spec.car('../MY18/can_spec_my18.yml')


def msg_to_row(msg):
    tup = list(msg.items())
    tup = sorted(tup)

    keys, values = list(zip(*tup))

    return keys, values


def log_to_listdict(logfile, parser, time=True):
    logfile = Path(logfile)

    log = data.log(logfile, parser)
    unp = log.unpack(car, raw=True)

    listdict = {}

    for frame, parsed in unp:
        if not parsed:
            continue

        for msgnm, msg in parsed['can0'].items():
            keys, values = msg_to_row(msg)

            if msgnm not in listdict:
                if time:
                    keys = ('time',) + keys

                listdict[msgnm] = (keys, [])

            if time:
                t = frame.time.to('ms').magnitude
                values = (t,) + values

            listdict[msgnm][1].append(values)

    return listdict


def listdict_to_vecdict(listdict, raw=True):
    vecdict = {}

    for msgnm, (keys, values) in listdict.items():
        cols = list(zip(*values))

        if msgnm not in vecdict:
            vecdict[msgnm] = {key: None for key in keys}

        for i, key in enumerate(keys):
            arr = np.array(cols[i])

            # TODO: Add units support here.
            #       Need to overhaul msgnm so as to point to the message type.

            vecdict[msgnm][key] = arr

    return vecdict


def vecdict_to_matdict(vecdict):
    matdict = {}

    for msgnm, vecs in vecdict.items():
        title = tuple(vecs.keys())
        matdict[msgnm] = (title, np.hstack(vecs[k] for k in title))

    return matdict


def interp_vecdict(timeseries, vecdict):
    intdict = {}
    intdict['time'] = timeseries

    for msgnm, vecs in vecdict.items():
        if 'time' not in vecs:
            raise ValueError('no time data given in all of vecdict')

        old_time = vecs['time']
        intdict[msgnm] = {}

        for vecnm, vec in vecs.items():
            if vecnm == 'time':
                continue

            try:
                interp = np.interp(timeseries, old_time, vec, left=0, right=0)
            except TypeError:
                continue

            intdict[msgnm][vecnm] = interp

    return intdict


def stack_vecdict(*vecdicts):
    if len(vecdicts) == 0:
        return

    fvecdict = vecdicts[0]
    res = {}

    for msgnm in fvecdict:
        res[msgnm] = {}

        if not isinstance(fvecdict[msgnm], dict):
            gen = list(vecdict[msgnm] for vecdict in vecdicts)
            res[msgnm] = np.hstack(gen)
            continue

        for vecnm in fvecdict[msgnm]:
            gen = (vecdict[msgnm][vecnm] for vecdict in vecdicts)
            res[msgnm][vecnm] = np.hstack(gen)

    return res


if __name__ == '__main__':
    specific = r'20180521\192147.TSV'
    logfile = Path(r'C:\Users\nistath\Dropbox (MIT)\FSAE\Data\Raw\\' + specific)

    ad = log_to_listdict(logfile, tsvlog_parser)
    l = listdict_to_vecdict(ad)
    a = np.linspace(0, 180e3, 100)
    hh = interp_vecdict(a, l)
