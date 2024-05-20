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

dependencies:
  adsr.py - envelope definition
  config.py - Global Config params
  control_loop.py - asyncio loops
  dacs.py - calculates the correct value for the DAC (velocity*env) 
  envelopes.py - processes envelopes for each note
  note_map.py - maps MIDI notes to tonegenerator outputs

requirements:
  mido
  itertools
  serial
"""

import asyncio
import argparse
from itertools import chain
import logging
import mido
import serial
import sys
import time

from config import *
from note_map import *

import adsr
import control_loop
import dacs
import envelopes as eg


class FluxProcessor:
  def __init__(self):
    self._logger = logging.getLogger('fluxharmonium')  
    
    self.midi_port = MIDI_PORT
    self.midi_in = None

    self.serial_port = SERIAL_PORT
    self.channel = None

    self.velocity_values = [0] * NUMBER_OF_NOTES
    self.envelope_values = [0] * NUMBER_OF_NOTES
    
    self.envelopes = None
    self.dacs = None

    self.last_dacs = None
    
    self.control_loop = control_loop.ControlLoop(self, CONTROL_RATE)
    
    self.running = False

  def initEnvelopes(self):
    self.envelopes = eg.Envelopes(self, CONTROL_RATE, self.envelope_values)
    for e in range(NUMBER_OF_NOTES):
        self.envelopes.add_envelope(adsr.ADSR(0.1, 0.05, 1, 1, CONTROL_RATE))
  
  def initDACs(self):
    self.dacs = dacs.DACs(self, CONTROL_RATE, self.envelope_values, self.velocity_values)
    
  def run(self):
    if self.serial_port:
      self.start_serial(self.serial_port)
    if self.midi_port:
      self.start_midi(self.midi_port)
      # pass

    self.initEnvelopes()
    self.initDACs()
    
    self.running = True
    
    self._logger.info(f'--------------------------')
    self._logger.info(f'fluxharmonium running...')
    self._logger.info(f'--------------------------')

    self._logger.debug(f'{self.control_loop}')

    self.control_loop.add_control(self.envelopes.run())
    self.control_loop.add_control(self.dacs.run())

    self._logger.debug(f'control loops started')
    
    while self.running:
        self._logger.debug(f'running')
        try:
          asyncio.run(self.control_loop.run())
        except KeyboardInterrupt:
          self._logger.info("fluxharmonium terminated...shutting down")
        finally:
          self.control_loop.stop()
          self.midi_in.close()
          self.channel.close()
          sys.exit('see ya next time')
    

  def start_serial(self, port):
    try:
      self._logger.info(f'opening serial port {port}')
      self.channel = serial.Serial(port, 115200, dsrdtr=True)
      self.channel.timeout = 0.05
      self.channel.write_timeout = 0.2
      self._logger.debug(f'serial channel {self.channel}')
      self._logger.debug(f'serial DTR state {self.channel.dtr}')
    except (EOFError, KeyboardInterrupt):
      self._logger.error(f'Serial device {port} failed to initialize')
      sys.exit(1)
    
  def start_midi(self, port):
    try:
      self._logger.info(f'opening MIDI port {port}')

      # mido.set_backend('mido.backends.rtmidi', load=True)
      # mido.set_backend('mido.backends.rtmidi/LINUX_ALSA', load=True)

      self._logger.debug(f'mido backend {mido.backend}')
      self._logger.debug(f'mido available APIs {mido.backend.module.get_api_names()}')
      self._logger.debug(f'MIDI inputs {mido.get_input_names()}')
      

      self.midi_in = mido.open_input(port, callback=self.parse_midi)  
    except (EOFError, KeyboardInterrupt):
      self._logger.error(f'MIDI device {port} failed to initialize')
      sys.exit(1)

  def parse_midi(self, msg):
    # self._logger.debug(f'MIDI message received: {msg}')
    if msg.type == 'note_on':
      self._logger.debug(f'Note On received: {msg}')
      note_index = msg.note - MIDI_LOW_VALUE
      self.velocity_values[note_index] = msg.velocity
      self.envelopes.envelopes[note_index].gate(1)

    elif msg.type == 'note_off':
      self._logger.debug(f'Note Off received: {msg}')
      note_index = msg.note - MIDI_LOW_VALUE
      self.envelopes.envelopes[note_index].gate(0)

    elif msg.type == 'control_change':
      """
      Volume and Envelope settings per note.
      """
      self._logger.debug(f'Control Change received: {msg}')
      if msg.channel == OUT_VOL_CHAN and msg.control >= MIDI_LOW_VALUE:
          # Process Dynamic Volume Control
          control_index = msg.control - MIDI_LOW_VALUE
          self.velocity_values[control_index] = msg.value
      elif msg.channel == ENV_MODE_CHAN and msg.control == ENV_MODE_CTRL:
          # Process Envelope Mode Control
          pass
      elif msg.channel == ENV_ATTACK_CHAN and msg.control >= MIDI_LOW_VALUE:
          # Process Envelope Attack Control
          note_index = msg.control - MIDI_LOW_VALUE
          self.envelopes.envelopes[note_index].update_attack(msg.value/CTRL_SEC_DIV)
      elif msg.channel == ENV_RELEASE_CHAN and msg.control >= MIDI_LOW_VALUE:
          # Process Envelope Release Control
          note_index = msg.control - MIDI_LOW_VALUE
          self.envelopes.envelopes[note_index].update_release(msg.value/CTRL_SEC_DIV)
    elif msg.type == 'aftertouch':
      pass
    elif msg.type == 'polytouch':
      pass
  
  def send_dac_values(self, dac_values):
    byte_values = bytes(list(chain.from_iterable(dac_values)))

    if byte_values != self.last_dacs:
      self.last_dacs = byte_values
      # self._logger.debug(f'serial is open {self.channel.isOpen()}')
      self._logger.debug(f'sending dac values {dac_values}')
      self.channel.reset_output_buffer()
      self._logger.debug(f'outbuffer {self.channel.out_waiting}')
      
      try:
        self.channel.write(byte_values)
        self.channel.write(b'\r\n')
        self._logger.debug(f'finished sending')
      except Exception as e:
        self._logger.error(f'Error sending dac values {e}')

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-v', action='count', dest='verbosity', default=0,
                      help='Increase logging verbosity level (-v or -vv)')
  args = parser.parse_args()
  
  log_level = logging.WARNING
  if args.verbosity == 1:
    log_level = logging.INFO
  elif args.verbosity >= 2:
    log_level = logging.DEBUG
    
  logging.basicConfig(format='[%(levelname)s] {%(filename)s:%(lineno)d} %(message)s', level=log_level)
    
  fluxprocessor = FluxProcessor()
  time.sleep(2)
  fluxprocessor.run()

if __name__ == '__main__':
  main()

