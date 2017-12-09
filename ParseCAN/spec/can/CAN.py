import yaml
from pathlib import Path
from ... import data, spec, meta


class CANSpec:
    '''
    A CAN specification.
    Describes the set of messages that flow through a CAN bus.
    Can interpret CAN Messages that were sent based on this spec.can.
    '''
    def __init__(self, source):
        self._source = Path(source)
        self.name = ''
        self.is_extended = None
        # A mapping of a message type's can_id to said message type.
        self.messages = {}
        self.parse()

    def parse(self):
        with self._source.open('r') as f:
            prem = yaml.safe_load(f)

        self.name = prem['name']
        self.is_extended = prem['is_extended']

        msgs = prem['messages']
        for msgnm in msgs:
            try:
                self.upsert_message(spec.message(name=msgnm, **msgs[msgnm]))
            except Exception as e:
                e.args = (
                    'in spec {}: in message {}: {}'.format(
                        self._source,
                        msgnm,
                        e
                    ),
                )

                raise

        return self.messages

    def get_message(self, msg):
        '''
        Given a meta.message return the
        corresponding spec.message in this spec.can.
        '''
        assert isinstance(msg, meta.message)
        return self.messages[msg.can_id]

    def upsert_message(self, msgtype):
        '''
        Attach, via upsert, a spec.message to this spec.can.
        '''
        assert isinstance(msgtype, spec.message)
        self.messages[msgtype.can_id] = msgtype

    def interpret(self, message):
        '''
        Interprets a data.message instance based on this spec.can.
        '''
        assert isinstance(message, data.message)
        return self.get_message(message).interpret(message)
