#include <Arduino.h>
// #include <SPI.h>
#include <chrono>

#include "TeensyTimerTool.h"
using namespace TeensyTimerTool;

#include "LTC166X.h"
#include "config.h"
#include "noteMap.h"

#define DEBUG true

const int chipSelectPin = 10;
// LTC166X dac = LTC1665(0,0,chipSelectPin, false);

uint8_t dacs[8][8] = {
  {255, 255, 255, 255, 255, 255, 255, 255},
  };

int count = 0;

PeriodicTimer dac_timer; 
PeriodicTimer env_timer;
PeriodicTimer blink_timer;

void dac_callback() {
  Serial.print("dac_callback: ");
  Serial.println(micros());

}

void env_callback() {
  Serial.print("env_callback: ");
  Serial.println(micros());
}

const int led_pin = 13;

void blink() {
  digitalWrite(led_pin, !digitalRead(led_pin));
}


void setup() {
  digitalWrite(led_pin, LOW);
  pinMode(led_pin, OUTPUT);

  Serial.begin(9600);

  Serial.println("Hello teensy");

  delay(1000);
  // Setup timers
  dac_timer.begin(dac_callback, CONTROL_RATE_Sec, false);
  env_timer.begin(env_callback, CONTROL_RATE_Sec, false);
  blink_timer.begin(blink, CONTROL_RATE_Sec);
  Serial.println("Timers set");
  


  delay(1000);
  // Run timers
  dac_timer.start();
  env_timer.start();


}

void loop() {

  
}

// put function definitions here:

// void write_value_to_spi(int address, int value) {
//   int out = 0x0000;
//   int data_bits = 12;
//   int bit_depth = 8;
//   // Set the top 4 bits to the address based on array position.
//   out |= address << data_bits;
//   // Set the next n bits based on bit depth.
//   out |= value << (data_bits - bit_depth);
//   // Serial.print("out value: ");
//   // Serial.print(out);
//   // Serial.print(" ");
//   // Serial.print(highByte(out), HEX);
//   // Serial.print(" ");
//   // Serial.println(lowByte(out), HEX);
//   SPI.beginTransaction(spi_set);
//   digitalWrite(chipSelectPin,LOW);
//   SPI.transfer(highByte(out));
//   SPI.transfer(lowByte(out));
//   digitalWrite(chipSelectPin,HIGH);
//   SPI.endTransaction();
// }
