import yaml
from pathlib import Path
from .. import data, spec, helper


class CarSpec:
    def __init__(self, source, name=''):
        self._source = Path(source)
        self.name = name
        # A mapping of bus names to bus objects.
        self.buses = {}
        # A mapping of board names to board objects.
        self.boards = {}
        self.parse()

    # TODO: Must move to another module
    def parse(self):
        with self._source.open('r') as f:
            prem = yaml.safe_load(f)

        self.name = prem['name']

        buses = prem['buses']
        for busnm in buses:
            try:
                self.upsert_bus(spec.bus(name=busnm, **buses[busnm]))
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

                # Prepare filtered bus representation
                kwargs['publish'] = {busnm: spec.busFiltered(self.buses[busnm], kwargs['publish'][busnm]) for busnsm in kwargs['publish']}
                kwargs['subscribe'] = {busnm: spec.busFiltered(self.buses[busnm], kwargs['subscribe'][busnm]) for busnsm in kwargs['publish']}
                try:
                    self.upsert_board(spec.board(name=brdnm, **kwargs))
                except Exception as e:
                    e.args = (
                        'in spec {}: in board {}: {}'.format(
                            self.name,
                            brdnm,
                            e
                        ),
                    )

                    raise

    def upsert_bus(self, bus: spec.bus) -> bool:
        assert isinstance(bus, spec.bus)
        rep = helper.dict_key_populated(self.buses, bus.name, bus)
        self.buses[bus.name] = bus

        return rep

    def upsert_board(self, board: spec.board) -> bool:
        assert isinstance(board, spec.board)
        rep = helper.dict_key_populated(self.boards, board.name, board)
        self.boards[board.name] = board

        return rep

    def get_message_coordinate_by_str(self, msgstr: str):
        '''
        Given a string in the format `<bus_name>/<message_name>`
        return the corresponding spec.bus, spec.message pair in this car.
        '''
        assert isinstance(msgstr, str)
        part = msgstr.split('/')

        return (self.buses[part[0]], self.buses[part[0]].get_message_by_name(part[1]))

    def interpret(self, message):
        '''
        Interprets a data.message instance based on this spec.can.
        '''
        assert isinstance(message, data.message)
        return self.get_message(message).interpret(message)
