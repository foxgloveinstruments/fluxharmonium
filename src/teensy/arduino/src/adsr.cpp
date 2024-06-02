#include "ADSR.h"

ADSR::ADSR(float attack_time, float decay_time, float sustain_level, float release_time, int sample_rate) :
  state(State::IDLE),
  attack_time(attack_time),
  decay_time(decay_time),
  sustain_level(sustain_level),
  release_time(release_time),
  sample_rate(sample_rate),
  gate_state(false),
  val(0.0f),
  ended(true) {
  update_attack_step();
  update_decay_step();
  update_release_step();
}

void ADSR::update_attack_step() {
  attack_step = 1.0f / (attack_time * sample_rate);
}

void ADSR::update_decay_step() {
  decay_step = -(1.0f - sustain_level) / (decay_time * sample_rate);
}

void ADSR::update_release_step() {
  release_step = -1.0f / (release_time * sample_rate);
}

void ADSR::update_attack(float attack_time) {
  this->attack_time = attack_time;
  update_attack_step();
}

void ADSR::update_release(float release_time) {
  this->release_time = release_time;
  update_release_step();
}

void ADSR::update_adsr(float attack_time, float decay_time, float sustain_level, float release_time) {
  this->attack_time = attack_time;
  this->decay_time = decay_time;
  this->sustain_level = sustain_level;
  this->release_time = release_time;

  update_attack_step();
  update_decay_step();
  update_release_step();
}

void ADSR::update_sustain(float sustain_level) {
  this->sustain_level = sustain_level;
  update_decay_step();
}

void ADSR::gate(bool state) {
  if (state && !gate_state) {
    attack();
  } else if (gate_state && !state) {
    release();
  }
}

ADSR::ADSRIterator::ADSRIterator(ADSR& adsr) : adsr_ptr(adsr), current_value(0), current_state(ADSR::State::IDLE) { }

bool ADSR::ADSRIterator::operator!=(const ADSRIterator& other) const {
  return std::addressof(adsr_ptr) != std::addressof(other.adsr_ptr) || current_state != other.current_state;
}

float ADSR::ADSRIterator::operator*() const {
  return current_value;
}

ADSR::ADSRIterator& ADSR::ADSRIterator::operator++() {
  current_state = adsr_ptr.state;
  current_value = adsr_ptr.val;
  if (adsr_ptr.ended) {
    return *this;
  }
  // Serial.printf("Current state: %d\n", current_state);
  
  switch (current_state) {
    case ADSR::State::IDLE:
    case ADSR::State::FORCED:
      return *this;
    case ADSR::State::ATTACK:
      // Serial.printf("ADSR current_value: %f atk_step: %f\n", current_value, adsr_ptr.attack_step);
      current_value += adsr_ptr.attack_step;
      if (current_value > 1.0f) {
        current_value = 1.0f;
        if (adsr_ptr.decay_time > 0) {
            // Serial.println("Moving to DECAY state");
            current_state = ADSR::State::DECAY;
        } else {
            // Serial.println("Moving to SUSTAIN state");
            current_state = ADSR::State::SUSTAIN;
        }
      }
      break;
    case ADSR::State::DECAY:
      current_value += adsr_ptr.decay_step;
      if (current_value < adsr_ptr.sustain_level) {
        current_value = adsr_ptr.sustain_level;
        // Serial.println("Moving to SUSTAIN state");
        current_state = ADSR::State::SUSTAIN;
      }
      break;
    case ADSR::State::SUSTAIN:
      break;
    case ADSR::State::RELEASE:
      current_value += adsr_ptr.release_step;
      if (current_value <= 0.0f) {
        current_value = 0.0f;
        adsr_ptr.ended = true;
        current_state = ADSR::State::IDLE;
      }
      break;
  }
  adsr_ptr.val = current_value;
  // Serial.printf("ADSR current_value %f", current_value);
  return *this;
}

// ADSR::ADSRIterator ADSR::begin() const {
//   return ADSRIterator(this);
// }

// ADSR::ADSRIterator ADSR::end() const {
//   return ADSRIterator(nullptr);
// }

void ADSR::attack() {
  // Serial.println("starting ATTACK");
  gate_state = true;
  state = ADSR::State::ATTACK;
  val = 0.0f;
  ended = false;
}

void ADSR::release() {
  // Serial.println("starting RELEASE");
  gate_state = false;
  state = ADSR::State::RELEASE;
}