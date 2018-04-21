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
               data=int(datastr, 16)
           )


def log_to_csv(logfile, parser, outpath, dimensionless=False):
    logfile = Path(logfile)
    outpath = Path(outpath).joinpath(logfile.name)
    outpath.mkdir(exist_ok=True)

    log = data.log(logfile, parser)
    unp = log.unpack(car)

    if dimensionless:
        def outfn(x):
            if isinstance(x, parse.ureg.Quantity):
                x = x.to_base_units().magnitude
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


logpath = r'C:\Users\nistath\Desktop\420 torque shudder tests'
outpath = r'C:\Users\nistath\Desktop\420 torque shudder tests\outs'

for logfile in Path(logpath).glob('*.trc'):
    log_to_csv(logfile, pcantrc_parser, outpath, dimensionless=True)
