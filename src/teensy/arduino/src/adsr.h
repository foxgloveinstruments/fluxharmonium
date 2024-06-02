#ifndef ADSR_H
#define ADSR_H

#include <Arduino.h>
#include <memory>


class ADSR {
public:
    enum class State {
        IDLE = 0,
        ATTACK = 1,
        DECAY = 2,
        SUSTAIN = 3,
        RELEASE = 4,
        FORCED = 5
    };
    ADSR(float attack_time = 0.01f, float decay_time = 0.05f,
        float sustain_level = 1.0f, float release_time = 0.1f,
        int sample_rate = 44100);
    
    // Update functions for individual parameters
    void update_attack(float attack_time);
    void update_release(float release_time);
    void update_adsr(float attack_time, float decay_time, float sustain_level, float release_time);
    void update_sustain(float sustain_level);
    void gate(bool state);
    float val;
    bool ended;

    // Pre-calculated step values
    float attack_step;
    float decay_step;
    float sustain_level_q;
    float release_step;

    bool gate_state;

    // Iterator interface
    class ADSRIterator {
    public:
        ADSRIterator(ADSR& adsr);
        bool operator!=(const ADSRIterator& other) const;
        float operator*() const;
        ADSR::ADSRIterator & operator++();
        float current_value;
        State current_state;

    private:
        ADSR& adsr_ptr;
        
    };

    ADSRIterator begin() { return ADSRIterator(*this); }

private:
    State state;
    float attack_time;
    float decay_time;
    float sustain_level;
    float release_time;
    int sample_rate;
    void update_attack_step();
    void update_decay_step();
    void update_release_step();
    void get_ads_stepper();
    void get_r_stepper();
    void attack();
    void release();



};

#endif