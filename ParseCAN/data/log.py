from pathlib import Path
import ParseCAN as pcn

class Log:
    def unpack(self, spec, include_raw=False, **kwargs):
        # TODO: add multiplex support

        # Precompute which frame and bus each frame_id belongs to
        frames = {}
        buses = {}
        bus_unique = spec.protocol['name']['can'].bus
        for bus_nm in bus_unique['name']:
            frame_unique = bus_unique['name'][bus_nm].frame
            for id in frame_unique['key']:
                frames[id] = frame_unique['key'][id]
                buses[id] = bus_unique['name'][bus_nm]

        for t_frame in self:
            # Temporary -- working with incomplete spec. Should throw error
            if t_frame.id in frames:
                msg_nm = [buses[t_frame.id].name, frames[t_frame.id].name]
                frame_unp = frames[t_frame.id].unpack(t_frame, **kwargs)

                if isinstance(frames[t_frame.id], pcn.spec.frame.MultiplexedFrame):
                    # print('MUXFUX')
                    msg_nm.append(frame_unp[0])
                    frame_unp = frame_unp[1]

                if include_raw:
                    yield ('.'.join(msg_nm),
                            frame_unp,
                            t_frame)
                else:
                    yield ('.'.join(msg_nm),
                            frame_unp,
                            frames[t_frame.id].unpack(t_frame, **kwargs))
            # else:
            #     print('{} not in spec'.format(t_frame.id))


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
