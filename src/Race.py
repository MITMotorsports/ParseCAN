from pathlib import Path
from MessageType import MessageType
from Log import Log

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

    def __iter__(self):
        '''
        Returns a generator of Log objects within self.srcpath.
        '''
        return (Log(logfile) for logfile in self.srcdir.glob('*' + self.srcsuff))

    def __getattr__(self, index):
        '''
        Returns the log file with index i.
        '''


    def csv(self, outdir=None):
        '''
        Outputs csv files of each log into outdir/csv.
        '''
        outdir = Path(outdir) if outdir else self.outdir.joinpath('csv')

        if not outdir.exists():
            outdir.mkdir()

        for log in self:
            log.csv(outdir.joinpath(log.src.stem + '.csv'))
