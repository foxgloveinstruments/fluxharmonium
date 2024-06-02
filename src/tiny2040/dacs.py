
import asyncio
import board
from config import *
import math
import creativecontrol_circuitpython_ltc166x


class DACs():
    """
    Setup a DAC control loop to update and output the dac values by combining
    the envelope and velocity values
    """
    def __init__(self, frequency: float, dac_vals: list, env_vals: list, vel_vals: list):
        self.frequency = frequency
        self.env_vals = env_vals
        self.vel_vals = vel_vals
        self.dac_max_value = 255
        # DAC starting value           
        self.dac_values = dac_vals

        self.ltc1665 = creativecontrol_circuitpython_ltc166x.LTC1665(
            csel=board.GP1, sck=board.GP2, mosi=board.GP3, debug=False
        )
        self.init_all_dacs()

    def init_all_dacs(self):
        dac_line = [255]*NUMBER_OF_DACS
        self.ltc1665.write_chained_dac_value(dac_line, self.ltc1665.DAC_ALL)

    def scale_midi_to_dac(self, x):
        # Start simple by inverting MIDI range
        # if you need more use MIDI_DAC_MAP
        MIDI_MAX = 127
        return MIDI_MAX - x
        # return MIDI_DAC_MAP[x]

    def calculate_dac_values(self):
        """
        Read backwards through the array to fill the farthest DAC first
        """
        for dac in range(NUMBER_OF_NOTES):
            # This mapping should move into the final position so that LTC1665 library doesn't have to reorganize
            dac_map = NOTE_MAP[dac+MIDI_LOW_VALUE]
            self.dac_values[dac_map['map']-1] = self.scale_midi_to_dac(
                    (self.env_vals[dac] * self.vel_vals[dac])//1000
                )
    
    async def run(self):
        """
        DAC loop
        """
        while True:
            self.calculate_dac_values()
            if DEBUG:
                print(f'dac vals {self.dac_values}\n')
            self.ltc1665.write_listed_dac_values(self.dac_values, NUMBER_OF_DACS)
            await asyncio.sleep(self.frequency)
