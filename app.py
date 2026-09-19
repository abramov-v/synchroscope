import math
import time
import tkinter as tk
from tkinter import messagebox

BG, PANEL, TEXT, MUTED = "#0b1220", "#111827", "#f9fafb", "#9ca3af"
GRID, BLUE, GREEN, RED, AMBER = "#374151", "#60a5fa", "#34d399", "#f87171", "#fbbf24"


class Generator:
    def __init__(self, frequency, phase=0.0, voltage=110.0):
        self.frequency = frequency
        self.phase = phase
        self.voltage = voltage

    def advance(self, dt):
        self.phase = (self.phase + 2 * math.pi * self.frequency * dt) % (2 * math.pi)


class Synchroscope(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Synchroscope Simulator")
        self.geometry("1180x820")
        self.minsize(900, 680)
        self.configure(bg=BG)

        self.connected = False
        self.last_time = time.perf_counter()

        self.bus = Generator(50.00, 0.0, 110.0)
        self.generator = Generator(49.80, math.radians(-70), 108.5)

        self.frequency_rate = 0.20
        self.frequency_step = 0.01
        self.frequency_min = 49.0
        self.frequency_max = 51.0
        self.avr = False
        self.breaker_animating = False
        self.breaker_anim_start = 0.0
        self.breaker_anim_duration = 0.28

        self.build_ui()

        self.bind("<space>", self.on_space)
        self.bind("<Up>", lambda event: self.change_frequency(1))
        self.bind("<Down>", lambda event: self.change_frequency(-1))

        self.after(30, self.animate)

    @staticmethod
    def wrap_phase(a):
        return (a + math.pi) % (2 * math.pi) - math.pi

    def phase_error(self):
        return self.wrap_phase(self.generator.phase - self.bus.phase)

    def frequency_difference(self):
        return self.generator.frequency - self.bus.frequency

    def voltage_difference(self):
        return self.generator.voltage - self.bus.voltage

    def build_ui(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=20, pady=(14, 8))
        tk.Label(top, text="SYNCHROSCOPE", fg=TEXT, bg=BG,
                 font=("Arial", 20, "bold")).pack(side="left")
        tk.Label(top, text="GENERATOR SYNCHRONIZATION TRAINER",
                 fg=MUTED, bg=BG, font=("Arial", 10)).pack(side="left", padx=16)
        tk.Button(top, text="CLOSE WINDOW", command=self.destroy,
                  bg="#374151", fg=TEXT, relief="flat",
                  padx=14, pady=7).pack(side="right")

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=8)

        left = tk.Frame(body, bg=PANEL)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right = tk.Frame(body, bg=PANEL, width=310)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        self.canvas = tk.Canvas(left, bg="#080d18", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.build_controls(right)

        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="x", padx=20, pady=(4, 14))
        self.status = tk.Label(bottom, text="SYNCHRONIZING", fg=AMBER,
                               bg=BG, font=("Arial", 12, "bold"))
        self.status.pack(side="left")
        self.slip_label = tk.Label(
            bottom, text="SLIP  +0.000 Hz", fg=MUTED, bg=BG,
            font=("Arial", 10, "bold"))
        self.slip_label.pack(side="left", padx=24)
        tk.Label(
            bottom,
            text="Adjust frequency → wait for 12 o'clock → press SPACE or CLOSE BREAKER",
            fg=MUTED, bg=BG, font=("Arial", 10)).pack(side="right")

    def build_controls(self, parent):
        tk.Label(parent, text="INCOMING GENERATOR", fg=TEXT, bg=PANEL,
                 font=("Arial", 15, "bold")).pack(anchor="w", padx=18, pady=(16, 2))

        self.gen_freq_label = tk.Label(parent, fg=TEXT, bg=PANEL,
                                       font=("Arial", 18, "bold"))
        self.gen_freq_label.pack(anchor="w", padx=18)

        tk.Label(parent, text="Frequency control", fg=MUTED, bg=PANEL).pack(
            anchor="w", padx=18, pady=(2, 4))

        freq_buttons = tk.Frame(parent, bg=PANEL)
        freq_buttons.pack(fill="x", padx=18)

        self.down_button = tk.Button(
            freq_buttons, text="▼  SPEED DOWN",
            command=lambda: self.change_frequency(-1),
            bg="#374151", fg=TEXT, activebackground=RED,
            activeforeground=TEXT, relief="flat",
            font=("Arial", 10, "bold"), padx=4, pady=10)
        self.down_button.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.up_button = tk.Button(
            freq_buttons, text="▲  SPEED UP",
            command=lambda: self.change_frequency(1),
            bg="#374151", fg=TEXT, activebackground=BLUE,
            activeforeground=TEXT, relief="flat",
            font=("Arial", 10, "bold"), padx=4, pady=10)
        self.up_button.pack(side="left", fill="x", expand=True, padx=(4, 0))

        tk.Label(parent, text="One click = one frequency step", fg=MUTED,
                 bg=PANEL, font=("Arial", 8)).pack(anchor="w", padx=18, pady=(3, 0))

        tk.Label(parent, text="Optional frequency slider", fg=MUTED, bg=PANEL).pack(
            anchor="w", padx=18, pady=(10, 2))

        self.frequency_scale = tk.Scale(
            parent, from_=49.0, to=51.0, resolution=0.01,
            orient="horizontal", bg=PANEL, fg=TEXT, highlightthickness=0,
            troughcolor=GRID, activebackground=BLUE,
            command=self.set_frequency_slider)
        self.frequency_scale.set(self.generator.frequency)
        self.frequency_scale.pack(fill="x", padx=18)

        tk.Label(parent, text="Slider directly sets generator frequency",
                 fg=MUTED, bg=PANEL, font=("Arial", 8)).pack(
                     anchor="w", padx=18, pady=(0, 0))

        tk.Label(parent, text="Frequency step size", fg=MUTED, bg=PANEL).pack(
            anchor="w", padx=18, pady=(10, 3))

        rate_frame = tk.Frame(parent, bg=PANEL)
        rate_frame.pack(fill="x", padx=18)

        self.slow_button = tk.Button(
            rate_frame, text="SLOW", command=lambda: self.set_rate("slow"),
            bg=BLUE, fg=TEXT, activebackground=BLUE, activeforeground=TEXT,
            relief="flat", font=("Arial", 10, "bold"), padx=8, pady=8)
        self.slow_button.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.fast_button = tk.Button(
            rate_frame, text="FAST", command=lambda: self.set_rate("fast"),
            bg="#374151", fg=MUTED, activebackground=BLUE, activeforeground=TEXT,
            relief="flat", font=("Arial", 10, "bold"), padx=8, pady=8)
        self.fast_button.pack(side="left", fill="x", expand=True, padx=(4, 0))

        self.rate_label = tk.Label(
            parent, text="ACTIVE: SLOW • STEP 0.01 Hz", fg=BLUE, bg=PANEL,
            font=("Arial", 9, "bold"))
        self.rate_label.pack(anchor="w", padx=18, pady=(3, 0))

        tk.Label(parent, text="Voltage (kV)", fg=MUTED, bg=PANEL).pack(
            anchor="w", padx=18, pady=(10, 0))
        self.voltage_scale = tk.Scale(
            parent, from_=105, to=115, resolution=0.1,
            orient="horizontal", bg=PANEL, fg=TEXT, highlightthickness=0,
            troughcolor=GRID, activebackground=BLUE,
            command=self.set_voltage)
        self.voltage_scale.set(self.generator.voltage)
        self.voltage_scale.pack(fill="x", padx=18)

        self.avr_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            parent, text="AUTO AVR", variable=self.avr_var,
            command=self.toggle_avr, bg=PANEL, fg=MUTED,
            selectcolor=BG, activebackground=PANEL, activeforeground=TEXT,
            highlightthickness=0).pack(anchor="w", padx=14, pady=(8, 0))

        self.close_button = tk.Button(
            parent, text="CLOSE BREAKER  [SPACE]", command=self.close_breaker,
            bg="#374151", fg=TEXT, relief="flat",
            font=("Arial", 12, "bold"), padx=10, pady=12)
        self.close_button.pack(fill="x", padx=18, pady=(17, 8))

        tk.Button(parent, text="RESET", command=self.reset,
                  bg="#1f2937", fg=MUTED, relief="flat",
                  padx=10, pady=8).pack(fill="x", padx=18)

        tk.Label(parent, text="SYNC CHECK", fg=TEXT, bg=PANEL,
                 font=("Arial", 11, "bold")).pack(anchor="w", padx=18, pady=(16, 6))

        self.sync_check = tk.Label(
            parent, justify="left", anchor="w", fg=MUTED, bg=PANEL,
            font=("Courier New", 9))
        self.sync_check.pack(fill="x", padx=18)

        self.phase_big = tk.Label(
            parent, text="PHASE  +0.0°", fg=MUTED, bg=PANEL,
            font=("Arial", 14, "bold"))
        self.phase_big.pack(anchor="w", padx=18, pady=(7, 0))

        tk.Label(parent, text="LIVE MEASUREMENTS", fg=TEXT, bg=PANEL,
                 font=("Arial", 11, "bold")).pack(anchor="w", padx=18, pady=(12, 6))
        self.measurements = tk.Label(
            parent, justify="left", anchor="w", fg=MUTED, bg=PANEL,
            font=("Courier New", 10))
        self.measurements.pack(fill="x", padx=18)

    def change_frequency(self, direction):
        if self.connected:
            return

        step = 0.01 if self.frequency_rate <= 0.20 else 0.05
        self.frequency_step = step

        new_frequency = self.generator.frequency + direction * step
        self.generator.frequency = max(
            self.frequency_min,
            min(self.frequency_max, new_frequency)
        )
        self.frequency_scale.set(self.generator.frequency)

        button = self.up_button if direction > 0 else self.down_button
        active = BLUE if direction > 0 else RED
        button.config(bg=active)
        self.after(90, lambda: button.config(bg="#374151"))

    def set_rate(self, mode):
        if mode == "slow":
            self.frequency_rate = 0.20
            step = 0.01
            name = "SLOW"
        else:
            self.frequency_rate = 1.00
            step = 0.05
            name = "FAST"

        self.frequency_step = step

        self.slow_button.config(
            bg=BLUE if mode == "slow" else "#374151",
            fg=TEXT if mode == "slow" else MUTED)
        self.fast_button.config(
            bg=BLUE if mode == "fast" else "#374151",
            fg=TEXT if mode == "fast" else MUTED)
        self.rate_label.config(
            text=f"ACTIVE: {name} • STEP {step:.2f} Hz",
            fg=BLUE)

    def set_frequency_slider(self, value):
        if not self.connected:
            self.generator.frequency = float(value)

    def set_voltage(self, value):
        if not self.connected:
            self.generator.voltage = float(value)

    def toggle_avr(self):
        self.avr = self.avr_var.get()

    def on_space(self, event=None):
        if not self.connected:
            self.close_breaker()
        return "break"

    def close_breaker(self):
        phase = abs(math.degrees(self.phase_error()))
        df = abs(self.frequency_difference())
        dv = abs(self.voltage_difference())

        if phase <= 10 and df < 0.067 and dv <= 1.0:
            self.breaker_animating = True
            self.breaker_anim_start = time.perf_counter()
            self.close_button.config(text="CLOSING...", state="disabled")
            self.frequency_scale.config(state="disabled")
            self.voltage_scale.config(state="disabled")
            self.after(280, self.finish_close_breaker)
        else:
            messagebox.showwarning(
                "Cannot close breaker",
                "Synchronization conditions are not met.\n\n"
                f"Phase error: {phase:.1f}° (need ≤ 10°)\n"
                f"Frequency difference: {df:.2f} Hz (need < 0.067 Hz)\n"
                f"Voltage difference: {dv:.1f} kV (need ≤ 1.0 kV)"
            )

    def finish_close_breaker(self):
        if not self.breaker_animating or self.connected:
            return
        self.breaker_animating = False
        self.connected = True
        self.generator.frequency = self.bus.frequency
        self.generator.voltage = self.bus.voltage
        self.close_button.config(text="BREAKER CLOSED", state="disabled")
        self.status.config(text="CONNECTED — SYNCHRONIZED", fg=GREEN)

    def reset(self):
        self.connected = False
        self.breaker_animating = False
        self.generator.frequency = 49.80
        self.generator.phase = math.radians(-70)
        self.generator.voltage = 108.5

        self.frequency_scale.config(state="normal")
        self.frequency_scale.set(self.generator.frequency)
        self.voltage_scale.config(state="normal")
        self.voltage_scale.set(self.generator.voltage)

        self.avr_var.set(False)
        self.avr = False

        self.close_button.config(text="CLOSE BREAKER  [SPACE]", state="normal")
        self.status.config(text="SYNCHRONIZING", fg=AMBER)
        self.set_rate("slow")

    def animate(self):
        now = time.perf_counter()
        dt = min(now - self.last_time, 0.1)
        self.last_time = now

        self.bus.advance(dt)

        if self.connected:
            self.generator.phase = self.bus.phase
            self.generator.frequency = self.bus.frequency
            self.generator.voltage = self.bus.voltage
        else:
            if self.avr:
                error_v = self.bus.voltage - self.generator.voltage
                self.generator.voltage += error_v * min(dt * 2.0, 1.0)

            self.generator.advance(dt)

        self.draw()
        self.after(30, self.animate)

    def draw_vector(self, cx, cy, radius, title, phase, color, fixed=False):
        self.canvas.create_oval(
            cx-radius, cy-radius, cx+radius, cy+radius,
            outline="#4b5563")
        self.canvas.create_line(cx-radius, cy, cx+radius, cy,
                                fill="#1f2937")
        self.canvas.create_line(cx, cy-radius, cx, cy+radius,
                                fill="#1f2937")

        # BUS is the fixed reference. GEN is drawn using relative phase.
        a = -math.pi / 2 if fixed else phase - math.pi / 2
        x = cx + (radius - 10) * math.cos(a)
        y = cy + (radius - 10) * math.sin(a)

        self.canvas.create_line(cx, cy, x, y, fill="#1f2937", width=9)
        self.canvas.create_line(cx, cy, x, y, fill=color, width=4)
        self.canvas.create_oval(cx-4, cy-4, cx+4, cy+4, fill=TEXT, outline="")
        self.canvas.create_text(cx, cy-radius-16, text=title,
                                fill=TEXT, font=("Arial", 10, "bold"))

    def draw_synchroscope(self, cx, cy, radius):
        self.canvas.create_oval(
            cx-radius, cy-radius, cx+radius, cy+radius,
            fill="#0b1220", outline="#6b7280", width=2)

        error = self.phase_error()
        phase_deg = math.degrees(error)
        df = self.frequency_difference()
        dv = self.voltage_difference()

        phase_ok = abs(phase_deg) <= 10
        freq_ok = abs(df) < 0.067
        volt_ok = abs(dv) <= 1.0
        ready = phase_ok and freq_ok and volt_ok

        zone = math.radians(10)
        for side in (-1, 1):
            aa = -math.pi / 2 + side * zone
            self.canvas.create_line(
                cx, cy,
                cx + (radius-5)*math.cos(aa),
                cy + (radius-5)*math.sin(aa),
                fill=GREEN if ready else "#4b5563", width=4)

        for deg in range(0, 360, 30):
            a = math.radians(deg - 90)
            inner = radius - 14
            outer = radius - 2
            self.canvas.create_line(
                cx + inner*math.cos(a), cy + inner*math.sin(a),
                cx + outer*math.cos(a), cy + outer*math.sin(a),
                fill="#6b7280", width=2)

        for label, deg in [("12", 0), ("3", 90), ("6", 180), ("9", 270)]:
            a = math.radians(deg - 90)
            self.canvas.create_text(
                cx + (radius-30)*math.cos(a),
                cy + (radius-30)*math.sin(a),
                text=label, fill=TEXT, font=("Arial", 10, "bold"))

        a = error - math.pi / 2
        px = cx + (radius-18) * math.cos(a)
        py = cy + (radius-18) * math.sin(a)

        pointer_color = GREEN if ready else (AMBER if phase_ok and freq_ok else BLUE)

        self.canvas.create_line(cx, cy, px, py, fill="#1f2937", width=9)
        self.canvas.create_line(cx, cy, px, py, fill=pointer_color, width=4)
        self.canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill=TEXT, outline="")

        self.canvas.create_text(
            cx, cy+radius+20, text="SYNCHROSCOPE",
            fill=GREEN if ready else MUTED,
            font=("Arial", 9, "bold"))

    def draw_waveform(self, x, y, width, height):
        self.canvas.create_rectangle(
            x, y, x+width, y+height, outline="#263244")
        mid = y + height/2
        self.canvas.create_line(x, mid, x+width, mid, fill="#1f2937")

        df = self.frequency_difference()
        phase = self.phase_error()

        self.canvas.create_text(
            x+8, y+8, anchor="nw",
            text="VOLTAGE WAVEFORM • RELATIVE PHASE",
            fill=MUTED, font=("Arial", 8, "bold"))
        self.canvas.create_text(
            x+width-8, y+8, anchor="ne",
            text=f"ΔF {df:+.3f} Hz",
            fill=GREEN if abs(df) < 0.067 else BLUE,
            font=("Arial", 8, "bold"))

        # Display a readable 2.2 cycles. The real 50 Hz carrier is not animated
        # at 50 cycles/sec; only the physically meaningful relative phase/slip
        # is animated.
        samples = 240
        for color, label, relative_phase in [
            ("#d1d5db", "BUS", 0.0),
            (BLUE, "GEN", phase),
        ]:
            points = []
            for i in range(samples):
                t = i / (samples - 1)
                local_phase = 2 * math.pi * 2.2 * t + relative_phase
                xx = x + t * width
                yy = mid - math.sin(local_phase) * (height * 0.30)
                points.extend((xx, yy))

            self.canvas.create_line(
                *points, fill=color, width=2, smooth=True)
            self.canvas.create_text(
                x+width-8, y+22 + (0 if label == "BUS" else 15),
                anchor="ne", text=label, fill=color,
                font=("Arial", 8, "bold"))

    def draw_breaker(self, x, y, width):
        left = x - width/2
        right = x + width/2
        gap = 26
        left_contact = x - gap
        right_contact = x + gap
        line_y = y + 8

        self.canvas.create_line(
            left, line_y, left_contact, line_y, fill="#6b7280", width=5)
        self.canvas.create_line(
            right_contact, line_y, right, line_y, fill="#6b7280", width=5)

        self.canvas.create_oval(
            left_contact-6, line_y-6, left_contact+6, line_y+6,
            fill="#d1d5db", outline="")
        self.canvas.create_oval(
            right_contact-6, line_y-6, right_contact+6, line_y+6,
            fill="#d1d5db", outline="")

        if self.breaker_animating:
            progress = min(
                1.0,
                (time.perf_counter() - self.breaker_anim_start)
                / self.breaker_anim_duration)
            blade_end_y = line_y - 30 * (1.0 - progress)
            blade_color = AMBER
            state = "BREAKER CLOSING..."
        else:
            blade_color = GREEN if self.connected else RED
            blade_end_y = line_y if self.connected else line_y - 30
            state = "BREAKER CLOSED" if self.connected else "BREAKER OPEN"

        self.canvas.create_line(
            left_contact, line_y, right_contact, blade_end_y,
            fill=blade_color, width=7)
        self.canvas.create_text(
            x, y + 43, text=state, fill=blade_color,
            font=("Arial", 10, "bold"))

    def draw(self):
        self.canvas.delete("all")
        w = max(self.canvas.winfo_width(), 600)
        h = max(self.canvas.winfo_height(), 450)

        r = min(w, h) * 0.16
        self.draw_vector(w*.22, h*.30, r, "BUS / GRID", 0.0, "#d1d5db", fixed=True)
        self.draw_vector(w*.78, h*.30, r, "INCOMING GENERATOR",
                         self.phase_error(), BLUE, fixed=False)
        self.draw_synchroscope(w*.50, h*.30, r*0.82)
        self.draw_waveform(w*.08, h*.52, w*.84, h*.25)
        self.draw_breaker(w*.50, h*.85, w*.70)

        phase_deg = math.degrees(self.phase_error())
        df = self.frequency_difference()
        dv = self.voltage_difference()

        phase_ok = abs(phase_deg) <= 10
        freq_ok = abs(df) < 0.067
        volt_ok = abs(dv) <= 1.0
        ready = phase_ok and freq_ok and volt_ok

        def mark(ok):
            return "✓ OK" if ok else "✕ WAIT"

        self.phase_big.config(
            text=f"PHASE  {phase_deg:+.1f}°  {'READY' if phase_ok else 'WAIT'}",
            fg=GREEN if phase_ok else AMBER)

        self.sync_check.config(
            text=(
                f"PHASE       {mark(phase_ok):<6}  ≤ 10°\n"
                f"ΔF          {mark(freq_ok):<6}  < 0.067 Hz\n"
                f"ΔV          {mark(volt_ok):<6}  ≤ 1.0 kV\n"
                f"\n{'READY TO CLOSE' if ready else 'NOT READY'}"
            ),
            fg=GREEN if ready else AMBER)

        self.gen_freq_label.config(text=f"{self.generator.frequency:.2f} Hz")
        self.measurements.config(
            text=(
                f"BUS       {self.bus.frequency:>6.2f} Hz\n"
                f"GEN       {self.generator.frequency:>6.2f} Hz\n"
                f"ΔF        {df:>+6.3f} Hz\n"
                f"BUS V     {self.bus.voltage:>6.1f} kV\n"
                f"GEN V     {self.generator.voltage:>6.1f} kV\n"
                f"ΔV        {dv:>+6.1f} kV\n"
                f"PHASE     {phase_deg:>+6.1f}°\n"
                f"SLIP      {abs(df):>6.3f} Hz\n"
                f"STATUS    {'CLOSED' if self.connected else 'OPEN'}"
            ))

        self.slip_label.config(
            text=f"SLIP  {df:+.3f} Hz",
            fg=GREEN if abs(df) < 0.067 else MUTED)

        if self.connected:
            self.status.config(text="CONNECTED — SYNCHRONIZED", fg=GREEN)
        elif self.breaker_animating:
            self.status.config(text="CLOSING BREAKER...", fg=AMBER)
        else:
            self.status.config(
                text="READY TO CLOSE" if ready else "SYNCHRONIZING",
                fg=GREEN if ready else AMBER)


if __name__ == "__main__":
    Synchroscope().mainloop()
