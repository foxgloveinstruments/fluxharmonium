import usb_cdc

class SerialCDC:
  def __init__(self, frequency, dac_values):
    self.frequency = frequency
    self.dac_values = dac_values
    self.serial = usb_cdc.data

  def freq_to_sec(self, freq):
        return 1000/1000/freq

  def write_to_dac_values(self, data):
    """
    DACs are arranged in groups of 8. Write each group of 8 to 
    """
    group_size = 8

    for index, dac_value in enumerate(data):
      self.dac_values[int(index/group_size)][index%group_size] = dac_value

  async def run(self):
    while True:
      if serial.in_waiting > 0:
        data_in = serial.readline()
        data = {"raw": data_in.decode()}
        self.write_to_dac_values(data)
      await asyncio.sleep(self.freq_to_sec(self.frequency))
    
