from itertools import chain
from pathlib import Path
import ParseCAN


class Race:
    def __init__(self, srcpath, outdir=None, srcsuff='.log'):
        '''
        Expects a path to the files in the form of a string or a pathlib.Path.
        Expects an outdir in the same format.
        srcsuff: suffix of log files
        '''
        self.srcdir = Path(srcpath)
        self.srcsuff = srcsuff
        self.outdir = Path(outdir) if outdir else self.srcdir.joinpath('out')

    def logfiles(self):
        return self.srcdir.glob('*' + self.srcsuff)

    def __iter__(self):
        '''
        Returns a generator of Log objects within self.srcdir.
        '''
        return (ParseCAN.data.log(logfile) for logfile in self.logfiles())

    def _iter_messages(self):
        return chain.from_iterable(self)
    messages = property(fget=_iter_messages, doc='All the messages in a race.')

    def interpret(self, spec):
        return chain.from_iterable(msg.interpret(spec) for msg in self)

    # def __getattr__(self, index):
    #     '''
    #     Returns the log file with index i.
    #     '''
    #     raise NotImplementedError

    def csv(self, outdir=None):
        '''
        Outputs csv files of each log into outdir/csv.
        '''
        outdir = Path(outdir) if outdir else self.outdir.joinpath('csv')

        if not outdir.exists():
            outdir.mkdir()

        for log in self:
            log.csv(outdir.joinpath(log.src.stem + '.csv'))