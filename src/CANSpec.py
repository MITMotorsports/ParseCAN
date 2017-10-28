import yaml
from pathlib import Path
from MessageType import MessageType
from CANMessage import CANMessage

class CANSpec:
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
            self.upsert_messagetype(MessageType(name=msgnm, **prem[msgnm]))

        return self.messages

    def get_messagetype(self, msg):
        '''
        Given a CANMessage or a MessageType return the corresponding
        MessageType in self CANSpec.
        '''
        assert isinstance(msg, (CANMessage, MessageType))
        print(msg)
        return self.messages[msg.can_id]

    def upsert_messagetype(self, msgtype):
        '''
        Attach, via upsert, a MessageType to self CANSpec.
        '''
        assert isinstance(msgtype, MessageType)
        self.messages[msgtype.can_id] = msgtype

    def interpret(self, message):
        '''
        Interprets a CANMessage instance based on self CAN specification.
        '''
        assert isinstance(message, CANMessage)
        return self.get_messagetype(message).interpret(message)
