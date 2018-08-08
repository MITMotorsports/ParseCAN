import sys
sys.path.append('../ParseCAN')

import ParseCAN as pcn
from ParseCAN.spec import *

car = pcn.spec.Car.from_file('examples/can_spec_my18.yml')
print(car)
print('OK')

from dataclasses import asdict

d = asdict(car)
