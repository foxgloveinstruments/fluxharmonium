
import _asyncio
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
        self.dac_max_value = 255
        # DAC starting value
        dsv = self.dac_max_value
        self.dac_values = [
            [dsv, dsv, dsv, dsv, dsv, dsv, dsv, dsv],
            [dsv, dsv, dsv, dsv, dsv, dsv, dsv, dsv],
            [dsv, dsv, dsv, dsv, dsv, dsv, dsv, dsv],
            [dsv, dsv, dsv, dsv, dsv, dsv, dsv, dsv],
            [dsv, dsv, dsv, dsv, dsv, dsv, dsv, dsv],
            [dsv, dsv, dsv, dsv, dsv, dsv, dsv, dsv],
            [dsv, dsv, dsv, dsv, dsv, dsv, dsv, dsv],
            [dsv, dsv, dsv, dsv, dsv, dsv, dsv, dsv],
            [dsv, dsv, dsv, dsv, dsv, dsv, dsv, dsv],
            [dsv, dsv, dsv, dsv, dsv, dsv, dsv, dsv],
            [dsv, dsv, dsv, dsv, dsv, dsv, dsv, dsv],
            [dsv, dsv, dsv, dsv, dsv, dsv, dsv, dsv],
        ]
        
        # Teensy 4.0 CS=board.D10 SCK=board.SCK (D13) MOSI=board.MOSI (D11)
        # Teensy 4.0 CS=board.D10 SCK=board.D12 (to be able to use pin 13 for LED) MOSI=board.MOSI (D11)
        self.ltc1665 = creativecontrol_circuitpython_ltc166x.LTC1665(
            csel=board.D10, sck=board.SCK, mosi=board.MOSI, debug=False
        )

        self.ltc1665.write_chained_dac_values(self.dac_values)

    def get_group_index(self, position):
        """
        Retrieving the matrix 2D position
        """
        output = position

        group = int(((output-1) / 8))
        index = int(((output-1) % 8))

        if self.debug:
            print("output: ", output)
            print("group: ", group)
            print("index: ", index)

        return {"group": group, "index": index}

    def invert_dac_value(self, value):
        """
        Because of the circuit the value of the output range must be inverted.
        """
        return self.dac_max_value - value

    def calculate_dac_values(self):
        """
        Calculate all values for all DACs.
        current envelope value * velocity value * 2

        envelope and velocity values are 0-127 so must be doubled
        to take advantage of the full DAC range.
        """
        for dac in range(NUMBER_OF_NOTES):
            dac_index = self.get_group_index(NOTE_MAP[dac+MIDI_LOW_VALUE]-1)
            try:
                self.dac_values[dac_index["group"]][dac_index["index"]] = self.invert_dac_value(
                    math.floor((self.env_vals[dac] * self.vel_vals[dac] * 2)))
            except IndexError:
                print(f'Index Error - dac: {dac}')
                print(f'note: {NOTE_MAP[dac+MIDI_LOW_VALUE]}')
                print(f'idx: {dac_index}')

    def freq_to_sec(self, freq):
        """
        Returns the space between events in seconds.
        """
        return 1000/1000/freq

    async def run(self):
        """
        DAC loop
        """
        while True:
            self.calculate_dac_values()
            self.ltc1665.write_chained_dac_values(self.dac_values)
            await asyncio.sleep(self.freq_to_sec(self.frequency))
