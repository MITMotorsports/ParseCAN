import sys
sys.path.append('../ParseCAN')

import ParseCAN as pcn
# from ParseCAN.spec import Bus, Message, Slice, Segment, Enumeration
from ParseCAN.spec import *
from ParseCAN.plural import Unique

cr = pcn.spec.Car('examples/can_spec_my18.yml')
print(cr.buses)
print('OK')
copy = eval(repr(cr.buses))

print('Reconstruction success:', repr(copy) == repr(cr.buses))