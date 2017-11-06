import csv
from pathlib import Path
from .. import data, parse


class Log:
    def __init__(self, source):
        self.src = Path(source)

    def __iter__(self):
        return (data.messageTimed(**parse.log(line)) for line in self.src.open() if not line.startswith('#'))

    def interpret(self, spec):
        return (msg.interpret(spec) for msg in self)

    def csv(self, outpath):
        '''
        Outputs a csv representation of the log in outpath.
        '''
        outpath = Path(outpath)
        csvfile = outpath.open('w', newline='')
        writer = csv.writer(csvfile)

        writer.writerow(data.messageTimed.attributes)
        for message in self:
            writer.writerow(message)
