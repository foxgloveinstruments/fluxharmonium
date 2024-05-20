"""
MIDI input test
"""

import mido

print(mido.get_input_names())

port = 'pisound MIDI PS-08XK6BQ'

def parse_midi(message):
    print(f'MIDI msg {message}');
    
    

midiin = mido.open_input(port, callback=parse_midi)

while True:
    pass