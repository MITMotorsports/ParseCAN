import csv
from pathlib import Path
from .. import data, parse


class Log:
    def __init__(self, source, parser):
        self.src = Path(source)
        self.parser = parser

    def __iter__(self):
        return filter(bool, map(self.parser, self.src.open()))

    def unpack(self, spec):
        return ((msg, msg.unpack(spec)) for msg in self)

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
