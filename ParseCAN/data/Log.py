from pathlib import Path


class Log:
    def unpack(self, spec, **kwargs):
        return ((msg, spec.unpack(msg, **kwargs)) for msg in self)


class File(Log):
    ''' A lazy-loaded logfile parser. '''

    def __init__(self, source, parser):
        self.src = Path(source)
        self.parser = parser

    def __iter__(self):
        '''
        Returns an iterator of the valid outputs of self.parser.
        '''
        # TODO: Add fopen method in parser: could use a different delimiter.
        return filter(bool, map(self.parser, self.src.open('r')))


class List(Log, list):
    pass
