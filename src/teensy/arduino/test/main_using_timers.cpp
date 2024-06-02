#include <Arduino.h>
#include <SPI.h>
#include <chrono>

/**
 * @file main_using_timers.cpp
 * @author your name (you@domain.com)
 * @brief 
 * @version 0.1
 * @date 2024-05-27
 * 
 * @copyright Copyright (c) 2024
 * 
 * This works OK sometimes. It is inconsistent with connecting to the MIDI device and actually running. There is some issue with getting envs to trigger when running DACs
 * It's possible this is a Windows issue.
 * 
 */

#include "TeensyTimerTool.h"
using namespace TeensyTimerTool;


#include "config.h"
#include "noteMap.h"

#include "dacs.h"
#include "adsr.h"

#define DEBUG true


uint8_t velocity_values[NUMBER_OF_NOTES];
float envelope_values[NUMBER_OF_NOTES];

DACs dacs(&envelope_values[0], &velocity_values[0], DEBUG);
std::vector<ADSR> envelopes(NUMBER_OF_NOTES, ADSR(0.01f, 0.0f, 1.0f, 0.1f, CONTROL_RATE_Hz));

PeriodicTimer dac_timer;
PeriodicTimer env_timer;

void NoteOn(byte channel, byte note, byte velocity) {
  // DEBUG = true;
  uint8_t note_index = note - MIDI_LOW_VALUE;
  velocity_values[note_index] = velocity;
  envelopes[note_index].gate(1);
  if (DEBUG) {
    Serial.printf("Note ON channel: %d note: %d vel: %d\n", channel, note, velocity);
  }
}
void NoteOff(byte channel, byte note, byte velocity) {
  uint8_t note_index = note - MIDI_LOW_VALUE;
  envelopes[note_index].gate(0);
  if (DEBUG) {
    Serial.printf("Note OFF channel: %d note: %d vel: %d\n", channel, note, velocity);
  }
  // DEBUG = false;
}

void printEnvelopes() {
  Serial.println("env_values: ");
    Serial.print("[");
    for (int i=0; i<NUMBER_OF_NOTES;i++){
        Serial.print(envelope_values[i]);
        Serial.print(",");
    }
    Serial.println("]");
    Serial.println("");
    Serial.println("");
}

void envelope_run() {
  for(uint16_t env=0;env< envelopes.size();env++) {
        float env_val = envelopes[env].val;
        envelope_values[env] = env_val;
    }

    for(ADSR& adsr : envelopes) {
        ++adsr.begin();  // Get iterator from ADSR
    }

    if (DEBUG) {
      printEnvelopes();
    }
}

void setup() {
  // if (DEBUG) {
    Serial.begin(9600);
    Serial.println("Hello teensy");
  // }

  usbMIDI.setHandleNoteOn(NoteOn);
  usbMIDI.setHandleNoteOff(NoteOff);
  delay(1000);


  dacs.init();
  // env_timer.begin([] {envelope_run();}, CONTROL_RATE_Sec, false);
  // dac_timer.begin([] {dacs.run();}, CONTROL_RATE_Sec, false);
  // Testing rate
  env_timer.begin([] {envelope_run();}, 0.1s, false);
  dac_timer.begin([] {dacs.run();}, 0.1s, false);

  delay(1000);
  // Run timers
  env_timer.start();
  dac_timer.start();
  Serial.println("All started....");
}

void loop() {
  usbMIDI.read();
}

