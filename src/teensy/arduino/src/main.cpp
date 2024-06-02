#include <Arduino.h>
#include <SPI.h>
#include <chrono>

#include <TeensyThreads.h>
// this method is experimental
ThreadWrap(Serial, SerialXtra);
#define Serial ThreadClone(SerialXtra)

#include "config.h"
#include "noteMap.h"

#include "dacs.h"
#include "adsr.h"

#define DEBUG true

const int yield_time = int((1.0/1)*1000);


uint8_t velocity_values[NUMBER_OF_NOTES];
float envelope_values[NUMBER_OF_NOTES];

DACs dacs(&envelope_values[0], &velocity_values[0], DEBUG);
std::vector<ADSR> envelopes(NUMBER_OF_NOTES, ADSR(0.01f, 0.0f, 1.0f, 0.1f, CONTROL_RATE_Hz));

int env_thread_id;
int dac_thread_id;

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

void NoteOn(byte channel, byte note, byte velocity) {
  // DEBUG = true;
  uint8_t note_index = note - MIDI_LOW_VALUE;
  velocity_values[note_index] = velocity;
  envelopes[note_index].gate(1);
  if (DEBUG) {
    Serial.printf("Note ON channel: %d note: %d vel: %d\n", channel, note, velocity);
    printEnvelopes();
    dacs.printDacs();
  }
}
void NoteOff(byte channel, byte note, byte velocity) {
  uint8_t note_index = note - MIDI_LOW_VALUE;
  envelopes[note_index].gate(0);
  if (DEBUG) {
    Serial.printf("Note OFF channel: %d note: %d vel: %d\n", channel, note, velocity);
    printEnvelopes();
    dacs.printDacs();
  }
  // DEBUG = false;
}

void envelope_run() {
  while(1) {
    Serial.println("running envelopes");
    for(uint16_t env=0;env< envelopes.size();env++) {
          float env_val = envelopes[env].val;
          envelope_values[env] = env_val;
      }

    for(ADSR& adsr : envelopes) {
        ++adsr.begin();  // Get iterator from ADSR
    }

    if (DEBUG) {
      // printEnvelopes();
    }

    threads.delay(yield_time);
  }
}

void dac_run() {
  while(1) {
    Serial.println("running dacs");
    dacs.run();
    threads.delay(yield_time);
  }
}

void midi_run() {
  while(1) {
    usbMIDI.read();
    Serial.printf("ENV thread is %d\n", threads.getState(env_thread_id));
    Serial.printf("DAC thread is %d\n", threads.getState(dac_thread_id));
    threads.delay(yield_time);
  }
}


void setup() {
  // if (DEBUG) {
    Serial.begin(9600);
    Serial.println("Hello teensy");
    Serial.printf("yield time: %d ms\n", yield_time);
  // }

  usbMIDI.setHandleNoteOn(NoteOn);
  usbMIDI.setHandleNoteOff(NoteOff);
  delay(1000);


  dacs.init();
  
  delay(1000);
  // Run threads
  env_thread_id = threads.addThread(envelope_run);
  dac_thread_id = threads.addThread(dac_run);
  threads.addThread(midi_run);


  Serial.println("All started....");
}

void loop() {
  // usbMIDI.read();
  
}

