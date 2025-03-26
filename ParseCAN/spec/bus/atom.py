from dataclasses import dataclass, field

from ... import parse
from ...helper import Slice
from .type import Type
# from ...data.frame import Frame # circular import with FrameBus

# TODO: Figure out why this breaks dict generation.
# class Unit(str):
#     def pint(self):
#         return parse.ureg[self]
Unit = str

@dataclass
class Atom:
    name: str
    slice: Slice
    type: Type = ''
    unit: Unit = field(default_factory=Unit)

    mirror_bus: str = None
    mirror_frame: str = None
    mirror_atom: str = None

    def __post_init__(self):
        self.slice = Slice.from_general(self.slice)
        if self.slice.start < 0 or self.slice.stop > 64:
            raise ValueError(f'{self.slice} out of bounds')
        
        assert (self.mirror_frame is None) == (self.mirror_bus is None) == (self.mirror_atom is None), f"Mirror atoms have to specify a frame, a bus, and an atom! ({self.name})"

        # TODO: Get a multiple dispatch here too.
        if self.mirror_frame is None:
            if isinstance(self.type, str):
                self.type = Type.from_str(self.type)
            elif isinstance(self.type, dict):
                self.type = Type.from_dict(self.type)
            elif not isinstance(self.type, Type):
                raise ValueError('unparseable type: {}'.format(self.type))
        else:
            assert self.mirror_frame is not None

    def resolve_mirrors(self, system):
        if self.mirror_frame is not None and self.mirror_bus is not None and self.mirror_atom is not None:
            if self.mirror_bus in system.protocol['name']['can'].bus['name']:
                bus = system.protocol['name']['can'].bus['name'][self.mirror_bus]
                if self.mirror_frame in bus.frame['name']:
                    selected_frame = bus.frame['name'][self.mirror_frame]
                    if self.mirror_atom in selected_frame.atom['name']:
                        selected_atom = selected_frame.atom['name'][self.mirror_atom]
                        if isinstance(selected_atom, Atom) and selected_atom.mirror_frame is None:
                            self.type = selected_atom.type
                            self.unit = selected_atom.unit
                            return
            assert False, f"Unable to find mirror {self.mirror_frame} for atom {self.name}!"
        
    def validate_slice(self):
        if self.slice.length < self.type.bits():
            if self.type.isenum():  # is annoying for anything other than enum
                raise ValueError(f'have {self.slice.length} and need {self.type.bits()} '
                                 f'bits to represent {self.type}')

        if self.slice.length > self.type.bits():
            raise ValueError('slice allocated is bigger than type expressed')

    @classmethod
    def from_str(cls, name, string, **kwargs):
        '''
        Constructs an instance from a string of format
        `START + LEN | RAWTYPE | *SCALE | -OFFSET | *UNIT`
        `LEN | RAWTYPE | TYPE | *SCALE | -OFFSET | log10 | exp2 | *UNIT`
        '''
        pipe = string.split('|')
        # TODO: change unit to *unit when you convert it to a list thing
        slice, type, unit = map(str.strip, pipe)

        return cls(name=name, slice=slice, type=type, unit=unit, **kwargs)

    def unpack(self, frame, **kwargs):
        # assert isinstance(frame, Frame)

        raw = frame[self.slice.start, self.slice.length]

        if self.type.isenum():
            try:
                retval = self.type.enum['value'][raw].name
            except KeyError as e:
                e.args = (f'on {self} got exception {e}',)
                raise

            # REMOVED: now return object in frame
            # if kwargs.get('segtuple', False):
            #     return retval, self

            if kwargs.get('unittuple', False):
                return retval, self.unit

            return retval

        clean = self.type.clean(raw)
        if kwargs.get('segtuple', False):
            return clean, self

        return clean
