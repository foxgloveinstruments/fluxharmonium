"""
Simple serial test
"""

from itertools import chain
import serial

port = '/dev/ttyACM1'

try:
    channel = serial.Serial(port)
    channel.timeout = 0.05
except (EOFError, KeyboardInterrupt):
    sys.exit()
    

dac_values = [[3,2,1], [6,57,4]]
    
byte_values = bytes(list(chain.from_iterable(dac_values)))
    
channel.write(byte_values)
channel.write(b"\r\n")