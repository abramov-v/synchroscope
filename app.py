import math
import time
import tkinter as tk
from tkinter import messagebox

BG, PANEL, TEXT, MUTED = "#0b1220", "#111827", "#f9fafb", "#9ca3af"
GRID, BLUE, GREEN, RED, AMBER = "#374151", "#60a5fa", "#34d399", "#f87171", "#fbbf24"

class Generator:
    def __init__(self, name, frequency, phase=0.0):
        self.name, self.frequency, self.phase = name, frequency, phase
    def advance(self, dt):
        self.phase = (self.phase + 2 * math.pi * self.frequency * dt) % (2 * math.pi)

class Synchroscope(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Synchroscope Simulator")
        self.geometry("1100x760")
        self.minsize(850, 620)
        self.configure(bg=BG)
        self.connected, self.time_scale, self.last_time = False, 1.0, time.perf_counter()
        self.bus = Generator("BUS", 50.00, 0.0)
        self.generator = Generator("GENERATOR", 49.80, math.radians(-70))
        self.build_ui()
        self.after(30, self.animate)

    @staticmethod
    def wrap_phase(a):
        return (a + math.pi) % (2 * math.pi) - math.pi

    def phase_error(self):
        return self.wrap_phase(self.generator.phase - self.bus.phase)

    def frequency_difference(self):
        return self.generator.frequency - self.bus.frequency

    def build_ui(self):
        top = tk.Frame(self, bg=BG); top.pack(fill="x", padx=20, pady=(16, 8))
        tk.Label(top, text="SYNCHROSCOPE", fg=TEXT, bg=BG, font=("Arial",20,"bold")).pack(side="left")
        tk.Label(top, text="GENERATOR SYNCHRONIZATION TRAINER", fg=MUTED, bg=BG, font=("Arial",10)).pack(side="left", padx=16)
        tk.Button(top, text="CLOSE WINDOW", command=self.destroy, bg="#374151", fg=TEXT, relief="flat", padx=14, pady=7).pack(side="right")

        body = tk.Frame(self, bg=BG); body.pack(fill="both", expand=True, padx=20, pady=8)
        left = tk.Frame(body, bg=PANEL); left.pack(side="left", fill="both", expand=True, padx=(0,10))
        right = tk.Frame(body, bg=PANEL, width=300); right.pack(side="right", fill="y"); right.pack_propagate(False)
        self.canvas = tk.Canvas(left, bg="#080d18", highlightthickness=0); self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.build_controls(right)

        bottom = tk.Frame(self, bg=BG); bottom.pack(fill="x", padx=20, pady=(8,16))
        self.status = tk.Label(bottom, text="SYNCHRONIZING", fg=AMBER, bg=BG, font=("Arial",12,"bold")); self.status.pack(side="left")
        tk.Label(bottom, text="Match frequency → wait for 12 o'clock → CLOSE BREAKER", fg=MUTED, bg=BG, font=("Arial",10)).pack(side="right")

    def build_controls(self, parent):
        tk.Label(parent, text="INCOMING GENERATOR", fg=TEXT, bg=PANEL, font=("Arial",15,"bold")).pack(anchor="w", padx=18, pady=(18,4))
        self.gen_freq_label = tk.Label(parent, fg=TEXT, bg=PANEL, font=("Arial",18,"bold")); self.gen_freq_label.pack(anchor="w", padx=18)
        tk.Label(parent, text="Frequency (Hz)", fg=MUTED, bg=PANEL).pack(anchor="w", padx=18)
        self.freq_scale = tk.Scale(parent, from_=49.0, to=51.0, resolution=0.01, orient="horizontal", bg=PANEL, fg=TEXT, highlightthickness=0, troughcolor=GRID, activebackground=BLUE, command=self.set_frequency)
        self.freq_scale.set(self.generator.frequency); self.freq_scale.pack(fill="x", padx=18)

        tk.Label(parent, text="Simulation speed", fg=MUTED, bg=PANEL).pack(anchor="w", padx=18, pady=(20,4))
        self.speed_scale = tk.Scale(parent, from_=0.25, to=3.0, resolution=0.25, orient="horizontal", bg=PANEL, fg=TEXT, highlightthickness=0, troughcolor=GRID, activebackground=BLUE, command=self.set_time_scale)
        self.speed_scale.set(1.0); self.speed_scale.pack(fill="x", padx=18)

        self.close_button = tk.Button(parent, text="CLOSE BREAKER", command=self.close_breaker, bg="#374151", fg=TEXT, relief="flat", font=("Arial",12,"bold"), padx=10, pady=12)
        self.close_button.pack(fill="x", padx=18, pady=(28,10))
        tk.Button(parent, text="RESET", command=self.reset, bg="#1f2937", fg=MUTED, relief="flat", padx=10, pady=8).pack(fill="x", padx=18)

        tk.Label(parent, text="MEASUREMENTS", fg=TEXT, bg=PANEL, font=("Arial",11,"bold")).pack(anchor="w", padx=18, pady=(28,8))
        self.measurements = tk.Label(parent, justify="left", anchor="w", fg=MUTED, bg=PANEL, font=("Courier New",10))
        self.measurements.pack(fill="x", padx=18)

    def set_frequency(self, value):
        if not self.connected: self.generator.frequency = float(value)

    def set_time_scale(self, value):
        self.time_scale = float(value)

    def close_breaker(self):
        phase, df = abs(math.degrees(self.phase_error())), abs(self.frequency_difference())
        if phase <= 10 and df <= 0.10:
            self.connected = True
            self.generator.frequency = self.bus.frequency
            self.close_button.config(text="BREAKER CLOSED", state="disabled")
            self.freq_scale.config(state="disabled")
            self.status.config(text="CONNECTED — SYNCHRONIZED", fg=GREEN)
        else:
            messagebox.showwarning("Cannot close breaker", f"Generator is not synchronized yet.\n\nPhase error: {phase:.1f}° (need ≤ 10°)\nFrequency difference: {df:.2f} Hz (need ≤ 0.10 Hz)")

    def reset(self):
        self.connected = False
        self.generator.frequency, self.generator.phase = 49.80, math.radians(-70)
        self.freq_scale.config(state="normal"); self.freq_scale.set(self.generator.frequency)
        self.close_button.config(text="CLOSE BREAKER", state="normal")
        self.status.config(text="SYNCHRONIZING", fg=AMBER)

    def animate(self):
        now = time.perf_counter()
        dt = min(now - self.last_time, 0.1) * self.time_scale
        self.last_time = now
        self.bus.advance(dt)
        if self.connected:
            self.generator.phase, self.generator.frequency = self.bus.phase, self.bus.frequency
        else:
            self.generator.advance(dt)
        self.draw()
        self.after(30, self.animate)

    def draw_vector(self, cx, cy, radius, title, phase, color):
        self.canvas.create_oval(cx-radius,cy-radius,cx+radius,cy+radius,outline="#4b5563")
        self.canvas.create_line(cx-radius,cy,cx+radius,cy,fill="#1f2937")
        self.canvas.create_line(cx,cy-radius,cx,cy+radius,fill="#1f2937")
        a = phase - math.pi/2
        x, y = cx+(radius-10)*math.cos(a), cy+(radius-10)*math.sin(a)
        self.canvas.create_line(cx,cy,x,y,fill=color,width=4)
        self.canvas.create_oval(cx-4,cy-4,cx+4,cy+4,fill=TEXT,outline="")
        self.canvas.create_text(cx,cy-radius-18,text=title,fill=TEXT,font=("Arial",10,"bold"))

    def draw(self):
        self.canvas.delete("all")
        w, h = max(self.canvas.winfo_width(),500), max(self.canvas.winfo_height(),400)
        r = min(w,h)*0.19
        self.draw_vector(w*.24,h*.43,r,"BUS / GRID",self.bus.phase,"#d1d5db")
        self.draw_vector(w*.76,h*.43,r,"INCOMING GENERATOR",self.generator.phase,BLUE)

        cx, cy, sr = w*.50, h*.43, min(w,h)*.15
        self.canvas.create_oval(cx-sr,cy-sr,cx+sr,cy+sr,outline="#6b7280",width=2)
        for deg in range(0,360,30):
            a=math.radians(deg-90); self.canvas.create_line(cx+(sr-12)*math.cos(a),cy+(sr-12)*math.sin(a),cx+(sr-2)*math.cos(a),cy+(sr-2)*math.sin(a),fill="#6b7280",width=2)
        for label,deg in [("12",0),("3",90),("6",180),("9",270)]:
            a=math.radians(deg-90); self.canvas.create_text(cx+(sr-30)*math.cos(a),cy+(sr-30)*math.sin(a),text=label,fill=TEXT,font=("Arial",10,"bold"))
        error=self.phase_error(); a=error-math.pi/2
        px,py=cx+(sr-18)*math.cos(a),cy+(sr-18)*math.sin(a)
        ready=abs(math.degrees(error))<=10 and abs(self.frequency_difference())<=.10
        self.canvas.create_line(cx,cy,px,py,fill=GREEN if ready else BLUE,width=4)
        self.canvas.create_oval(cx-5,cy-5,cx+5,cy+5,fill=TEXT,outline="")
        self.canvas.create_text(cx,cy+sr+22,text="SYNCHROSCOPE",fill=MUTED,font=("Arial",9,"bold"))

        y=h*.84; bx=w*.76; bc=GREEN if self.connected else RED
        self.canvas.create_line(w*.08,y,w*.92,y,fill=GRID,width=4)
        self.canvas.create_oval(bx-9,y-9,bx+9,y+9,fill=bc,outline="")
        self.canvas.create_text(bx,y+24,text="BREAKER CLOSED" if self.connected else "BREAKER OPEN",fill=bc,font=("Arial",10,"bold"))

        phase_deg=math.degrees(error); df=self.frequency_difference()
        self.gen_freq_label.config(text=f"{self.generator.frequency:.2f} Hz")
        self.measurements.config(text=f"BUS       {self.bus.frequency:>6.2f} Hz\nGEN       {self.generator.frequency:>6.2f} Hz\nΔF        {df:>+6.2f} Hz\nPHASE     {phase_deg:>+6.1f}°\nSTATUS    {'CLOSED' if self.connected else 'OPEN'}")
        if not self.connected: self.status.config(text="READY TO CLOSE" if ready else "SYNCHRONIZING", fg=GREEN if ready else AMBER)

if __name__ == "__main__":
    Synchroscope().mainloop()
