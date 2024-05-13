
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
    def __init__(self, frequency, env_vals, vel_vals, debug=False):
        self.frequency = frequency
        self.debug = debug
        self.env_vals = env_vals
        self.vel_vals = vel_vals
        self.dac_values = [
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

        self.ltc1665 = creativecontrol_circuitpython_ltc166x.LTC1665(
            csel=board.GP1, sck=board.GP2, mosi=board.GP3, debug=False
        )

        self.ltc1665.write_chained_dac_values(self.dac_values)
    
    def get_group_index(self, position):
        """
        Retrieving the matrix 2D position
        """
        output = position
        if self.debug:
            print("original note: ", output)

        group = int((output / 8))
        index = int((output % 8))

        if self.debug:
            print("modified note: ", output)
            print("group: ", group)
            print("index: ", index)

        return {"group": group, "index": index}
    
    def calculate_dac_values(self):
        for dac in range(NUMBER_OF_NOTES):
            dac_index = self.get_group_index(NOTE_MAP[dac+MIDI_LOW_VALUE]-1)
            try:
                self.dac_values[dac_index["group"]][dac_index["index"]] = math.floor((self.env_vals[dac] * self.vel_vals[dac] * 2))
            except IndexError:
                print(f'Index Error - dac: {dac} note: {NOTE_MAP[dac+MIDI_LOW_VALUE]} idx: {dac_index}')
    
    def freq_to_sec(self, freq):
        return 1000/1000/freq

    async def run(self):
        while True:
            self.calculate_dac_values()
            self.ltc1665.write_chained_dac_values(self.dac_values)
            await asyncio.sleep(self.freq_to_sec(self.frequency))
