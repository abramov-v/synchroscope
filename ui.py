"""Tkinter UI and controls."""

import time
import tkinter as tk
from tkinter import messagebox

import config


class UIMixin:
    def build_ui(self):
        self.title("Synchroscope Simulator")
        self.geometry("1180x820")
        self.minsize(900, 680)
        self.configure(bg=config.BG)

        top = tk.Frame(self, bg=config.BG)
        top.pack(fill="x", padx=20, pady=(14, 8))
        tk.Label(top, text="SYNCHROSCOPE", fg=config.TEXT, bg=config.BG,
                 font=("Arial", 20, "bold")).pack(side="left")
        tk.Label(top, text="GENERATOR SYNCHRONIZATION TRAINER",
                 fg=config.MUTED, bg=config.BG, font=("Arial", 10)).pack(side="left", padx=16)
        tk.Button(top, text="CLOSE WINDOW", command=self.destroy,
                  bg="#374151", fg=config.TEXT, relief="flat",
                  padx=14, pady=7).pack(side="right")

        body = tk.Frame(self, bg=config.BG)
        body.pack(fill="both", expand=True, padx=20, pady=8)
        left = tk.Frame(body, bg=config.PANEL)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right = tk.Frame(body, bg=config.PANEL, width=310)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        self.canvas = tk.Canvas(left, bg="#080d18", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.build_controls(right)

        bottom = tk.Frame(self, bg=config.BG)
        bottom.pack(fill="x", padx=20, pady=(4, 14))
        self.status = tk.Label(bottom, text="SYNCHRONIZING", fg=config.AMBER,
                               bg=config.BG, font=("Arial", 12, "bold"))
        self.status.pack(side="left")
        self.slip_label = tk.Label(bottom, text="SLIP  +0.000 Hz",
                                   fg=config.MUTED, bg=config.BG,
                                   font=("Arial", 10, "bold"))
        self.slip_label.pack(side="left", padx=24)
        tk.Label(bottom,
                 text="Adjust frequency → wait for 12 o'clock → press SPACE or CLOSE BREAKER",
                 fg=config.MUTED, bg=config.BG, font=("Arial", 10)).pack(side="right")

    def build_controls(self, parent):
        tk.Label(parent, text="INCOMING GENERATOR", fg=config.TEXT, bg=config.PANEL,
                 font=("Arial", 12, "bold")).pack(anchor="w", padx=18, pady=(10, 1))
        self.gen_freq_label = tk.Label(parent, fg=config.TEXT, bg=config.PANEL,
                                       font=("Arial", 17, "bold"))
        self.gen_freq_label.pack(anchor="w", padx=18)
        tk.Label(parent, text="Frequency control", fg=config.MUTED, bg=config.PANEL).pack(
            anchor="w", padx=18, pady=(2, 4))

        freq_buttons = tk.Frame(parent, bg=config.PANEL)
        freq_buttons.pack(fill="x", padx=18)
        self.down_button = tk.Button(
            freq_buttons, text="▼  SLOW",
            
            bg="#374151", fg=config.TEXT, activebackground=config.RED,
            activeforeground=config.TEXT, relief="flat",
            font=("Arial", 10, "bold"), padx=4, pady=10)
        self.down_button.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.up_button = tk.Button(
            freq_buttons, text="▲  FAST",
            
            bg="#374151", fg=config.TEXT, activebackground=config.BLUE,
            activeforeground=config.TEXT, relief="flat",
            font=("Arial", 10, "bold"), padx=4, pady=10)
        self.up_button.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # Hold the mouse button to continuously adjust frequency.
        self.down_button.bind("<ButtonPress-1>", lambda event: self.start_frequency_hold(-1))
        self.down_button.bind("<ButtonRelease-1>", self.stop_frequency_hold)
        self.up_button.bind("<ButtonPress-1>", lambda event: self.start_frequency_hold(1))
        self.up_button.bind("<ButtonRelease-1>", self.stop_frequency_hold)
        tk.Label(parent, text="0.01 Hz/step • HOLD = continuous", fg=config.MUTED,
                 bg=config.PANEL, font=("Arial", 8)).pack(anchor="w", padx=18, pady=(3, 0))

        tk.Label(parent, text="Frequency", fg=config.MUTED, bg=config.PANEL).pack(
            anchor="w", padx=18, pady=(10, 2))
        self.frequency_scale = tk.Scale(
            parent, from_=config.FREQUENCY_MIN, to=config.FREQUENCY_MAX,
            resolution=config.FREQUENCY_STEP, orient="horizontal",
            bg=config.PANEL, fg=config.TEXT, highlightthickness=0,
            troughcolor=config.GRID, activebackground=config.BLUE,
            command=self.set_frequency_slider)
        self.frequency_scale.set(self.simulation.generator.frequency)
        self.frequency_scale.pack(fill="x", padx=18)
        tk.Label(parent, text="Direct frequency",
                 fg=config.MUTED, bg=config.PANEL, font=("Arial", 8)).pack(anchor="w", padx=18)

        tk.Label(parent, text="EXCITATION", fg=config.MUTED, bg=config.PANEL,
                 font=("Arial", 9, "bold")).pack(
            anchor="w", padx=18, pady=(10, 0))
        excitation_row = tk.Frame(parent, bg=config.PANEL)
        excitation_row.pack(fill="x", padx=18)
        self.excitation_minus = tk.Button(
            excitation_row, text="−", command=lambda: self.change_excitation(-1),
            bg="#374151", fg=config.TEXT, relief="flat",
            font=("Arial", 11, "bold"), width=3)
        self.excitation_minus.pack(side="left")
        self.excitation_scale = tk.Scale(
            excitation_row, from_=config.EXCITATION_MIN, to=config.EXCITATION_MAX,
            resolution=config.EXCITATION_STEP, orient="horizontal",
            bg=config.PANEL, fg=config.TEXT, highlightthickness=0,
            troughcolor=config.GRID, activebackground=config.BLUE,
            showvalue=False, command=self.set_excitation)
        self.excitation_scale.set(self.simulation.excitation)
        self.excitation_scale.pack(side="left", fill="x", expand=True, padx=4)
        self.excitation_plus = tk.Button(
            excitation_row, text="+", command=lambda: self.change_excitation(1),
            bg="#374151", fg=config.TEXT, relief="flat",
            font=("Arial", 11, "bold"), width=3)
        self.excitation_plus.pack(side="left")
        self.excitation_value = tk.Label(
            parent, text="", fg=config.TEXT, bg=config.PANEL,
            font=("Courier New", 8, "bold"))
        self.excitation_value.pack(anchor="w", padx=18, pady=(1, 0))

        self.avr_var = tk.BooleanVar(value=False)
        tk.Checkbutton(parent, text="AUTO AVR", variable=self.avr_var,
                       command=self.toggle_avr, bg=config.PANEL, fg=config.MUTED,
                       selectcolor=config.BG, activebackground=config.PANEL,
                       activeforeground=config.TEXT, highlightthickness=0).pack(
                           anchor="w", padx=14, pady=(6, 0))

        self.close_button = tk.Button(
            parent, text="CLOSE BREAKER  [SPACE]", command=self.close_breaker,
            bg="#374151", fg=config.TEXT, relief="flat",
            font=("Arial", 11, "bold"), padx=10, pady=8)
        self.close_button.pack(fill="x", padx=18, pady=(10, 5))
        tk.Button(parent, text="RESET", command=self.reset,
                  bg="#1f2937", fg=config.MUTED, relief="flat",
                  padx=10, pady=6).pack(fill="x", padx=18)

        tk.Label(parent, text="SYNC CHECK", fg=config.TEXT, bg=config.PANEL,
                 font=("Arial", 11, "bold")).pack(anchor="w", padx=18, pady=(10, 4))
        self.sync_check = tk.Label(parent, justify="left", anchor="w",
                                   fg=config.MUTED, bg=config.PANEL,
                                   font=("Courier New", 8))
        self.sync_check.pack(fill="x", padx=18)
        self.phase_big = tk.Label(parent, text="PHASE  +0.0°", fg=config.MUTED,
                                  bg=config.PANEL, font=("Arial", 14, "bold"))
        self.phase_big.pack(anchor="w", padx=18, pady=(4, 0))
        tk.Label(parent, text="LIVE MEASUREMENTS", fg=config.TEXT, bg=config.PANEL,
                 font=("Arial", 11, "bold")).pack(anchor="w", padx=18, pady=(8, 4))
        self.measurements = tk.Label(parent, justify="left", anchor="w",
                                     fg=config.MUTED, bg=config.PANEL,
                                     font=("Courier New", 8))
        self.measurements.pack(fill="x", padx=18)

    def start_frequency_hold(self, direction):
        if self.connected:
            return

        self.stop_frequency_hold()
        self.frequency_hold_direction = direction
        self.change_frequency(direction)

        # First repeat after a short delay, then continue while held.
        self.frequency_hold_job = self.after(
            180, self.repeat_frequency_hold)

    def repeat_frequency_hold(self):
        if self.frequency_hold_direction == 0 or self.connected:
            self.frequency_hold_job = None
            return

        self.change_frequency(self.frequency_hold_direction)
        self.frequency_hold_job = self.after(
            60, self.repeat_frequency_hold)

    def stop_frequency_hold(self, event=None):
        self.frequency_hold_direction = 0
        if self.frequency_hold_job is not None:
            try:
                self.after_cancel(self.frequency_hold_job)
            except tk.TclError:
                pass
            self.frequency_hold_job = None

    def change_frequency(self, direction):
        if self.connected:
            return
        new_frequency = self.simulation.generator.frequency + direction * config.FREQUENCY_STEP
        self.simulation.generator.frequency = max(
            config.FREQUENCY_MIN, min(config.FREQUENCY_MAX, new_frequency))
        self.frequency_scale.set(self.simulation.generator.frequency)
        button = self.up_button if direction > 0 else self.down_button
        button.config(bg=config.BLUE if direction > 0 else config.RED)
        self.after(90, lambda: button.config(bg="#374151"))

    def set_frequency_slider(self, value):
        if not self.connected:
            self.simulation.generator.frequency = float(value)

    def set_excitation(self, value):
        if not self.connected and not self.avr:
            self.simulation.excitation = float(value)

    def change_excitation(self, direction):
        if self.connected or self.avr:
            return
        value = self.simulation.excitation + direction * config.EXCITATION_STEP
        value = max(config.EXCITATION_MIN, min(config.EXCITATION_MAX, value))
        self.simulation.excitation = value
        self.excitation_scale.set(value)

    def toggle_avr(self):
        self.avr = self.avr_var.get()
        state = "disabled" if self.avr or self.connected else "normal"
        self.excitation_scale.config(state=state)
        self.excitation_minus.config(state=state)
        self.excitation_plus.config(state=state)

    def on_space(self, event=None):
        if not self.connected:
            self.close_breaker()
        return "break"

    def close_breaker(self):
        phase = abs(self.simulation.phase_error_degrees())
        df = abs(self.simulation.frequency_difference())
        dv_percent = self.simulation.voltage_difference_percent()
        if (phase <= config.SYNC_PHASE_LIMIT_DEG
                and df < config.SYNC_FREQUENCY_LIMIT_HZ
                and config.SYNC_VOLTAGE_MIN_PERCENT <= dv_percent
                <= config.SYNC_VOLTAGE_MAX_PERCENT):
            self.breaker_animating = True
            self.breaker_anim_start = time.perf_counter()
            self.close_button.config(text="CLOSING...", state="disabled")
            self.frequency_scale.config(state="disabled")
            self.excitation_scale.config(state="disabled")
            self.excitation_minus.config(state="disabled")
            self.excitation_plus.config(state="disabled")
            self.after(int(config.BREAKER_ANIMATION_DURATION * 1000),
                       self.finish_close_breaker)
        else:
            reasons = []
            if phase > config.SYNC_PHASE_LIMIT_DEG:
                reasons.append("Phase angle out of limit")
            if df >= config.SYNC_FREQUENCY_LIMIT_HZ:
                reasons.append("Frequency slip too large")
            if dv_percent < config.SYNC_VOLTAGE_MIN_PERCENT:
                reasons.append("Generator voltage is below BUS")
            elif dv_percent > config.SYNC_VOLTAGE_MAX_PERCENT:
                reasons.append("Generator voltage is above +5% limit")
            messagebox.showwarning(
                "⚠ SYNC CHECK FAILED",
                "BREAKER BLOCKED\n\n"
                + "\n".join(f"• {reason}" for reason in reasons)
                + "\n\n"
                f"PHASE  {self.simulation.phase_error_degrees():+.1f}°  (limit ±10°)\n"
                f"ΔF     {self.simulation.frequency_difference():+.3f} Hz  (limit <0.067 Hz)\n"
                f"ΔV     {dv_percent:+.2f}%  (allowed 0% to +5%)"
            )

    def finish_close_breaker(self):
        if not self.breaker_animating or self.connected:
            return
        self.breaker_animating = False
        self.connected = True
        self.simulation.connect_generator()
        self.close_button.config(
            text="BREAKER CLOSED", state="disabled", bg=config.GREEN,
            fg=config.BG)
        self.status.config(text="CONNECTED — SYNCHRONIZED", fg=config.GREEN)

    def reset(self):
        self.connected = False
        self.breaker_animating = False
        self.simulation.reset_generator()
        self.frequency_scale.config(state="normal")
        self.frequency_scale.set(self.simulation.generator.frequency)
        self.excitation_scale.config(state="normal")
        self.excitation_minus.config(state="normal")
        self.excitation_plus.config(state="normal")
        self.excitation_scale.set(self.simulation.excitation)
        self.avr_var.set(False)
        self.avr = False
        self.close_button.config(text="CLOSE BREAKER  [SPACE]", state="normal",
                                bg="#374151", fg=config.TEXT)
        self.status.config(text="SYNCHRONIZING", fg=config.AMBER)
