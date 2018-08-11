import sys
sys.path.append('../ParseCAN')

import yaml
from yaml import SafeDumper
import ParseCAN as pcn
from ParseCAN.spec import *
from collections import OrderedDict

car = pcn.spec.Car.from_yaml(open('examples/can_spec_my18.yml', 'r'))
print(car)
print('OK')

d = pcn.plural.asdict(car, dict_factory=OrderedDict)


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


def dict_representer(dumper, data):
    return dumper.represent_dict(data.items())


SafeDumper.add_representer(OrderedDict, dict_representer)


def dump(d, stream):
    return yaml.dump(d, stream, Dumper=SafeDumper, default_flow_style=False)


clean(d['buses'])
clean(d['boards'])
dump(d, open('dump.yml', 'w'))
