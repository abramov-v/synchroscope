import math
import tkinter as tk

class Synchroscope(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Synchroscope Simulator")
        self.geometry("900x650")
        self.configure(bg="#111827")
        self.running = True
        self.speed = 1.0
        self.phase = 0.0
        self.create_ui()
        self.animate()

    def create_ui(self):
        top = tk.Frame(self, bg="#111827")
        top.pack(fill="x", padx=18, pady=(14, 8))
        tk.Label(top, text="SYNCHROSCOPE", fg="#f9fafb", bg="#111827",
                 font=("Arial", 18, "bold")).pack(side="left")
        tk.Button(top, text="CLOSE", command=self.destroy,
                  bg="#374151", fg="white", relief="flat", padx=16, pady=7).pack(side="right")

        self.canvas = tk.Canvas(self, bg="#0b1220", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=18, pady=8)

        controls = tk.Frame(self, bg="#111827")
        controls.pack(fill="x", padx=18, pady=(8, 16))
        tk.Label(controls, text="Generator speed", fg="#d1d5db", bg="#111827").pack(side="left")
        self.scale = tk.Scale(controls, from_=0.25, to=3.0, resolution=0.25,
                              orient="horizontal", variable=tk.DoubleVar(value=1.0),
                              command=self.set_speed, bg="#111827", fg="#d1d5db",
                              highlightthickness=0, troughcolor="#374151")
        self.scale.pack(side="left", padx=12, fill="x", expand=True)
        self.status = tk.Label(controls, text="SYNCHRONIZING", fg="#60a5fa", bg="#111827",
                               font=("Arial", 11, "bold"))
        self.status.pack(side="right")

    def set_speed(self, value):
        self.speed = float(value)

    def animate(self):
        self.phase += 0.035 * self.speed
        self.draw()
        self.after(30, self.animate)

    def draw(self):
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w/2, h/2
        r = min(w, h) * 0.30

        # synchroscope dial
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline="#6b7280", width=3)
        for deg in range(0, 360, 30):
            a = math.radians(deg-90)
            x1, y1 = cx+(r-14)*math.cos(a), cy+(r-14)*math.sin(a)
            x2, y2 = cx+(r-2)*math.cos(a), cy+(r-2)*math.sin(a)
            self.canvas.create_line(x1,y1,x2,y2, fill="#9ca3af", width=2)

        labels = [("12",0),("3",90),("6",180),("9",270)]
        for txt, deg in labels:
            a=math.radians(deg-90)
            self.canvas.create_text(cx+(r-38)*math.cos(a), cy+(r-38)*math.sin(a),
                                    text=txt, fill="#e5e7eb", font=("Arial", 13, "bold"))

        # phase pointer: speed controls how quickly it rotates toward synchronism
        a = self.phase
        px, py = cx+(r-30)*math.cos(a-math.pi/2), cy+(r-30)*math.sin(a-math.pi/2)
        self.canvas.create_line(cx,cy,px,py, fill="#60a5fa", width=5)
        self.canvas.create_oval(cx-7,cy-7,cx+7,cy+7, fill="#f9fafb", outline="")

        # generator labels
        self.canvas.create_text(cx, cy+r+45, text="Incoming generator ↔ Bus",
                                fill="#d1d5db", font=("Arial", 13))
        self.canvas.create_text(cx, cy+r+70, text=f"Speed: {self.speed:.2f}×",
                                fill="#9ca3af", font=("Arial", 11))

        # synchroscope indication near 12 o'clock
        phase_error = abs(((a + math.pi) % (2*math.pi)) - math.pi)
        synced = phase_error < 0.10
        self.status.config(text="SYNC — CLOSE" if synced else "SYNCHRONIZING",
                           fg="#34d399" if synced else "#60a5fa")

if __name__ == "__main__":
    Synchroscope().mainloop()
