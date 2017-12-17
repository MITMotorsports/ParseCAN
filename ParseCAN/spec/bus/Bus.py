from ... import data, spec, meta, helper
from typing import Sequence, Union


class BusSpec:
    '''
    A (CAN) bus specification.
    Describes the set of messages that flow through a CAN bus.
    Can interpret CAN Messages that were sent based on this spec.bus.
    '''
    def __init__(self, name, is_extended=None, messages=None):
        self.name = name
        self.is_extended = is_extended
        self._msg_name = {}
        '''Mapping from message `names` to `spec.message`'''
        self._msg_id = {}
        '''Mapping from message `can_id` to `spec.message`'''

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

    @property
    def messages(self):  # Iterable[spec.message]:
        return self._msg_id.values()

    def get_message(self, msg: meta.message):  # spec.message:
        assert isinstance(msg, meta.message)
        return self._msg_name[msg.name] or self._msg_id[msg.can_id]

    def get_message_by_name(self, name: str):
        return self._msg_name[name]

    def get_message_by_id(self, i: int):
        return self._msg_id[i]

    def upsert_message(self, msgtype) -> bool:
        assert isinstance(msgtype, spec.message)
        rep = (helper.dict_key_populated(self._msg_name, msgtype.name, msgtype)
               or helper.dict_key_populated(self._msg_id, msgtype.can_id, msgtype))
        self._msg_name[msgtype.name] = msgtype
        self._msg_id[msgtype.can_id] = msgtype

        return rep

    def interpret(self, message):
        '''
        Interprets a data.message instance based on this spec.can.
        '''
        assert isinstance(message, data.message)
        return self.get_message(message).interpret(message)


class BusSpecFiltered(BusSpec):
    def __init__(self, bus: BusSpec, interests: Sequence[Union[int, str]]):
        self.bus = bus
        self.interests = interests

    def interested(self, msg):
        return msg.name in self.interests or msg.can_id in self.interests

    @property
    def messages(self):
        return (msg for msg in self.bus.messages if self.interested(msg))

    def get_message(self, msg):
        msg = self.bus.get_message(msg)
        if self.interested(msg):
            return msg

        raise KeyError('mapping exists but is not in interests')

    def get_message_by_id(self, i):
        msg = self.bus.get_message_by_id(i)
        if self.interested(msg):
            return msg

        raise KeyError('mapping exists but is not in interests')

    def get_message_by_name(self, name):
        msg = self.bus.get_message_by_name(name)
        if msg.name in self.interests or msg.can_id in self.interests:
            return msg

        raise KeyError('mapping exists but is not in interests')

    def upsert_message(self, msgtype):
        return self.bus.upsert_message(msgtype)
