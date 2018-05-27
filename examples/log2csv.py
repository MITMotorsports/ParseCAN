import sys
sys.path.append('../ParseCAN')

import csv
from pathlib import Path
from itertools import chain
from ParseCAN import spec, data, parse

from log_parsers import *

car = spec.car('../MY18/can_spec_my18.yml')

# One needs to write a parser that converts a line of the log file to
# a data.Frame object or None if the line does not represent a message


def log_to_csv(logfile, parser, outpath, dimensionless=False, raw=False):
    logfile = Path(logfile)
    outpath = Path(outpath).joinpath(logfile.stem)
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


if __name__ == '__main__':
    specific = ''
    logdir = Path(r'C:\Users\nistath\Dropbox (MIT)\FSAE\Data\Raw\\' + specific)
    outdir = Path(r'C:\Users\nistath\Dropbox (MIT)\FSAE\Data\\' + specific)

    for logfile in Path(logdir).glob('**/*.tsv'):
        print('Parsing {}'.format(logfile))

        outpath = outdir.joinpath(logfile.parent.relative_to(logdir))
        log_to_csv(logfile, tsvlog_parser, outpath, dimensionless=True)
