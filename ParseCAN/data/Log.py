from pathlib import Path


class Log:
    def unpack(self, spec, **kwargs):
        return ((msg, spec.unpack(msg, **kwargs)) for msg in self)


class File(Log):
    ''' A lazy-loaded logfile parser. '''

    def __init__(self, source, parser):
        self.src = source
        self.parser = parser

    def __iter__(self):
        '''
        Returns an iterator of the valid outputs of self.parser.
        '''
        # TODO: Add fopen method in parser: could use a different delimiter.
        try:
            log = Path(self.src).open('r')
        except TypeError as e:
            log = self.src
        return filter(bool, map(self.parser, log)) 


class List(Log, list):
    pass
