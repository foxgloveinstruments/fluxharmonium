#include "dacs.h"

// DAC Constructor
DACs::DACs(float* env_vals, uint8_t* vel_vals, bool debug) {  
      DACs::m_env_vals = env_vals;
      DACs::m_vel_vals = vel_vals;
      DACs::m_debug = debug;
}

void DACs::init() {
  // Allocate memory for the 2D dac_values array
  m_dac_values = new uint16_t [NUMBER_OF_NOTES];
  memset(m_dac_values, 255, 96 * sizeof(uint8_t));

  m_dac_values[0] = 0;

  m_ltc1665.init(uint8_t(10), m_debug);
  m_ltc1665.write_chained_dac_values(m_dac_values, NUMBER_OF_NOTES);

  if (m_debug) {
      Serial.println("DACs init'd");
      printDacs();
  }

}

// Destructor with memory deallocation for dac_values
// DACs::~DACs() {
//   for (int i = 0; i < NUMBER_OF_NOTES; ++i) {
//     delete[] dac_values[i];
//   }
//   delete[] dac_values;
// }

// Invert DAC value (assuming higher value means lower output)
uint8_t DACs::invert_dac_value(uint8_t value) {
  return uint8_t(DAC_MAX_RANGE - value);
}

// Scale MIDI value to DAC range
uint8_t DACs::scale_midi_to_dac(uint8_t x) {
  const uint8_t MIDI_MAX = 127;
  return uint8_t(x * (DAC_MAX_RANGE - DAC_MIN_RANGE) / MIDI_MAX + DAC_MIN_RANGE);
}

// Calculate DAC values for all channels
void DACs::calculate_dac_values() {
  for (int dac = 0; dac < NUMBER_OF_NOTES; dac++) {
    uint8_t position = NOTE_MAP[(dac + MIDI_LOW_VALUE)]-1;

    m_dac_values[position] = invert_dac_value(
        scale_midi_to_dac(uint8_t((m_env_vals[dac] * m_vel_vals[dac])))
    );

    // Optional debug print for a specific note
    // if (dac + MIDI_LOW_VALUE == 60) {
    //   Serial.printf("Note 60 env_val: %d vel_val: %d dac_val: %d", m_env_vals[dac], m_vel_vals[dac], m_dac_values[group_index][channel_index]);
    // }
  }
  Serial.println("Calculated dacs");
}

// Function to run in the DAC loop
void DACs::run() {
    calculate_dac_values();
    if (m_debug) {
      printDacs();
    }
    m_ltc1665.write_chained_dac_values(m_dac_values, NUMBER_OF_NOTES);
    Serial.println("DAC running");
}

void DACs::printDacs() {
  Serial.println("dac_values: ");
    for (int i=0; i<NUMBER_OF_NOTES;i++){
      if (i % DAC_GROUP == 0){
        Serial.print("\n[");
      }
      
      Serial.print(m_dac_values[i]);
      
      if (i % DAC_GROUP == DAC_GROUP-1){
        Serial.println("]");
      } else {
        Serial.print(",");
      }
    }
    Serial.println("");
    Serial.println("");
}
