import yaml
from pathlib import Path
from .. import data, spec


class CarSpec:
    def __init__(self, source, name=''):
        self._source = Path(source)
        self.name = name
        # A mapping of bus names to bus objects.
        self.busses = {}
        # A mapping of board names to board objects.
        self.boards = {}
        self.parse()

    # Must move to another module
    def parse(self):
        with self._source.open('r') as f:
            prem = yaml.safe_load(f)

        self.name = prem['name']

        busses = prem['busses']
        for busnm in busses:
            try:
                self.upsert_bus(spec.bus(name=busnm, **busses[busnm]))
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
        boards = {}
        for brdnm in boards:
            if isinstance(boards[brdnm], dict):
                kwargs = boards[brdnm]
                kwargs['publish'][:] = map(self.get_message, kwargs['publish'])
                kwargs['subscribe'][:] = map(self.get_message, kwargs['subscribe'])

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

    def upsert_bus(self, bus):
        assert isinstance(bus, spec.bus)
        self.busses[bus.name] = bus

    def upsert_board(self, board):
        assert isinstance(board, spec.board)
        self.boards[board.name] = board

    def get_message(self, msgstr):
        '''
        Given a string in the format `<bus_name>/<message_name>`
        return the corresponding message in this spec.
        '''
        assert isinstance(msgstr, str)
        part = msgstr.split('/')

        return self.busses[part[0]].messages[part[1]]

    def interpret(self, message):
        '''
        Interprets a data.message instance based on this spec.can.
        '''
        assert isinstance(message, data.message)
        return self.get_message(message).interpret(message)
