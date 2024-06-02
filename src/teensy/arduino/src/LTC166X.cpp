#include "LTC166X.h"
#include "Arduino.h"


LTC166X::LTC166X() {
  LTC166X::_cs = 10;
  LTC166X::_bit_depth = 8;
  LTC166X::_data_bits = 12;
  LTC166X::_range = pow(2, _bit_depth),
  LTC166X::_debug = false;
  SPISettings _spi_set(5000000, MSBFIRST, SPI_MODE0);

}

void LTC166X::init(uint8_t csel, bool debug) {
  _debug = debug;
  pinMode(_cs, OUTPUT);
  digitalWrite(_cs, HIGH);
  SPI.begin();
}

void LTC166X::start_transmission() {
  SPI.beginTransaction(_spi_set);
  digitalWrite(_cs, LOW);  // Activate chip select
}

void LTC166X::end_transmission() {
  digitalWrite(_cs, HIGH); // Deactivate chip select
  SPI.endTransaction();
}

void LTC166X::sleep(uint8_t dac) {
  // Implement sleep logic using write_value_to_spi with DAC_SLEEP value
  write_value_to_spi(DAC_SLEEP, dac);
}

void LTC166X::wake_no_change(uint8_t dac) {
  // Implement wake logic using write_value_to_spi with appropriate value
  // (might be DAC_WAKE or another depending on device)
  write_value_to_spi(DAC_WAKE, dac);
}

/**
 * @brief Write list of values to a chain of DACs. All lists should be the same length.
 *       Do not update if value is < 0. This allows for comparison of
 *       update frames and only updating if value has changed.
 * 
 * @param dac_values
 */
void LTC166X::write_chained_dac_values(uint16_t* dac_values, uint8_t num_values) {
  start_transmission();
  for (int out=0; out<num_values ; out++) {
    uint8_t position = num_values-out;
    uint8_t address = ((position-1)%DAC_GROUP)+1; // Invert the output writing last first
    uint8_t out_value = dac_values[position-1];
    if (out_value >= 0) {
      write_value_to_spi(out_value, address); // Assuming write_value_to_spi takes care of addressing
    } else {
      write_value_to_spi(0, 0); // Send 0 for values less than 0 (optional behavior)
    }
  }
  end_transmission();
  
  Serial.println("Completed transmission");
}

void LTC166X::write_chained_dac_value(uint16_t value, uint8_t address, uint8_t chain_length) {
  for (int i = 0; i < chain_length; i++) {
    write_value_to_spi(value, address);
  }
}

void LTC166X::write_dac_value(uint16_t value, uint8_t address) {
  write_value_to_spi(value, address);
}

void LTC166X::write_dac_values(uint16_t* values, uint8_t values_length) {
  for (uint8_t index = 0; index < values_length; index++) {
    uint16_t value = values[index];
    if (value >= 0) {
      write_value_to_spi(value, index + 1);
    }
  }
}

void LTC166X::write_value_to_spi(uint8_t data, uint8_t address) {
  // Combine address and data based on data_bits and bit_depth
  uint16_t out = address << _data_bits;
  out |= (data) << (_data_bits - _bit_depth);

  // Convert 16-bit out to a byte array for SPI transfer
  uint8_t out_bytes[2];
  out_bytes[0] = (out >> 8) & 0xFF;
  out_bytes[1] = out & 0xFF;

  
  // digitalWrite(_cs, LOW);  // Activate chip select
  SPI.transfer(out_bytes, sizeof(out_bytes));
  // digitalWrite(_cs, HIGH); // Deactivate chip select
  

  if (_debug) {
    Serial.printf("address: %d data: %d out: %X data1: %X data2: %X\n", address, data, out, u_int8_t(out_bytes[0]), u_int8_t(out_bytes[1]));
  }

}

LTC1660::LTC1660() :
  LTC166X() {
  LTC166X::_bit_depth = 10;
}

LTC1665::LTC1665() :
  LTC166X() {
  LTC166X::_bit_depth = 8;
}