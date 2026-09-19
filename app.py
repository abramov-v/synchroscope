"""Application entry point."""

import tkinter as tk

from animation import AnimationMixin
from drawing import DrawingMixin
from simulation import Simulation
from ui import UIMixin


class Synchroscope(AnimationMixin, DrawingMixin, UIMixin, tk.Tk):
    def __init__(self):
        super().__init__()
        self.connected = False
        self.avr = False
        self.breaker_animating = False
        self.breaker_anim_start = 0.0
        self.breaker_anim_duration = 0.28

        self.simulation = Simulation()
        self.init_animation()
        self.build_ui()

        self.bind("<space>", self.on_space)
        self.bind("<Up>", lambda event: self.change_frequency(1))
        self.bind("<Down>", lambda event: self.change_frequency(-1))
        self.start_animation()


if __name__ == "__main__":
    Synchroscope().mainloop()
