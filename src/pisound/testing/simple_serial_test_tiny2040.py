"""
Receive data using the usb_cdc library
"""

import time
import usb_cdc

serial = usb_cdc.data
# This must be init'd to the proper size to avoid out of range errors
dac_values = [[0,0,0],[0,0,0]]

print('started')

def write_to_dac_values(data):
    group_size = 3
    for index, dac_value in enumerate(data):
        indexA = int(index/group_size)
        indexB = int(index%group_size)
        print(f'index A {indexA} index B {indexB} | {index}:{dac_value}')
        dac_values[indexA][indexB] = int(dac_value)

while True:
    if serial.in_waiting > 0:
        data_in = serial.readline()
        # strip the last 2 bytes which are \r\n
        data = data_in[:-2]
        print(f'data received: {data}')
        write_to_dac_values(data)
        print(f'dac vals: {dac_values}')
        time.sleep(0.2)
