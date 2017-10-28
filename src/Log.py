import csv
from pathlib import Path
import parse
from CANMessage import DAQMessage

class Log:
    def __init__(self, source):
        self.src = Path(source)

    def __iter__(self):
        return (DAQMessage(**parse.log(line)) for line in open(self.src, 'r') if not line.startswith('#'))

    def csv(self, outpath):
        '''
        Outputs a csv representation of the log in outpath.
        '''
        csvfile = outpath.open('w', newline='')
        writer = csv.writer(csvfile)

        writer.writerow(DAQMessage.attributes)
        for message in self:
            writer.writerow(message)
