import sys
sys.path.append('../ParseCAN')

import serial
from xbee import XBee

# To run this script you will need pip package `xbee`


from ParseCAN import spec, data

car = spec.car('../MY18/can_spec_my18.yml')

serial_port = serial.Serial('COM8', 115200)
xbee = XBee(serial_port)


def xframe_to_frame(xframe):
    # Format of xframe
    # {'id': 'rx', 'source_addr': b'\x00\x00',
    #  'rssi': b'(', 'options': b'\x02',
    #  'rf_data': b'\x00\x01\x02\xac\xdc'}

    raw = xframe['rf_data']

    return data.Frame(
                can_id=int.from_bytes(raw[:2], 'big'),
                data=raw[2:]
            )


while True:
    try:
        xframe = xbee.wait_read_frame()
        # print(xframe)

        frame = xframe_to_frame(xframe)
        unp = car.unpack(frame)
        print(unp)
    except KeyboardInterrupt:
        break

serial_port.close()
