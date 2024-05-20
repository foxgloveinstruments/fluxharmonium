
""" 
Receives DAC values over usb_cdc and applies them to the SPI DACs
"""

import time
import usb_cdc

import control_loop

from note_map import *
from config import *
import dacs
import serial_cdc
DEBUG = False

if DEBUG:
    print("fluxharmonium")

dac_values = [
            [255, 255, 255, 255, 255, 255, 255, 255],
            [255, 255, 255, 255, 255, 255, 255, 255],
            [255, 255, 255, 255, 255, 255, 255, 255],
            [255, 255, 255, 255, 255, 255, 255, 255],
            [255, 255, 255, 255, 255, 255, 255, 255],
            [255, 255, 255, 255, 255, 255, 255, 255],
            [255, 255, 255, 255, 255, 255, 255, 255],
            [255, 255, 255, 255, 255, 255, 255, 255],
            [255, 255, 255, 255, 255, 255, 255, 255],
            [255, 255, 255, 255, 255, 255, 255, 255],
            [255, 255, 255, 255, 255, 255, 255, 255],
            [255, 255, 255, 255, 255, 255, 255, 255],
        ]

# Prepare the DACs (super rough)
dacs = dacs.DACs(CONTROL_RATE, dac_values)

# Prepare the serial
serial = serial_cdc.SerialCDC(CONTROL_RATE, dac_values)

cl = control_loop.ControlLoop(CONTROL_RATE)

cl.add_control(dacs.run())
cl.add_control(serial.run())

cl.run()
