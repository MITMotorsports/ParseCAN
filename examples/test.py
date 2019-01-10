import sys
sys.path.append('../ParseCAN')

import yaml
from yaml import SafeDumper
import ParseCAN as pcn
from ParseCAN.spec import *
from enum import Enum
from collections import OrderedDict
from pprint import pprint

system = pcn.spec.System.from_yaml(open('examples/example_can_spec.yml', 'r'))
print(system)

oldD = pcn.plural.asdict(system, dict_factory=OrderedDict)


def compact_dict(items, dict_factory=OrderedDict):
    ret = dict_factory()

    for k, v in items:
        if isinstance(v, Slice):
            v = str(v)
        if isinstance(v, Atom):
            unit = ' | '.join(v.unit)
            pipe = [str(v.slice), str(v.type), unit]
            v = ' | '.join(pipe)

        ret[k] = v

    return ret


d = pcn.plural.asdict(system, dict_factory=compact_dict)


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


def endianness_representer(dumper, data):
    return dumper.represent_str(data.value)


noalias_dumper = yaml.dumper.SafeDumper
noalias_dumper.ignore_aliases = lambda self, data: True
SafeDumper.add_representer(OrderedDict, dict_representer)
SafeDumper.add_multi_representer(Endianness, endianness_representer)


def dump(d, stream):
    return yaml.dump(d, stream, Dumper=SafeDumper, default_flow_style=False)


dump(d, open('examples/dump.yml', 'w'))
