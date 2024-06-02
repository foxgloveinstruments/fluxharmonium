# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Thadeus Frazier-Reed for creativecontrol
#
# SPDX-License-Identifier: MIT
"""
`creativecontrol_circuitpython_ltc166x`
================================================================================

CircuitPython library for control of LTC166X 8-bit and 10-bit DACs.


* Author(s): Thadeus Frazier-Reed

Implementation Notes
--------------------
The library provides options for storing all DAC values in a list
or a list of lists for DAC daisy-chains.
A channel may be marked for no update using a negative number (i.e. -1)
This value will be skipped or a no change message will be sent in the case of a daisy-change.

**TODO:**

* Add Sleep and Wake control

* Influenced by
  http://www.kerrywong.com/2010/05/02/a-library-for-ltc1665ltc1660/

**Hardware:**

* Linear Technologies LTC166X datasheet:
  https://www.analog.com/media/en/technical-documentation/data-sheets/166560fa.pdf

Multiple LTC1665/LTC1660’s can be controlled from a
single 3-wire serial port (i.e., SCK, DIN and CS/LD) by
using the included “daisy-chain” facility. A series of m
chips is configured by connecting each DOUT (except the
last) to DIN of the next chip, forming a single 16m-bit
shift register. The SCK and CS/LD signals are common
to all chips in the chain. In use, CS/LD is held low while m
16-bit words are clocked to DIN of the first chip; CS/LD
is then pulled high, updating all of them simultaneously.

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""

import microcontroller
from busio import SPI
import digitalio
from adafruit_bus_device.spi_device import SPIDevice

__version__ = "0.0.0+auto.0"
__repo__ = (
    "https://github.com/creativecontrol/creativecontrol_CircuitPython_LTC166X.git"
)


class LTC166X:
    """
    LTC166X 8 or 10-bit digital to analog converter.

    :param microcontroller.Pin sck: SPI clock pin.
    :param microcontroller.Pin mosi: SPI output pin.
    :param microcontroller.Pin csel: SPI chip select pin.
    :param bool debug: Debug the SPI output values.
    """

    DAC_WAKE = 0x00
    DAC_A = 0x01
    DAC_B = 0x02
    DAC_C = 0x03
    DAC_D = 0x04
    DAC_E = 0x05
    DAC_F = 0x06
    DAC_G = 0x07
    DAC_H = 0x08
    DAC_SLEEP = 0x0E
    DAC_ALL = 0x0F

    def __init__(
        self,
        sck: microcontroller.Pin,
        mosi: microcontroller.Pin,
        csel: microcontroller.Pin,
        debug: bool = False,
    ) -> None:
        """ """
        self._num_channels = 8
        self._data_bits = 12
        self._cs = digitalio.DigitalInOut(csel)
        self._spi = SPI(clock=sck, MOSI=mosi)
        self._bit_depth = 8
        self._range = pow(2, self._bit_depth)
        self._device = SPIDevice(
            self._spi, self._cs, baudrate=5000000, polarity=0, phase=0
        )
        self._debug = debug

    def get_bit_depth(self):
        """
        Return bit_depth based on device used.
        """
        return self._bit_depth

    def get_device_range(self):
        """
        Return device range based on device used.
        """
        return self._range

    def sleep(self, dac):
        """
        Put DAC in sleep mode.
        """

    def wake_no_change(self, dac):
        """
        Wake DAC with no value updates.
        """

    def write_chained_dac_values(self, dac_values: list):
        """
        Write list of values to a chain of DACs. All lists should be the same length.
        Do not update if value is < 0. This allows for comparison of
        update frames and only updating if value has changed.

        :param list dac_values: list of lists of values from 0 to device range.

        Each list represents a DAC's channel values.
        [[DAC 1], [DAC 2], [DAC 3], etc.]
        """
        for dac_index, _ in enumerate(dac_values[0]):
            dac_chain_list = [dac[dac_index] for dac in dac_values]
            # DAC chain is reversed because of the way the shift register works.
            dac_chain_list.reverse()
            with self._device as spi:
                for chain_value in dac_chain_list:
                    if chain_value >= 0:
                        self.write_value_to_spi(spi, chain_value, dac_index + 1)
                    else:
                        self.write_value_to_spi(spi, 0, 0)

    def write_chained_dac_value(self, value: list, address: int, chain_length: int):
        """
        Write a single DAC value to a chain.

        :param list value: DAC value from 0 to device range.
        :param int address: DAC address DAC A = 1 ... DAC H = 8 ... ALL DACs = 15.
        :param int chain_length: Number of DACs in the chain.
        """
        with self._device as spi:
            for _ in enumerate(chain_length):
                self.write_value_to_spi(spi, value, address)

    def write_dac_value(self, value: int, address: int):
        """
        Write a single DAC value.

        :param int value: DAC value from 0 to device range.
        :param int address: DAC address DAC A = 1 ... DAC H = 8 ... ALL DACs = 15.
        """
        with self._device as spi:
            self.write_value_to_spi(spi, value, address)

    def write_dac_values(self, values: list):
        """
        Write to list of values to DAC.
        Do not update if value is < 0. This allows for comparison of
        update frames and only updating if value has changed.

        :param list values: list of values from 0 to device range.
        """
        for index, value in enumerate(values):
            with self._device as spi:
                if value >= 0:
                    self.write_value_to_spi(spi, value, index + 1)

    def write_value_to_spi(self, spi: SPIDevice, value: int, address: int):
        """
        Write a single value to SPI.

        :param SPIDevice spi: adafruit_bus_device.spi_device.
        :param int value: DAC value from 0 to device range.
        :param int address: DAC address DAC A = 1 ... DAC H = 8 ... ALL DACs = 15.
        """
        assert 0 <= value <= self._range
        out = 0x0000
        # Set the top 4 bits to the address based on array position.
        out |= address << self._data_bits
        # Set the next n bits based on bit depth.
        out |= value << (self._data_bits - self._bit_depth)
        out_bytes = out.to_bytes(2, "big")
        if self._debug:
            print(f"{address} {hex(out)} {out_bytes} {len(out_bytes)}")
        spi.write(out_bytes)


class LTC1660(LTC166X):
    """
    Extended class for 10bit Octal DAC
    """

    def __init__(
        self,
        sck: microcontroller.Pin,
        mosi: microcontroller.Pin,
        csel: microcontroller.Pin,
        debug: bool = False,
    ):
        super().__init__(sck, mosi, csel, debug)
        self._bit_depth = 10


class LTC1665(LTC166X):
    """
    Extended class for 8bit Octal DAC
    """

    def __init__(
        self,
        sck: microcontroller.Pin,
        mosi: microcontroller.Pin,
        csel: microcontroller.Pin,
        debug: bool = False,
    ):
        super().__init__(sck, mosi, csel, debug)
        self._bit_depth = 8
