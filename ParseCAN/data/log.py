from pathlib import Path
import ParseCAN as pcn

class Log:
    def unpack(self, spec, include_raw=False, **kwargs):
        for t_frame in filter(bool, self):
            # TEMPORARY. Testing with incomplete spec!
            # Remove check and throw error in final version!
            if t_frame.id in t_frame.bus.frame['key']:
                # Could just implement unpack in data.Frame
                unp = t_frame.bus.unpack(t_frame, **kwargs)
                msg_nm = [t_frame.bus.name]
                while isinstance(unp, tuple):
                    msg_nm.append(unp[0].name)
                    unp = unp[1]

                msg_nm = '__'.join(msg_nm)

                if include_raw:
                    yield (msg_nm,
                           unp,
                           t_frame)
                else:
                    yield (msg_nm,
                           unp)
            # else:
            #     print('id {} not in spec'.format(t_frame.id))


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
