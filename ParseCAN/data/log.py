from pathlib import Path
import ParseCAN as pcn

class Log:
    def unpack(self, spec, include_raw=False, **kwargs):
        bus_unique = spec.protocol['name']['can'].bus
        for t_frame in self:
            # Temporary -- working with incomplete spec.
            # Should remove check and throw error

            # Probably better to implement unpack on data.Frame
            unp = bus_unique['name'][t_frame.bus].unpack(t_frame, **kwargs)
            msg_nm = [t_frame.bus]
            while isinstance(unp, tuple):
                msg_nm.append(unp[0].name)
                unp = unp[1]

            msg_nm = '.'.join(msg_nm)

            if include_raw:
                yield (msg_nm,
                       unp,
                       t_frame)
            else:
                yield (msg_nm,
                       unp)


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
