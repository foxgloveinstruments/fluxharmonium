#include <Arduino.h>
#include <vector>

#include "adsr.h"

const int NUMBER_OF_NOTES = 96;
const int CONTROL_RATE_Hz = 200;

float envelope_values[NUMBER_OF_NOTES];
std::vector<ADSR> envelopes(NUMBER_OF_NOTES, ADSR(0.01f, 0.0f, 1.0f, 0.1f, CONTROL_RATE_Hz));

void envelope_run() {
  for(uint16_t env=0;env< envelopes.size();env++) {
        float env_val = envelopes[env].val;
        envelope_values[env] = env_val;
    }

    for(ADSR& adsr : envelopes) {
        ADSR::ADSRIterator it = adsr.begin();  // Get iterator from ADSR
        ++it;
    }
}


void loop() {
      envelope_run();
      delay(1000);
}