
""" A simple test using the control_loop and midi_monitor modules.

Control Loop sets up a simple asyncio loop with multiple control tasks.
Task 1 is a MIDI Monitor that listens for incoming note on/off messages and executes
a functions for each message.
Task 2 keeps track of and reports gate states.
"""

import usb_midi
import adafruit_midi
import time

import control_loop
import midi_monitor
from note_map import *
from config import *
import adsr
import envelopes
import dacs

if DEBUG:
    print("fluxharmonium")

# print(usb_midi.ports)
midi = adafruit_midi.MIDI(
    midi_in=usb_midi.ports[0], in_channel=0
    )

velocity_values = [0] * NUMBER_OF_NOTES
envelope_values = [0] * NUMBER_OF_NOTES
dac_values = [DAC_STARTUP_VALUE] * NUMBER_OF_NOTES

# Prepare all of the Envelopes
envelopes = envelopes.Envelopes(CONTROL_RATE_SEC, envelope_values)

for e in range(NUMBER_OF_NOTES):
    envelopes.add_envelope(adsr.ADSR(0.5, 0, 1, 0.5, CONTROL_RATE))

if DEBUG:
    print(f'env vals {envelope_values}')
    print(f'vel vals {velocity_values}')

# Prepare the DACs (super rough)
dacs = dacs.DACs(CONTROL_RATE_SEC, dac_values, envelope_values, velocity_values)
# dacs = dacs.DACs(0.5, dac_values, envelope_values, velocity_values)


# MIDI Callbacks
def note_on(msg):
    """
    MIDI Note On callback function.
    Updates velocity and triggers envelope gate.
    """
    if DEBUG:
        print(f'note on {msg}')
    if msg.note >= MIDI_LOW_VALUE and msg.note <= MIDI_HIGH_VALUE:
        note_index = msg.note - MIDI_LOW_VALUE
        velocity_values[note_index] = msg.velocity
        envelopes.envelopes[note_index].gate(1)
    if DEBUG:
        print(f'env vals {envelope_values}')
        # print(f'dac vals {dac_values}')

def note_off(msg):
    """
    MIDI Note Off callback function.
    Turns envelope gate off.
    """
    if DEBUG:
        print(f'note off {msg}')
    if msg.note >= MIDI_LOW_VALUE and msg.note <= MIDI_HIGH_VALUE:
        note_index = msg.note - MIDI_LOW_VALUE
        envelopes.envelopes[note_index].gate(0)
    if DEBUG:
        print(f'env vals {envelope_values}')
        # print(f'dac vals {dac_values}')

def control_change(msg):
    """
    Volume and Envelope settings per note.
    """
    if msg.channel == OUT_VOL_CHAN and msg.control >= MIDI_LOW_VALUE:
        # Process Dynamic Volume Control
        control_index = msg.control - MIDI_LOW_VALUE
        velocity_values[control_index] = msg.value
    elif msg.channel == ENV_MODE_CHAN and msg.control == ENV_MODE_CTRL:
        # Process Envelope Mode Control
        pass
    elif msg.channel == ENV_ATTACK_CHAN and msg.control >= MIDI_LOW_VALUE:
        # Process Envelope Attack Control
        note_index = msg.control - MIDI_LOW_VALUE
        envelopes.envelopes[note_index].update_attack(msg.value/CTRL_SEC_DIV)
    elif msg.channel == ENV_RELEASE_CHAN and msg.control >= MIDI_LOW_VALUE:
        # Process Envelope Release Control
        note_index = msg.control - MIDI_LOW_VALUE
        envelopes.envelopes[note_index].update_release(msg.value/CTRL_SEC_DIV)


cl = control_loop.ControlLoop(CONTROL_RATE_SEC)
mm = midi_monitor.MidiMonitor(0, "ALL", note_on, note_off, control_change, CONTROL_RATE_SEC)

cl.add_control(mm.run())
cl.add_control(envelopes.run())
cl.add_control(dacs.run())

cl.run()
