#ifndef CONFIG_H
#define CONFIG_H

#include <chrono>

#include "noteMap.h"

#define CONTROL_RATE_Hz 200
#define CONTROL_RATE_Sec 0.005s
#define CONTROL_RATE_Ms 5
#define NUMBER_OF_NOTES 96

// MIDI Constants (OFFSET BY -1)
#define MIDI_LOW_VALUE 24
#define MIDI_HIGH_VALUE 119
#define CTRL_SEC_DIV 12.7  // gives a range of 10 sec for MIDI range 0-127

#define DAC_MIN_RANGE 127
#define DAC_MAX_RANGE 255

#define OUT_VOL_CHAN 0

#define ENV_MODE_CHAN 0
#define ENV_MODE_CTRL 0

#define ENV_ATTACK_CHAN 1
#define ENV_RELEASE_CHAN 2

#define HARM_MODE_CHAN 0
#define HARM_MODE_CTRL 6
#define HARM_SUB8_CTRL 7
#define HARM_SUB3_CTRL 8
#define HARM_UNIS_CTRL 9
#define HARM_OCT_CTRL 10
#define HARM_3RD_CTRL 11
#define HARM_4TH_CTRL 12
#define HARM_5TH_CTRL 13
#define HARM_6TH_CTRL 14
#define HARM_8TH_CTRL 15
#define HARM_9TH_CTRL 16
#define HARM_12TH_CTRL 17
#define HARM_15TH_CTRL 18
#define HARM_17TH_CTRL 19
#define HARM_18TH_CTRL 20
#define HARM_19TH_CTRL 21

#endif
