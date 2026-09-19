"""Animation and timing."""

import math
import time

import config


class AnimationMixin:
    def init_animation(self):
        self.last_time = time.perf_counter()
        self.visual_phase = 0.0
        self.visual_phase_scale = config.VISUAL_PHASE_SCALE

    def start_animation(self):
        self.after(config.FRAME_MS, self.animate)

    def animate(self):
        now = time.perf_counter()
        dt = min(now - self.last_time, config.MAX_DT)
        self.last_time = now

        self.simulation.advance_bus(dt)
        self.visual_phase = (
            self.visual_phase
            + 2 * math.pi * self.simulation.bus.frequency
            * dt * self.visual_phase_scale
        ) % (2 * math.pi)

        if self.connected:
            self.simulation.connect_generator()
        else:
            self.simulation.advance_generator(dt, self.avr)

            # Keep the voltage control synchronized with AUTO AVR.
            if self.avr and hasattr(self, "voltage_scale"):
                self.voltage_scale.set(self.simulation.generator.voltage)

        self.draw()
        self.after(config.FRAME_MS, self.animate)
