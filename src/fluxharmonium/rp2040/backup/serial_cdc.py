import asyncio
import usb_cdc

class SerialCDC:
  def __init__(self, frequency, dac_values, debug=False):
    self.frequency = frequency
    self.dac_values = dac_values
    self.group_size = len(self.dac_values[0])
    self.serial = usb_cdc.data
    
    self.debug = debug

  def freq_to_sec(self, freq):
        return 1000/1000/freq

  def write_to_dac_values(self, data):
    """
    Split single list data into multidimensional list 
    """
    indexA = int(index/self.group_size)
    indexB = index/self.group_size
    for index, dac_value in enumerate(data):
      self.dac_values[indexA][indexB] = int(dac_value)

  async def run(self):
    while True:
      if self.serial.in_waiting > 0:
        data_in = self.serial.readline()
        # remove the last 2 bytes b'\r\n'
        data = data_in[:-2]
        self.write_to_dac_values(data)
        if self.debug:
            print(f'serial in dac vals: {data}')
      await asyncio.sleep(self.freq_to_sec(self.frequency))
    
