"""
Asynio runnable class for listening to MIDI events
"""
import asyncio
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.control_change import ControlChange
from adafruit_midi.midi_message import MIDIUnknownEvent

class MidiMonitor():
    def __init__(self, _in_port, _in_channel, _note_on_function, _note_off_function, _control_change_function, frequency=200, debug=False):
        self.midi = adafruit_midi.MIDI(midi_in=usb_midi.ports[_in_port], in_channel=_in_channel)
        self.note_on_function = _note_on_function
        self.note_off_function = _note_off_function
        self.control_change_function = _control_change_function
        self.frequency = frequency
        self.debug = debug
    
    def freq_to_sec(self, freq):
        return 1000/1000/freq

    async def run(self):
        while True:
            msg = self.midi.receive()
            if isinstance(msg, MIDIUnknownEvent):
                continue
            if msg is not None:
                #  if a NoteOn message...
                if isinstance(msg, NoteOn):
                    self.note_on_function(msg)
                    if self.debug:
                        print(f'received Note On {msg}')
                #  if a NoteOff message...
                elif isinstance(msg, NoteOff):
                    self.note_off_function(msg)
                    if self.debug:
                        print(f'received Note Off {msg}')
                elif isinstance(msg, ControlChange):
                    self.control_change_function(msg)
                    if self.debug:
                        print(f'received Control Change {msg}')
            await asyncio.sleep(self.freq_to_sec(self.frequency))
