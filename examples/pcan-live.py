import sys
sys.path.append('../ParseCAN')

import can
from ParseCAN import spec, data

car = spec.car('../MY18/can_spec_my18.yml')
bus = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate=500000)


def msg_conv(msg):
    return data.Frame(can_id=msg.arbitration_id, data=msg.data)


black_list = [0xD8, 0xF0]
black_list.extend(range(0x521, 0x525))
print('Blacklisted:', black_list)

white_list = []
print('Whitelisted:', white_list)
raw_list = [0xD4]

try:
    for msg in bus:
        can_id = msg.arbitration_id

        if white_list and can_id not in white_list:
            continue

        if black_list and can_id in black_list:
            continue

        frame = msg_conv(msg)

        print(hex(msg.arbitration_id), hex(frame.data))

        if msg.arbitration_id in raw_list:
            continue  # raw
        try:
            msg = car.unpack(frame)['can0']
            print(msg)

        except KeyError:
            print('Unknown message.')

except KeyboardInterrupt:
    pass
