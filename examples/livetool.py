import sys
sys.path.append('../ParseCAN')

from ParseCAN import spec, data
car = spec.car('can_spec_my18.yml')

exit()

bitrate = 500000
interface = 'vector'

providers = {
    'pcan': lambda: can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate=bitrate),
    'ixxat': lambda: can.interface.Bus(bustype='ixxat', channel=0, bitrate=bitrate),
    'vector': lambda: can.interface.Bus(bustype='vector', channel=0, bitrate=bitrate),
}

bus = providers[interface]()

def convert_to_frame(msg):
    return data.Frame(can_id=msg.arbitration_id, data=msg.data)

black_list = [0xD8, 0xF0]
print('Blacklisted:', black_list)

white_list = [0x2FF, 0xDF, 0x521, 0x522]
white_list = []
print('Whitelisted:', white_list)
raw_list = []

try:
    for msg in bus:
        can_id = msg.arbitration_id

        if white_list and can_id not in white_list:
            continue

        if black_list and can_id in black_list:
            continue

        frame = convert_to_frame(msg)

        print(hex(msg.arbitration_id)[2:], bytes(frame.data).hex())

        if msg.arbitration_id in raw_list:
            continue

        msg = car.unpack(frame)
        print(msg)

except KeyboardInterrupt:
    pass
