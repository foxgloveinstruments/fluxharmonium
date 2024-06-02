# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Thadeus Frazier-Reed for creativecontrol
#
# SPDX-License-Identifier: MIT
"""
`creativecontrol_synth-envelopes`
================================================================================

Envelope generators for audio synthesis.
Updated with pre-calculated floating point values

Value output will be between 0 * 1000
Scaling should happen after being multiplied by the output volume value using //

* Author(s): Thadeus Frazier-Reed

Implementation Notes
--------------------

**Hardware:**

.. todo:: Add links to any specific hardware product page(s), or category page(s).
  Use unordered list & hyperlink rST inline format: "* `Link Text <url>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Based on the ideas and code presented in:
  https://python.plainenglish.io/build-your-own-python-synthesizer-part-2-66396f6dad81

"""

# imports
try:
    from adafruit_itertools import count
except:
    from itertools import count

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/creativecontrol/Creativecontrol_CircuitPython_synth-envelopes.git"

class ADSR:
    """
    :Args:

        attack_time: float, optional
            Duration of the attack phase in seconds. Defaults to 0.01.
        decay: float, optional
            Duration of the decay in seconds. Defaults to 0.05.
        sustain: float, optional
            Amplitude of the sustain phase. Defaults to 0.707.
        release: float, optional
            Duration of the release in seconds. Defaults to 0.1.
        sample_rate: int, optional
            Control signal sample rate
    """

    STATE_IDLE = 0
    STATE_ATTACK = 1
    STATE_DECAY = 2
    STATE_SUSTAIN = 3
    STATE_RELEASE = 4
    STATE_FORCED = 5

    ATTACK_MULT = 0.5 # attacks tend to feel slow because of the curve of the VCA

    def __init__(self, attack_time=0.01, decay_time=0.01, sustain_level=1, release_time=0.1, sample_rate=44100)  -> None:
        """
        """
        self.attack_time = attack_time
        self.decay_time = decay_time
        self.sustain_level = sustain_level
        self.release_time = release_time
        self._sample_rate = sample_rate

        self.update_attack_step()
        self.update_decay_step()
        self.update_sustain_level_q()
        self.update_release_step()

        self.gate_state = False

        self.val = 0
        self.ended = False
        self.stepper = 0
        # self.stepper = self.get_ads_stepper()

    def update_attack_step(self):
        if self.attack_time == 0:
            self.attack_step = 0
        else:
            self.attack_step = 1000 // (self.attack_time * self._sample_rate * ATTACK_MULT)
     
    def update_decay_step(self):
        if self.decay_time == 0:
            self.decay_step = 0
        else:
            self.decay_step = -(1000 - self.sustain_level * 1000) // (self.decay_time * self._sample_rate)

    def update_sustain_level_q(self):
        self.sustain_level_q = int(self.sustain_level * 1000)
    
    def update_release_step(self):
        if self.release_time == 0:
            self.release_step = 0
        else:
            self.release_step = - 1000 // (self.release_time * self._sample_rate)


    def update_attack(self, attack_time):
        self.attack_time = attack_time
        self.update_attack_step()

    def update_release(self, release_time):
        self.release_time = release_time
        self.update_release_step()

    def update_adsr(self, attack_time, decay_time, sustain_level, release_time):
        self.attack_time = attack_time
        self.decay_time = decay_time
        self.sustain_level = sustain_level
        self.release_time = release_time

        self.update_attack_step()
        self.update_decay_step()
        self.update_sustain_level_q()
        self.update_release_step()

    def update_sustain(self, sustain):
        """
        This can be used to update the sustain level from the incoming velocity
        """
        self.sustain_level = sustain
        self.update_sustain_level_q()
        self.update_decay_step()

    def get_ads_stepper(self):
        """
        Steps through the Attack, Decay, and Sustain states
        """
        val = self.val
        state = 0
        while True:
            if state == 0:
                # attack
                if self.attack_step == 0:
                    val = 1001
                else:
                    val += self.attack_step
                if val > 1000:
                    val = 1000
                    state = 1
            elif state == 1:
                if self.decay_step == 0:
                    state = 2
                else:
                    val += self.decay_step
                    if val < self.sustain_level_q:
                        state = 2
            else:
                val = self.sustain_level_q
            yield val

    def get_r_stepper(self):
        """
        release state
        """
        val = self.val
        while True:
            val += self.release_step
            if val <= 0:
                self.ended = True
                val = 0
            yield val

    def __iter__(self):
        # self.val = 0
        # self.ended = False
        # self.stepper = self.get_ads_stepper()
        return self

    def __next__(self):
        if self.stepper:
            self.val = next(self.stepper)
            return self.val
        return 0

    def gate (self, state):
        """
        Set the envelope state based on the incoming gate.
        """
        if state and not self.gate_state:
            self.attack()
        elif self.gate_state and not state:
            self.release()

    def attack(self):
        """
        Start the attack state when the gate goes to 1
        """
        self.gate_state = True
        self.stepper = self.get_ads_stepper()

    def release(self):
        """
        Start the release state when gate goes to 0
        """
        self.gate_state = False
        self.stepper = self.get_r_stepper()
