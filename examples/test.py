import sys
sys.path.append('../ParseCAN')

import ParseCAN as pcn
from ParseCAN.spec import Bus, Message, Slice, Segment, Enumeration

cr = pcn.spec.Car('examples/can_spec_my18.yml')
print('OK')
copy = eval(repr(cr.buses))
