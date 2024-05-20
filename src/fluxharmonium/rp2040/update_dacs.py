
import asyncio
import board
from config import *
import math
import creativecontrol_circuitpython_ltc166x


class DACs():
    """
    Setup a DAC control loop to output the dac values
    """
    def __init__(self, frequency, dac_values, debug=False):
        self.frequency = frequency
        self.debug = debug
        self.dac_values = dac_values

        self.ltc1665 = creativecontrol_circuitpython_ltc166x.LTC1665(
            csel=board.GP1, sck=board.GP2, mosi=board.GP3, debug=False
        )

        self.ltc1665.write_chained_dac_values(self.dac_values)
    
    def freq_to_sec(self, freq):
        return 1000/1000/freq

    async def run(self):
        while True:
            if self.debug:
              print(f'writing dac vals {self.dac_values}')
            self.ltc1665.write_chained_dac_values(self.dac_values)
            await asyncio.sleep(self.freq_to_sec(self.frequency))
