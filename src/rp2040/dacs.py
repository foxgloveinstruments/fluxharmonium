
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
    def __init__(self, frequency,debug=False):
        self.frequency = frequency
        self.debug = debug
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
    
    def freq_to_sec(self, freq):
        return 1000/1000/freq

    async def run(self):
        while True:
            self.ltc1665.write_chained_dac_values(self.dac_values)
            await asyncio.sleep(self.freq_to_sec(self.frequency))
