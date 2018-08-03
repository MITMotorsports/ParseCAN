import csv
from pathlib import Path
from itertools import chain
from ParseCAN import spec, data, parse

from log_parsers import *

car = spec.car('can_spec_my18.yml')


def log_to_csv(logfile, parser, outpath, dimensionless=False, raw=False):
    logfile = Path(logfile)
    outpath = Path(outpath).joinpath('newcsv').joinpath(logfile.stem)
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
                writers[msg].writerow(chain(['time'], parsed['can0'][msg].keys()))

            values = map(outfn, parsed['can0'][msg].values())
            writers[msg].writerow(chain([raw.time], values))

    return None


if __name__ == '__main__':
    specific = '20180601'
    logdir = Path(r'C:\Users\nicks\Dropbox (MIT)\FSAE\Data\Raw\\' + specific)
    outdir = Path(r'C:\Users\nicks\Dropbox (MIT)\FSAE\Data\\' + specific)

    for logfile in Path(logdir).glob('**/*.tsv'):
        print('Parsing {}'.format(logfile))

        outpath = outdir.joinpath(logfile.parent.relative_to(logdir))

        # Use your parser here
        log_to_csv(logfile, tsvlog_parser, outpath, dimensionless=True)
