from CANSpec import CANSpec
from CANMessage import DAQMessage
from Log import Log

a = CANSpec('../fsae_can_spec.yml')

l = Log('./fakelog.log')
for msg in l:
    print(msg.time, hex(msg.can_id), msg.interpret(a))
