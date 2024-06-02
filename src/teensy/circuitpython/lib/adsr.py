# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Thadeus Frazier-Reed for creativecontrol
#
# SPDX-License-Identifier: MIT
"""
`creativecontrol_synth-envelopes`
================================================================================

Envelope generators for audio synthesis.


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

    def __init__(self, attack_time=0.01, decay_time=0.01, sustain_level=1, release_time=0.1, sample_rate=44100)  -> None:
        """
        """
        self.attack_time = attack_time
        self.decay_time = decay_time
        self.sustain_level = sustain_level
        self.release_time = release_time
        self._sample_rate = sample_rate

        self.gate_state = False

        self.val = 0
        self.ended = False
        self.stepper = 0
        # self.stepper = self.get_ads_stepper()

    def update_attack(self, attack_time):
        self.attack_time = attack_time

    def update_release(self, release_time):
        self.release_time = release_time

    def update_adsr(self, attack_time, decay_time, sustain_level, release_time):
        self.attack_time = attack_time
        self.decay_time = decay_time
        self.sustain_level = sustain_level
        self.release_time = release_time
    
    def update_sustain(self, sustain):
        """
        This can be used to update the sustain level from the incoming velocity
        """
        self.sustain_level = sustain

    def get_ads_stepper(self):
        """
        """
        steppers = []
        if self.attack_time > 0:
            steppers.append(count(start=0, \
                step= 1 / (self.attack_time * self._sample_rate)))
        if self.decay_time > 0:
            steppers.append(count(start=1, \
            step=-(1 - self.sustain_level) / (self.decay_time  * self._sample_rate)))
        # print(len(steppers))
        while True:
            l = len(steppers)
            if l > 0:
                # attack
                val = next(steppers[0])
                if l == 2 and val > 1:
                    # decay
                    steppers.pop(0)
                    val = next(steppers[0])
                elif l == 1 and val < self.sustain_level:
                    # sustain
                    steppers.pop(0)
                    val = self.sustain_level
            else:
                # sustain only
                val = self.sustain_level
            yield val

    def get_r_stepper(self):
        """
        release state
        """
        val = 1
        if self.release_time > 0:
            release_step = - self.val / (self.release_time * self._sample_rate)
            stepper = count(self.val, step=release_step)
        else:
            val = -1
        while True:
            if val <= 0:
                self.ended = True
                val = 0
            else:
                val = next(stepper)
            yield val
            

    def __iter__(self):
        # self.val = 0
        # self.ended = False
        # self.stepper = self.get_ads_stepper()
        return self

    def __next__(self):
        if self.stepper:
            self.val = next(self.stepper)
            return self.clamp(self.val)
        return 0

    def clamp(self, value):
        return 0 if value < 0 else 1 if value > 1 else value

    def gate (self, state):
        if state and not self.gate_state:
            self.attack()
        elif self.gate_state and not state:
            self.release()

    def attack(self):
        self.gate_state = True
        self.stepper = self.get_ads_stepper()

    def release(self):
        """
        """
        self.gate_state = False
        self.stepper = self.get_r_stepper()
