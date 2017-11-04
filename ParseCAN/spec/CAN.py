import yaml
from pathlib import Path
from ParseCAN import data, spec, meta

class CANSpec:
    '''
    A CAN specification.
    Describes the set of messages that flow through a CAN bus.
    Can interpret CAN Messages that were sent based on this specification.
    '''
    def __init__(self, source):
        self._source = Path(source)
        # A mapping of a message type's can_id to said message type.
        self.messages = {}
        self.parse()

    def parse(self):
        with self._source.open('r') as f:
            prem = yaml.safe_load(f)

        for msgnm in prem:
            # TODO: Generalize this in parse module.
            self.upsert_message(spec.message(name=msgnm, **prem[msgnm]))

        return self.messages

    def get_message(self, msg):
        '''
        Given a Message or a MessageSpec return the
        corresponding MessageSpec in self Spec.
        '''
        assert isinstance(msg, meta.message)
        print(msg)
        return self.messages[msg.can_id]

    def upsert_message(self, msgtype):
        '''
        Attach, via upsert, a MessageSpec to this CAN specification.
        '''
        assert isinstance(msgtype, spec.message)
        self.messages[msgtype.can_id] = msgtype

    def interpret(self, message):
        '''
        Interprets a data.message instance based on this CAN specification.
        '''
        assert isinstance(message, data.message)
        return self.get_message(message).interpret(message)
