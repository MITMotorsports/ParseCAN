import sys
sys.path.append('../ParseCAN')

import re
import csv
from pathlib import Path
from itertools import chain
from ParseCAN import spec, data, parse

car = spec.car('../MY18/can_spec_my18.yml')

# One needs to write a parser that converts a line of the log file to
# a data.Frame object or None if the line does not represent a message


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


def log_to_csv(logfile, parser, outpath, dimensionless=False, raw=False):
    logfile = Path(logfile)
    outpath = Path(outpath).joinpath(logfile.name)
    outpath.mkdir(parents=True, exist_ok=True)

    log = data.log(logfile, parser)
    unp = log.unpack(car, raw=raw)

    if dimensionless:
        def outfn(x):
            if isinstance(x, parse.ureg.Quantity):
                try:
                    x = x.to_base_units().magnitude
                except KeyError:
                    x = x.magnitude
            elif isinstance(x, bool):
                x = int(x)

            return str(x)
    else:
        outfn = str

    writers = {}

    for raw, parsed in unp:
        if not parsed:
            continue

        for msg in parsed['can0']:
            if msg not in writers:
                outfile = outpath.joinpath(msg).with_suffix('.csv').open('w', newline='')
                writers[msg] = csv.writer(outfile)
                writers[msg].writerow(chain(['time (ms)'], parsed['can0'][msg].keys()))

            values = map(outfn, parsed['can0'][msg].values())
            writers[msg].writerow(chain([raw.time.to('ms').magnitude], values))

    return None


day = 'lol'
logpath = r'C:\Users\nistath\Dropbox (MIT)\FSAE\Data\Raw\\' + day
outpath = r'C:\Users\nistath\Dropbox (MIT)\FSAE\Data\\' + day

for logfile in Path(logpath).glob('*.tsv'):
    log_to_csv(logfile, tsvlog_parser, outpath, dimensionless=True)
