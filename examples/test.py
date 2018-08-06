import sys
sys.path.append('../ParseCAN')

import ParseCAN as pcn
from ParseCAN.spec import *
from ParseCAN.plural import Unique

car = pcn.spec.Car.from_file('examples/can_spec_my18.yml')
print(car)
print('OK')
copy = eval(repr(car))

print('Reconstruction success:', repr(copy) == repr(car))

from dataclasses import asdict

d = asdict(car)
