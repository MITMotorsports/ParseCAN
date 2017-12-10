from ... import data, spec, meta


class BusSpec:
    '''
    A (CAN) bus specification.
    Describes the set of messages that flow through a CAN bus.
    Can interpret CAN Messages that were sent based on this spec.bus.
    '''
    def __init__(self, name, is_extended=None, messages=None):
        self.name = name
        self.is_extended = is_extended
        # A mapping of a message type's can_id and name to said message type.
        self.messages = {}

        for msgnm in messages:
            if isinstance(messages[msgnm], dict):
                try:
                    self.upsert_message(spec.message(name=msgnm, bus=self, **messages[msgnm]))
                except Exception as e:
                    e.args = (
                        'in message {}: {}'.format(
                            msgnm,
                            e
                        ),
                    )

                    raise
            else:
                messages[msgnm].bus = self
                self.upsert_message(messages[msgnm])

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
        self.messages[msgtype.name] = msgtype

    def interpret(self, message):
        '''
        Interprets a data.message instance based on this spec.can.
        '''
        assert isinstance(message, data.message)
        return self.get_message(message).interpret(message)
