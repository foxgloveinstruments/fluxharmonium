"""
fluxharmonium MIDI and envelope processing.
Sends final DAC values to rp2040 for applying to SPI DACs using usb_cdc 

See https://github.com/Neradoc/circuitpython-sample-scripts/blob/main/usb_serial/serial_send-host.py for sending
See https://github.com/Neradoc/circuitpython-sample-scripts/blob/main/usb_serial/serial_send_data-code.py for receiving on the rp2040 side


# To send data to the rp2040 the dac_values need to be flattened and made into a bytes list.

from itertools import chain

dac_values = [[255, 133, 122], [255, 128, 65]]
bytes_values = bytes(list(chain.from_iterable(dac_values)))

print(f'in bytes: {bytes_values}')

dependancies:
  mido
  itertools
  serial
"""

from itertools import chain
import config
import mido
import serial


class FluxProcessor:
  __init__(self):
    self.midi_port = config.MIDI_PORT
    self.midi_in = None

    self.serial_port = config.SERIAL_PORT
    self.channel = None

    self.dac_values = []

  run(self):
    if self.serial_port:
      self.start_serial(self.serial_port)
    if self.midi_port:
      self.start_midi(self.midi_port)

  start_serial(self, port):
    try:
      self.channel = serial.Serial(port)
      self.channel.timeout = 0.05
    except (EOFError, KeyboardInterrupt):
      sys.exit()
    
  start_midi(self, port):
    try:
      self.midiin = mido.open_input(port, callback=self.parse_midi)
    except (EOFError, KeyboardInterrupt):
      sys.exit()

  parse_midi(self, msg):
    if msg.type == 'note_on':
      pass
    elif msg.type == 'note_off':
      pass
    elif msg.type == 'control_change':
      pass
    elif msg.type == 'aftertouch':
      pass
    elif msg.type == 'polytouch':
      pass
  
  send_dac_values(self):
    bytes_values = bytes(list(chain.from_iterable(self.dac_values)))
    
    channel.write(byte_values)
    channel.write(b"\r\n")
    

def main():
  fluxprocessor = FluxProcessor()
  fluxprocessor.run()

if __name__ == '__main__':
  main()

