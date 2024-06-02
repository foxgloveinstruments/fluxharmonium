#ifndef LTC166X_H
#define LTC166X_H


#include <SPI.h>
#include <stdint.h>

const uint8_t DAC_WAKE = 0x00;
const uint8_t DAC_A = 0x01;
const uint8_t DAC_B = 0x02;
const uint8_t DAC_C = 0x03;
const uint8_t DAC_D = 0x04;
const uint8_t DAC_E = 0x05;
const uint8_t DAC_F = 0x06;
const uint8_t DAC_G = 0x07;
const uint8_t DAC_H = 0x08;
const uint8_t DAC_SLEEP = 0x0E;
const uint8_t DAC_ALL = 0x0F;
const uint8_t DAC_GROUP = 8;

class LTC166X {
    
    public:
        LTC166X();

        void init(uint8_t csel, bool debug);
        
        void sleep(uint8_t dac);
        void wake_no_change(uint8_t dac);
        void write_chained_dac_values(uint16_t* dac_values, uint8_t chain_length);
        void write_chained_dac_value(uint16_t value, uint8_t address, uint8_t chain_length);
        void write_dac_value(uint16_t value, uint8_t address);
        void write_dac_values(uint16_t* values, uint8_t values_length);

        uint8_t _bit_depth;
        bool _debug = false;

    private:
        uint8_t _cs;
        uint8_t _data_bits;
        uint8_t _range;
        SPISettings _spi_set;
        void start_transmission();
        void end_transmission();
        void write_value_to_spi(uint8_t data, uint8_t address);

};

class LTC1660 : public LTC166X {
public:
  LTC1660();
};

class LTC1665 : public LTC166X {
public:
  LTC1665();
};

#endif