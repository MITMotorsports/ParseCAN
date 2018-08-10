import sys
sys.path.append('../ParseCAN')

import yaml
import ParseCAN as pcn
from ParseCAN.spec import *
from collections import OrderedDict

car = pcn.spec.Car.from_yaml(open('examples/can_spec_my18.yml', 'r'))
print(car)
print('OK')

d = pcn.plural.asdict(car)


def clean(d):
    if not isinstance(d, dict):
        return d

    if 'name' in d:
        del d['name']

    keys = tuple(d.keys())
    for k in keys:
        if d[k]:
            clean(d[k])
        else:
            del d[k]

    return d


def dump(filename='dump.yml'):
    yaml.safe_dump(d, open(filename, 'w'))
