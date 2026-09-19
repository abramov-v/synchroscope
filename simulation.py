"""Simulation and synchronization logic."""

import math

from config import (
    BUS_FREQUENCY, BUS_VOLTAGE,
    INITIAL_GEN_FREQUENCY, INITIAL_GEN_PHASE_DEG, INITIAL_GEN_VOLTAGE,
    SYNC_PHASE_LIMIT_DEG, SYNC_FREQUENCY_LIMIT_HZ, SYNC_VOLTAGE_LIMIT_KV,
)
from generator import Generator


class Simulation:
    def __init__(self):
        self.bus = Generator(BUS_FREQUENCY, 0.0, BUS_VOLTAGE)
        self.generator = Generator(
            INITIAL_GEN_FREQUENCY,
            math.radians(INITIAL_GEN_PHASE_DEG),
            INITIAL_GEN_VOLTAGE,
        )

    @staticmethod
    def wrap_phase(angle):
        return (angle + math.pi) % (2 * math.pi) - math.pi

    def phase_error(self):
        return self.wrap_phase(self.generator.phase - self.bus.phase)

    def phase_error_degrees(self):
        return math.degrees(self.phase_error())

    def frequency_difference(self):
        return self.generator.frequency - self.bus.frequency

    def voltage_difference(self):
        return self.generator.voltage - self.bus.voltage

    def sync_state(self):
        phase = abs(self.phase_error_degrees())
        df = abs(self.frequency_difference())
        dv = abs(self.voltage_difference())
        phase_ok = phase <= SYNC_PHASE_LIMIT_DEG
        freq_ok = df < SYNC_FREQUENCY_LIMIT_HZ
        volt_ok = dv <= SYNC_VOLTAGE_LIMIT_KV
        return phase_ok, freq_ok, volt_ok, phase_ok and freq_ok and volt_ok

    def reset_generator(self):
        self.generator.frequency = INITIAL_GEN_FREQUENCY
        self.generator.phase = math.radians(INITIAL_GEN_PHASE_DEG)
        self.generator.voltage = INITIAL_GEN_VOLTAGE

    def advance_bus(self, dt):
        self.bus.advance(dt)

    def advance_generator(self, dt, avr=False):
        if avr:
            error_v = self.bus.voltage - self.generator.voltage
            self.generator.voltage += error_v * min(dt * 2.0, 1.0)
        self.generator.advance(dt)

    def connect_generator(self):
        self.generator.phase = self.bus.phase
        self.generator.frequency = self.bus.frequency
        self.generator.voltage = self.bus.voltage
