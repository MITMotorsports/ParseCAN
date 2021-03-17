import csv
from pathlib import Path
from .. import data, parse


class Log:
    def __init__(self, source, parser):
        self.src = Path(source)
        self.parser = parser
        self.length = 0
        self.parsed = 0
        with self.src.open('r') as f:
            for l in f:
                self.length += 1

    def __iter__(self):
        '''
        Returns an iterator of the valid outputs of self.parser.
        '''
        def parse_progress(line):
            self.parsed += 1
            return self.parser(line)
        return filter(bool, map(parse_progress, self.src.open('r')))

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
