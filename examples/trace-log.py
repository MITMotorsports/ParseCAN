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


def log_to_csv(logfile, parser, outpath):
    logfile = Path(logfile)
    outpath = Path(outpath).joinpath(logfile.name)
    outpath.mkdir(exist_ok=True)

    log = data.log(logfile, parser)
    unp = log.unpack(car)

    writers = {}

    for raw, parsed in unp:
        if not parsed:
            continue

        for msg in parsed['can0']:
            if msg not in writers:
                outfile = outpath.joinpath(msg).with_suffix('.csv').open('w', newline='')
                writers[msg] = csv.writer(outfile)
                writers[msg].writerow(chain(['time'], parsed['can0'][msg].keys()))

            values = (str(x) for x in parsed['can0'][msg].values())
            writers[msg].writerow(chain([raw.time], values))

    return None


logpath = r'C:\Users\nistath\Desktop\Logs'
outpath = r'C:\Users\nistath\Desktop\Logs\outs'

for logfile in Path(logpath).glob('*.trc'):
    log_to_csv(logfile, pcantrc_parser, outpath)
