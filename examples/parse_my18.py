import sys
sys.path.append('../ParseCAN')

import csv
from pathlib import Path
from itertools import chain
from ParseCAN.examples.ParseCAN_old import spec, data, parse
import numpy as np
from .log_parsers import *

car = spec.car('can_spec_my18.yml')

def log_to_npz(logfile, parser, outfile, dimensionless=False, raw=False, progress_callback=None):
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
        if log.parsed % 1000 == 0 and progress_callback is not None: progress_callback(log.parsed/log.length)
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
    # print(writers)
    np.savez(outfile, **writers)

    return None

def parse_my18(logfile, outfile, progress_callback=None):
    log_to_npz(logfile, tsvlog_parser, outfile, dimensionless=True, progress_callback=progress_callback)

if __name__ == '__main__':

    parse_my18("133202.TSV", "out.npz")
