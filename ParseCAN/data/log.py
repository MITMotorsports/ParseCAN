from pathlib import Path


class Log:
    # def unpack(self, spec, **kwargs):
    #     return (spec.unpack(msg, **kwargs) for msg in self)
    def unpack(self, spec, include_raw = False, **kwargs):
        def helper():
            for t_frame in self:
                # 223 in intersection
                ret = {}

                can = spec.protocol['name']['can']
                bus_unique = can.bus
                for name in bus_unique['name']:
                    bus = bus_unique['name'][name]
                    frame_map = bus.frame['key']
                    # if t_frame.id == 223:
                    #     print(t_frame.id, bus.frame['key'][223])
                    x = frame_map.get(t_frame.id, None)

                    if x:
                        ret[name] = {x.name: x.unpack(t_frame, **kwargs)}
                    if include_raw:
                        yield (t_frame, ret)
                    else:
                        yield ret

        yield from helper()

    def unpack_pair_raw(self, spec, **kwargs):
        yield from self.unpack(spec, include_raw=True, **kwargs)


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
