import yaml
from pathlib import Path
from .. import data, spec, plural


class CarSpec:
    def __init__(self, source, name=''):
        self._source = Path(source)
        self.name = name
        # A mapping of bus names to bus objects.
        self.__buses = plural.unique('name', type=spec.bus)
        # A mapping of board names to board objects.
        self.__boards = plural.unique('name', type=spec.board)
        self.parse()

    # TODO: Must move to another module
    def parse(self):
        with self._source.open('r') as f:
            prem = yaml.safe_load(f)

        self.name = prem['name']

        buses = prem['buses']
        for busnm in buses:
            try:
                self.buses.safe_add(spec.bus(name=busnm, **buses[busnm]))
            except Exception as e:
                e.args = (
                    'in spec {}: in bus {}: {}'.format(
                        self.name,
                        busnm,
                        e
                    ),
                )

                raise

        boards = prem['boards']
        for brdnm in boards:
            if isinstance(boards[brdnm], dict):
                kwargs = boards[brdnm]

                try:
                    # Prepare filtered bus representation
                    if kwargs.get('publish', None):
                        kwargs['publish'] = [spec.busFiltered(self.buses.name[busnm], kwargs['publish'][busnm]) for busnm in kwargs['publish']]

                    if kwargs.get('subscribe', None):
                        kwargs['subscribe'] = [spec.busFiltered(self.buses.name[busnm], kwargs['subscribe'][busnm]) for busnm in kwargs['subscribe']]

                    self.boards.add(spec.board(name=brdnm, **kwargs))
                except Exception as e:
                    e.args = (
                        'in spec {}: in board {}: {}'.format(
                            self.name,
                            brdnm,
                            e
                        ),
                    )

                    raise

    @property
    def buses(self):
        return self.__buses

    @property
    def boards(self):
        return self.__boards

    def get_message_coordinate_by_str(self, msgstr: str):
        '''
        Given a string in the format `<bus_name>/<message_name>`
        return the corresponding spec.bus, spec.message pair in this car.
        '''
        assert isinstance(msgstr, str)
        part = msgstr.split('/')
        bus = self.buses['name'][part[0]]

        return (bus, bus['name'][part[1]])

    def unpack(self, frame):
        '''
        unpacks a data.message instance based on this spec.can.
        '''
        assert isinstance(frame, data.message)

        ret = {}
        # TODO: Make this a comprehension.
        # TODO: Make busFiltered interests receptive to message type objects.
        for bus in self.buses:
            msgs = list(spec.busFiltered(bus, [frame.can_id]).messages)

            if msgs:
                ret[bus.name] = [msg.unpack(frame) for msg in msgs]

        return ret
