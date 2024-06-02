#include <Arduino.h>
#include <SPI.h>

// put function declarations here:
void write_value_to_spi(int address, int value);

const int chipSelectPin = 10;
SPISettings spi_set(5000000, MSBFIRST, SPI_MODE0);

int count = 0;

void setup() {
  pinMode(chipSelectPin, OUTPUT);
  digitalWrite(chipSelectPin, HIGH);
  // Serial.begin(9600);
  SPI.begin();
}

void loop() {
  // put your main code here, to run repeatedly:
    write_value_to_spi(1, count);
    // Serial.println("on");
    
    count ++;

    if (count >=255) {
      count = 0;
    }
    delay(5);
    // write_value_to_spi(1, 0);
    // // Serial.println("off");
    // delay(2000);
}

// put function definitions here:
void write_value_to_spi(int address, int value) {
  int out = 0x0000;
  int data_bits = 12;
  int bit_depth = 8;
  // Set the top 4 bits to the address based on array position.
  out |= address << data_bits;
  // Set the next n bits based on bit depth.
  out |= value << (data_bits - bit_depth);
  // Serial.print("out value: ");
  // Serial.print(out);
  // Serial.print(" ");
  // Serial.print(highByte(out), HEX);
  // Serial.print(" ");
  // Serial.println(lowByte(out), HEX);
  SPI.beginTransaction(spi_set);
  digitalWrite(chipSelectPin,LOW);
  SPI.transfer(highByte(out));
  SPI.transfer(lowByte(out));
  digitalWrite(chipSelectPin,HIGH);
  SPI.endTransaction();
}
