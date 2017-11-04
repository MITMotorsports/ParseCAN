import csv
from pathlib import Path
from ParseCAN import data, parse

class Log:
    def __init__(self, source):
        self.src = Path(source)

    def __iter__(self):
        return (data.messageTimed(**parse.log(line)) for line in open(self.src, 'r') if not line.startswith('#'))

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
