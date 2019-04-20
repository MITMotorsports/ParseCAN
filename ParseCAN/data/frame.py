from . import evil_macros
from dataclasses import dataclass
from typing import T, Union
bitarray = int

__all__ = ['Frame', 'FrameTimed']


@dataclass
class Frame:
    id: int
    data: bytes

    def __getitem__(self, index: Union[int, tuple]) -> bitarray:
        '''
        Returns the bit or range of bits within data.
        '''
        if isinstance(index, int):
            position = index
            length = 1
        elif isinstance(index, tuple):
            position, length = index
        else:
            raise TypeError('index must be int or tuple')

        # Convert bytes to int
        as_int = int.from_bytes(self.data, byteorder='big', signed=False)
        # Shift until 64th bit populated (can also achieve by altering indices)
        as_int = as_int << 8 * (8 - len(self.data))

        return evil_macros.EXTRACT(as_int, position, length)


@dataclass
class FrameTimed(Frame):
    time: T
