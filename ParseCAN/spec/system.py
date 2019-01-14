import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set

from .. import plural
from .protocol import Protocol
from .computer import Computer
from .computer.participation import Participation

def _computer_constr(self, key, computer):
    try:
        if 'participation' in computer:
            for participationnm, value in computer['participation'].items():
                protocol = self.protocol['name'][participationnm]
                computer['participation'][participationnm] = Participation(name=participationnm, protocol=protocol, **value)

            computer['participation'] = computer['participation'].values()

        return Computer(name=key, **computer)
    except Exception as e:
        e.args = ('in computer {}: {}'.format(key, e),)

        raise

ComputerUnique = plural.Unique[Computer].make('ComputerUnique', ['name'], main='name')

def _computer_pre_add(self, computer, metadata):
    if computer.architecture:
        if computer.architecture not in metadata.architectures:
            raise ValueError(f'in computer {computer.name}: '
                             f'unknown architecture: {computer.architecture}')


_computer_ruleset = plural.RuleSet(dict(add=dict(pre=_computer_pre_add)))


def _protocol_constr(key, protocol):
    try:
        return Protocol(name=key, **protocol)
    except Exception as e:
        e.args = ('in protocol {}: {}'.format(key, e),)

        raise

ProtocolUnique = plural.Unique[Protocol].make('ProtocolUnique', ['name'], main='name')


@dataclass
class System:
    name: str
    architectures: Set[str]
    units: Set[str]
    computer: ComputerUnique = field(default_factory=ComputerUnique)
    protocol: ProtocolUnique = field(default_factory=ProtocolUnique)

    def __post_init__(self):
        protocol = self.protocol
        self.protocol = ProtocolUnique()
        if isinstance(protocol, dict):
            protocol = [_protocol_constr(key, protocol[key]) for key in protocol]

        self.protocol.extend(protocol)

        computer = self.computer
        self.computer = ComputerUnique()
        _computer_ruleset.apply(self.computer, metadata=self)

        if isinstance(computer, dict):
            computer = [_computer_constr(self, key, computer[key]) for key in computer]
        self.computer.extend(computer)

    @classmethod
    def from_yaml(cls, stream):
        spec = yaml.safe_load(stream)
        return cls(**spec)
