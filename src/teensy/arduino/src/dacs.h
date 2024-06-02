#ifndef DACS_H
#define DACS_H

// #include <chrono>
#include <string>

#include "config.h"
#include "noteMap.h"

#include "LTC166X.h"

class DACs {
public:
    DACs(float* env_vals, uint8_t* vel_vals, bool debug = false);
    void get_group_index(uint8_t position, uint8_t* group, uint8_t* index);
    uint8_t invert_dac_value(uint8_t value);
    uint8_t scale_midi_to_dac(uint8_t x);
    void calculate_dac_values();
    void init();
    void run();
    void printDacs();

private:
    bool m_debug;
    float* m_env_vals; // Array of envelope values
    uint8_t* m_vel_vals; // Array of velocity values
    uint8_t m_dac_max_value;
    uint16_t* m_dac_values; // 1D array to store DAC values for all channels
    LTC1665 m_ltc1665; // Assuming you have an LTC1665 library
};

#endif