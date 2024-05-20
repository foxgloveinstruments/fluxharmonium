"""
fluxharmonium dac value generator

processes all values to determine and scale the DAC values
and write them to the serial bus
"""
import asyncio
from itertools import chain

import math

from config import *

def clamp(n, min, max):
    if n < min: 
        return min
    elif n > max: 
        return max
    else: 
        return n 


class DACs():
    """
    Setup a DAC control loop to output the dac values
    """
    def __init__(self, parent, frequency, env_vals, vel_vals):
        self.parent = parent

        self.frequency = frequency
            
        self.env_vals = env_vals
        self.vel_vals = vel_vals
        
        self.dac_max_value = 255
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
        
        self.group_size = len(self.dac_values[0])
        
        self.parent._logger.debug('sending intial dac_values')
        self.parent.send_dac_values(self.dac_values)

    def freq_to_sec(self, freq):
        return 1000/1000/freq
    
    def get_group_index(self, position):
        output = position
        
        group = int(((output-1) / self.group_size))
        index = int(((output-1) % self.group_size))
        
        # self.parent._logger.debug(f'output: {output} group: {group} index: {index}')
        
        return {'group': group, 'index': index}
    
    def invert(self, value):
        return self.dac_max_value - value

    def scale_midi_to_dac(self, x):
        # (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
        MIDI_MAX = 127
        return int(x * (DAC_MAX_RANGE - DAC_MIN_RANGE) / MIDI_MAX + DAC_MIN_RANGE) 

    
    def calculate_dac_values(self):
        """
        Missing the mapping to the output range
        """
        for dac in range(NUMBER_OF_NOTES):
            dac_index = self.get_group_index(NOTE_MAP[dac+MIDI_LOW_VALUE]-1)
            try:
                current_value= clamp(self.invert(
                        self.scale_midi_to_dac(
                            math.floor(self.env_vals[dac] * self.vel_vals[dac])
                        )
                    ),0, 255)

                self.dac_values[dac_index['group']][dac_index['index']] = current_value
                # if dac == 0:
                #     self.parent._logger.info(f'dac 0 {current_value}')
            except Exception as e:
                self.parent._logger.error(f'Could not calculate the dac value {dac} {e}')

    async def run(self):
        while True:
            # self.parent._logger.debug('dac cycle')
            self.calculate_dac_values()
            self.parent.send_dac_values(self.dac_values)
            await asyncio.sleep(self.freq_to_sec(self.frequency))
