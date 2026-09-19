"""Generator model."""

import math


class Generator:
    def __init__(self, frequency, phase=0.0, voltage=110.0):
        self.frequency = frequency
        self.phase = phase
        self.voltage = voltage

    def advance(self, dt):
        self.phase = (
            self.phase + 2 * math.pi * self.frequency * dt
        ) % (2 * math.pi)
