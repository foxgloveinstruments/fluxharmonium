
""" 
Receives DAC values over usb_cdc and applies them to the SPI DACs
"""

import time
import usb_cdc

import control_loop

from note_map import *
from config import *
import dacs
DEBUG = False

if DEBUG:
    print("fluxharmonium")

# Prepare the DACs (super rough)
dacs = dacs.DACs(CONTROL_RATE, envelope_values, velocity_values)

cl = control_loop.ControlLoop(CONTROL_RATE)

cl.add_control(dacs.run())

cl.run()
