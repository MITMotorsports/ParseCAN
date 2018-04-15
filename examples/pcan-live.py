import can
from ParseCAN import spec, data

car = spec.car('../../MY18/can_spec_my18.yml')
bus = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate=500000)


def bitstr(bytes):
    return int.from_bytes(bytes, byteorder='big', signed=False)


def msg_conv(msg):
    return data.message(can_id=msg.arbitration_id, data=bitstr(msg.data))


black_list = [0xD8, 0xF0]
black_list.extend(range(0x521, 0x525))
print('Ignoring the following: ', black_list)

white_list = [0xD0]
raw_list = [0xD4]

try:
    for msg in bus:
        can_id = msg.arbitration_id
        if can_id in black_list or can_id not in white_list:
            continue

        print(hex(msg.arbitration_id), hex(msg_conv(msg).data))

        if msg.arbitration_id in raw_list:
            continue  # raw
        try:
            msg = car.unpack(msg_conv(msg))['can0']
            print(msg)

        except KeyError:
            print('Unknown message.')

except KeyboardInterrupt:
    pass
