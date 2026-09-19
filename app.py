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

        # Frequency setpoint is changed by the slider. Actual frequency
        # approaches it at the selected SLOW/FAST rate.
        self.frequency_target = 49.80
        self.frequency_rate = 0.20
        self.governor = False
        self.avr = False

        self.build_ui()
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
        tk.Label(
            bottom,
            text="Match ΔF and ΔV → wait for 12 o'clock → CLOSE BREAKER",
            fg=MUTED, bg=BG, font=("Arial", 10)).pack(side="right")

    def build_controls(self, parent):
        tk.Label(parent, text="INCOMING GENERATOR", fg=TEXT, bg=PANEL,
                 font=("Arial", 15, "bold")).pack(anchor="w", padx=18, pady=(16, 2))

        self.gen_freq_label = tk.Label(parent, fg=TEXT, bg=PANEL,
                                       font=("Arial", 18, "bold"))
        self.gen_freq_label.pack(anchor="w", padx=18)

        tk.Label(parent, text="Frequency setpoint (Hz)", fg=MUTED, bg=PANEL).pack(
            anchor="w", padx=18)
        self.freq_scale = tk.Scale(
            parent, from_=49.0, to=51.0, resolution=0.01,
            orient="horizontal", bg=PANEL, fg=TEXT, highlightthickness=0,
            troughcolor=GRID, activebackground=BLUE,
            command=self.set_frequency)
        self.freq_scale.set(self.frequency_target)
        self.freq_scale.pack(fill="x", padx=18)

        tk.Label(parent, text="Frequency change rate", fg=MUTED, bg=PANEL).pack(
            anchor="w", padx=18, pady=(8, 3))

        rate_frame = tk.Frame(parent, bg=PANEL)
        rate_frame.pack(fill="x", padx=18)

        self.slow_button = tk.Button(
            rate_frame, text="SLOW", command=lambda: self.set_rate("slow"),
            bg=BLUE, fg=TEXT, relief="flat",
            font=("Arial", 10, "bold"), padx=8, pady=7)
        self.slow_button.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.fast_button = tk.Button(
            rate_frame, text="FAST", command=lambda: self.set_rate("fast"),
            bg="#374151", fg=MUTED, relief="flat",
            font=("Arial", 10, "bold"), padx=8, pady=7)
        self.fast_button.pack(side="left", fill="x", expand=True, padx=(4, 0))

        self.rate_label = tk.Label(
            parent, text="0.20 Hz/s", fg=MUTED, bg=PANEL,
            font=("Arial", 9))
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

        self.gov_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            parent, text="AUTO GOVERNOR", variable=self.gov_var,
            command=self.toggle_governor, bg=PANEL, fg=MUTED,
            selectcolor=BG, activebackground=PANEL, activeforeground=TEXT,
            highlightthickness=0).pack(anchor="w", padx=14, pady=(8, 0))

        self.avr_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            parent, text="AUTO AVR", variable=self.avr_var,
            command=self.toggle_avr, bg=PANEL, fg=MUTED,
            selectcolor=BG, activebackground=PANEL, activeforeground=TEXT,
            highlightthickness=0).pack(anchor="w", padx=14)

        self.close_button = tk.Button(
            parent, text="CLOSE BREAKER", command=self.close_breaker,
            bg="#374151", fg=TEXT, relief="flat",
            font=("Arial", 12, "bold"), padx=10, pady=12)
        self.close_button.pack(fill="x", padx=18, pady=(17, 8))

        tk.Button(parent, text="RESET", command=self.reset,
                  bg="#1f2937", fg=MUTED, relief="flat",
                  padx=10, pady=8).pack(fill="x", padx=18)

        tk.Label(parent, text="LIVE MEASUREMENTS", fg=TEXT, bg=PANEL,
                 font=("Arial", 11, "bold")).pack(anchor="w", padx=18, pady=(20, 6))
        self.measurements = tk.Label(
            parent, justify="left", anchor="w", fg=MUTED, bg=PANEL,
            font=("Courier New", 10))
        self.measurements.pack(fill="x", padx=18)

    def set_frequency(self, value):
        if not self.connected:
            self.frequency_target = float(value)

    def set_rate(self, mode):
        if mode == "slow":
            self.frequency_rate = 0.20
            self.slow_button.config(bg=BLUE, fg=TEXT)
            self.fast_button.config(bg="#374151", fg=MUTED)
        else:
            self.frequency_rate = 1.00
            self.fast_button.config(bg=BLUE, fg=TEXT)
            self.slow_button.config(bg="#374151", fg=MUTED)
        self.rate_label.config(text=f"{self.frequency_rate:.2f} Hz/s")

    def set_voltage(self, value):
        if not self.connected:
            self.generator.voltage = float(value)

    def toggle_governor(self):
        self.governor = self.gov_var.get()

    def toggle_avr(self):
        self.avr = self.avr_var.get()

    def close_breaker(self):
        phase = abs(math.degrees(self.phase_error()))
        df = abs(self.frequency_difference())
        dv = abs(self.voltage_difference())

        if phase <= 10 and df <= 0.10 and dv <= 1.0:
            self.connected = True
            self.generator.frequency = self.bus.frequency
            self.frequency_target = self.bus.frequency
            self.generator.voltage = self.bus.voltage
            self.close_button.config(text="BREAKER CLOSED", state="disabled")
            self.freq_scale.config(state="disabled")
            self.voltage_scale.config(state="disabled")
            self.status.config(text="CONNECTED — SYNCHRONIZED", fg=GREEN)
        else:
            messagebox.showwarning(
                "Cannot close breaker",
                "Synchronization conditions are not met.\n\n"
                f"Phase error: {phase:.1f}° (need ≤ 10°)\n"
                f"Frequency difference: {df:.2f} Hz (need ≤ 0.10 Hz)\n"
                f"Voltage difference: {dv:.1f} kV (need ≤ 1.0 kV)"
            )

    def reset(self):
        self.connected = False
        self.generator.frequency = 49.80
        self.generator.phase = math.radians(-70)
        self.generator.voltage = 108.5
        self.frequency_target = 49.80

        self.freq_scale.config(state="normal")
        self.voltage_scale.config(state="normal")
        self.freq_scale.set(self.frequency_target)
        self.voltage_scale.set(self.generator.voltage)

        self.gov_var.set(False)
        self.avr_var.set(False)
        self.governor = False
        self.avr = False

        self.close_button.config(text="CLOSE BREAKER", state="normal")
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
            if self.governor:
                self.frequency_target = self.bus.frequency

            # Slew actual frequency toward the selected setpoint.
            error = self.frequency_target - self.generator.frequency
            max_change = self.frequency_rate * dt
            if abs(error) <= max_change:
                self.generator.frequency = self.frequency_target
            else:
                self.generator.frequency += math.copysign(max_change, error)

            if self.avr:
                error_v = self.bus.voltage - self.generator.voltage
                self.generator.voltage += error_v * min(dt * 2.0, 1.0)

            self.generator.advance(dt)

        self.draw()
        self.after(30, self.animate)

    def draw_vector(self, cx, cy, radius, title, phase, color):
        self.canvas.create_oval(
            cx-radius, cy-radius, cx+radius, cy+radius,
            outline="#4b5563")
        self.canvas.create_line(cx-radius, cy, cx+radius, cy, fill="#1f2937")
        self.canvas.create_line(cx, cy-radius, cx, cy+radius, fill="#1f2937")

        a = phase - math.pi / 2
        x = cx + (radius - 10) * math.cos(a)
        y = cy + (radius - 10) * math.sin(a)
        self.canvas.create_line(cx, cy, x, y, fill=color, width=4)
        self.canvas.create_oval(cx-4, cy-4, cx+4, cy+4, fill=TEXT, outline="")
        self.canvas.create_text(cx, cy-radius-16, text=title,
                                fill=TEXT, font=("Arial", 10, "bold"))

    def draw_synchroscope(self, cx, cy, radius):
        self.canvas.create_oval(
            cx-radius, cy-radius, cx+radius, cy+radius,
            outline="#6b7280", width=2)

        for deg in range(0, 360, 30):
            a = math.radians(deg - 90)
            inner = radius - 12
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

        error = self.phase_error()
        a = error - math.pi / 2
        px = cx + (radius-18) * math.cos(a)
        py = cy + (radius-18) * math.sin(a)

        phase_ok = abs(math.degrees(error)) <= 10
        freq_ok = abs(self.frequency_difference()) <= 0.10
        volt_ok = abs(self.voltage_difference()) <= 1.0
        ready = phase_ok and freq_ok and volt_ok

        self.canvas.create_line(
            cx, cy, px, py, fill=GREEN if ready else BLUE, width=4)
        self.canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill=TEXT, outline="")

        # Small ready zone around 12 o'clock.
        zone = math.radians(10)
        for side in (-1, 1):
            aa = -math.pi/2 + side * zone
            self.canvas.create_line(
                cx, cy,
                cx + (radius-5)*math.cos(aa),
                cy + (radius-5)*math.sin(aa),
                fill=GREEN, width=2)

        self.canvas.create_text(cx, cy+radius+20, text="SYNCHROSCOPE",
                                fill=MUTED, font=("Arial", 9, "bold"))

    def draw_waveform(self, x, y, width, height):
        self.canvas.create_rectangle(
            x, y, x+width, y+height, outline="#263244")
        mid = y + height/2
        self.canvas.create_line(x, mid, x+width, mid, fill="#1f2937")
        self.canvas.create_text(
            x+8, y+8, anchor="nw", text="VOLTAGE WAVEFORM",
            fill=MUTED, font=("Arial", 8, "bold"))

        samples = 180
        for idx, (phase, color, label) in enumerate([
            (self.bus.phase, "#d1d5db", "BUS"),
            (self.generator.phase, BLUE, "GEN")]):
            points = []
            for i in range(samples):
                t = i / (samples-1)
                xx = x + t * width
                yy = mid - math.sin(
                    2*math.pi*2.2*t + phase) * (height*0.30)
                points.extend((xx, yy))

            self.canvas.create_line(
                *points, fill=color, width=2, smooth=True)
            self.canvas.create_text(
                x+width-8, y+12+idx*15, anchor="ne",
                text=label, fill=color, font=("Arial", 8, "bold"))

    def draw_breaker(self, x, y, width):
        # Electrical one-line breaker symbol: two fixed contacts and a
        # movable blade. Open = diagonal blade, closed = horizontal blade.
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

        blade_color = GREEN if self.connected else RED
        blade_end_y = line_y if self.connected else line_y - 30
        self.canvas.create_line(
            left_contact, line_y, right_contact, blade_end_y,
            fill=blade_color, width=7)

        state = "BREAKER CLOSED" if self.connected else "BREAKER OPEN"
        self.canvas.create_text(
            x, y + 43, text=state, fill=blade_color,
            font=("Arial", 10, "bold"))

    def draw(self):
        self.canvas.delete("all")
        w = max(self.canvas.winfo_width(), 600)
        h = max(self.canvas.winfo_height(), 450)

        r = min(w, h) * 0.16
        self.draw_vector(
            w*.22, h*.30, r, "BUS / GRID", self.bus.phase, "#d1d5db")
        self.draw_vector(
            w*.78, h*.30, r, "INCOMING GENERATOR",
            self.generator.phase, BLUE)
        self.draw_synchroscope(w*.50, h*.30, r*0.82)

        self.draw_waveform(w*.08, h*.52, w*.84, h*.25)
        self.draw_breaker(w*.50, h*.85, w*.70)

        phase_deg = math.degrees(self.phase_error())
        df = self.frequency_difference()
        dv = self.voltage_difference()

        self.gen_freq_label.config(text=f"{self.generator.frequency:.2f} Hz")
        self.measurements.config(
            text=(
                f"BUS       {self.bus.frequency:>6.2f} Hz\n"
                f"GEN       {self.generator.frequency:>6.2f} Hz\n"
                f"SETPOINT  {self.frequency_target:>6.2f} Hz\n"
                f"ΔF        {df:>+6.2f} Hz\n"
                f"BUS V     {self.bus.voltage:>6.1f} kV\n"
                f"GEN V     {self.generator.voltage:>6.1f} kV\n"
                f"ΔV        {dv:>+6.1f} kV\n"
                f"PHASE     {phase_deg:>+6.1f}°\n"
                f"RATE      {self.frequency_rate:>6.2f} Hz/s\n"
                f"STATUS    {'CLOSED' if self.connected else 'OPEN'}"
            ))

        if not self.connected:
            ready = (
                abs(phase_deg) <= 10
                and abs(df) <= .10
                and abs(dv) <= 1.0
            )
            self.status.config(
                text="READY TO CLOSE" if ready else "SYNCHRONIZING",
                fg=GREEN if ready else AMBER)


if __name__ == "__main__":
    Synchroscope().mainloop()
