import csv
from pathlib import Path
from .. import data, parse


class Log:
    def __init__(self, source, parser):
        self.src = Path(source)
        self.parser = parser

    def __iter__(self):
        '''
        Returns an iterator of the valid outputs of self.parser.
        '''
        return filter(bool, map(self.parser, self.src.open()))

    def unpack(self, spec, **kwargs):
        return ((msg, spec.unpack(msg, **kwargs)) for msg in self)

    def csv(self, outpath):
        '''
        Outputs a csv representation of the log in outpath.
        '''
        outpath = Path(outpath)
        csvfile = outpath.open('w', newline='')
        writer = csv.writer(csvfile)

        writer.writerow(data.FrameTimed.attributes)
        for message in self:
            writer.writerow(message)
