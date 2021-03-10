import sys
sys.path.append('../ParseCAN')

import csv
from pathlib import Path
from itertools import chain
from ParseCAN import spec, data, parse
import numpy as np
from log_parsers import *

car = spec.car('can_spec_my18.yml')

def log_to_npz(logfile, parser, outfile, dimensionless=False, raw=False):
    logfile = Path(logfile)

    log = data.log(logfile, parser)
    unp = log.unpack(car, raw=raw)

    if dimensionless:
        def outfn(x):
            if isinstance(x, parse.ureg.Quantity):
                try:
                    x = x.to_base_units().magnitude
                except KeyError:
                    x = x.magnitude

            return x
    else:
        outfn = str

    def get_type(v):
        # print(v)
        if type(v) is int: return np.int64
        if type(v) is float: return np.float64
        if type(v) is bool: return np.bool8
        return np.string_
    writers = {}
    dtypes = {}
    for raw, parsed in unp:
        if not parsed:
            continue

        for msg in parsed['can0']:
            if msg not in writers:
                # print(msg)
                # writers[msg] = np.append(np.array([[]]), [tuple(list(chain(['time'], parsed['can0'][msg].keys())))])
                
                writers[msg] = []
                dtypes[msg] = parsed['can0'][msg].keys()
                # outfile = outpath.joinpath(msg).with_suffix('.csv').open('w', newline='')
                # writers[msg] = csv.writer(outfile)
                # writers[msg].writerow(chain(['time'], parsed['can0'][msg].keys()))

            values = map(outfn, parsed['can0'][msg].values())
            writers[msg].append(tuple(chain([raw.time], values)))
    for msg in writers:
        row = writers[msg][0]

        z = zip(chain(['time'], dtypes[msg]), row)
        z1 = zip(chain(['time'], dtypes[msg]), row)

        dtype = [(k, get_type(v)) for k, v in z]
        dtypes[msg] = dtype

        arr = np.array(writers[msg], dtypes[msg])
        arr.dtype.names = [x[0] for x in dtypes[msg]]
        writers[msg] = arr
    # print([list(x) for x in writers.values()])

    np.savez(outfile, **writers)
    return None

def parse_my18(logfile, outfile):
    log_to_npz(logfile, tsvlog_parser, outfile, dimensionless=True)

if __name__ == '__main__':

    log_to_npz("133202.TSV", tsvlog_parser, 'out/', dimensionless=True)
