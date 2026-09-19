"""Canvas drawing."""

import math
import time

import config


class DrawingMixin:
    def draw_vector(self, cx, cy, radius, title, color, relative_offset=0.0):
        self.canvas.create_oval(
            cx-radius, cy-radius, cx+radius, cy+radius,
            outline="#4b5563")
        self.canvas.create_line(cx-radius, cy, cx+radius, cy, fill="#1f2937")
        self.canvas.create_line(cx, cy-radius, cx, cy+radius, fill="#1f2937")

        angle = self.visual_phase + relative_offset - math.pi / 2
        x = cx + (radius - 10) * math.cos(angle)
        y = cy + (radius - 10) * math.sin(angle)

        self.canvas.create_line(cx, cy, x, y, fill="#1f2937", width=9)
        self.canvas.create_line(cx, cy, x, y, fill=color, width=4)
        self.canvas.create_oval(cx-4, cy-4, cx+4, cy+4, fill=config.TEXT, outline="")
        self.canvas.create_text(
            cx, cy-radius-16, text=title,
            fill=config.TEXT, font=("Arial", 10, "bold"))

    def draw_slip_indicator(self, cx, cy, radius):
        """Show which way the generator phase is moving around the clock."""
        df = self.simulation.frequency_difference()

        if abs(df) < config.SLIP_HOLD_LIMIT_HZ:
            state = "HOLD"
            color = config.GREEN
            direction = 0
        elif df > 0:
            state = "FAST  ↻"
            color = config.BLUE
            direction = 1
        else:
            state = "SLOW  ↺"
            color = config.AMBER
            direction = -1

        ring_r = radius + 16

        if direction:
            start = math.radians(-145)
            end = math.radians(-35)
            if direction < 0:
                start, end = end, start

            steps = 24
            points = []
            for i in range(steps + 1):
                angle = start + (end - start) * i / steps
                points.extend((
                    cx + ring_r * math.cos(angle),
                    cy + ring_r * math.sin(angle),
                ))
            self.canvas.create_line(
                *points, fill=color, width=3, smooth=True)

            angle = end
            tip_x = cx + ring_r * math.cos(angle)
            tip_y = cy + ring_r * math.sin(angle)
            tangent = 1 if direction > 0 else -1
            tx, ty = -math.sin(angle) * tangent, math.cos(angle) * tangent
            nx, ny = math.cos(angle), math.sin(angle)
            size = 10
            p1 = (tip_x, tip_y)
            p2 = (tip_x - tx * size - nx * 4, tip_y - ty * size - ny * 4)
            p3 = (tip_x - tx * size + nx * 4, tip_y - ty * size + ny * 4)
            self.canvas.create_polygon(
                *p1, *p2, *p3, fill=color, outline="")

        self.canvas.create_text(
            cx, cy + radius + 40,
            text=state,
            fill=color,
            font=("Arial", 9, "bold"))

        if direction > 0:
            hint = "GENERATOR FASTER — REDUCE FREQUENCY"
        elif direction < 0:
            hint = "GENERATOR SLOWER — INCREASE FREQUENCY"
        else:
            hint = "FREQUENCY MATCH — HOLD"

        self.canvas.create_text(
            cx, cy + radius + 56,
            text=hint,
            fill=config.MUTED,
            font=("Arial", 7, "bold"))

    def draw_synchroscope(self, cx, cy, radius):
        self.canvas.create_oval(
            cx-radius, cy-radius, cx+radius, cy+radius,
            fill=config.BG, outline="#6b7280", width=2)

        error = self.simulation.phase_error()
        phase_ok, freq_ok, volt_ok, ready = self.simulation.sync_state()

        zone = math.radians(config.SYNC_PHASE_LIMIT_DEG)
        gate_color = config.GREEN if ready else (
            config.AMBER if phase_ok else "#4b5563")
        for side in (-1, 1):
            angle = -math.pi / 2 + side * zone
            self.canvas.create_line(
                cx, cy,
                cx + (radius-5)*math.cos(angle),
                cy + (radius-5)*math.sin(angle),
                fill=gate_color, width=5)
        if ready:
            pulse = 0.55 + 0.45 * math.sin(time.perf_counter() * 6.0)
            glow = "#86efac" if pulse > 0.8 else config.GREEN
            self.canvas.create_oval(
                cx-radius+5, cy-radius+5, cx+radius-5, cy+radius-5,
                outline=glow, width=2)

        for deg in range(0, 360, 30):
            angle = math.radians(deg - 90)
            inner, outer = radius - 14, radius - 2
            self.canvas.create_line(
                cx + inner*math.cos(angle), cy + inner*math.sin(angle),
                cx + outer*math.cos(angle), cy + outer*math.sin(angle),
                fill="#6b7280", width=2)

        for label, deg in [("12", 0), ("3", 90), ("6", 180), ("9", 270)]:
            angle = math.radians(deg - 90)
            self.canvas.create_text(
                cx + (radius-30)*math.cos(angle),
                cy + (radius-30)*math.sin(angle),
                text=label, fill=config.TEXT, font=("Arial", 10, "bold"))

        angle = error - math.pi / 2
        px = cx + (radius-18) * math.cos(angle)
        py = cy + (radius-18) * math.sin(angle)
        pointer_color = (
            config.GREEN if ready
            else config.AMBER if phase_ok and freq_ok
            else config.BLUE
        )

        self.canvas.create_line(cx, cy, px, py, fill="#1f2937", width=9)
        self.canvas.create_line(cx, cy, px, py, fill=pointer_color, width=4)
        self.canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill=config.TEXT, outline="")
        self.canvas.create_text(
            cx, cy+radius+20, text="SYNCHROSCOPE",
            fill=config.GREEN if ready else config.MUTED,
            font=("Arial", 9, "bold"))
        self.draw_slip_indicator(cx, cy, radius)
        if ready:
            self.canvas.create_text(
                cx, cy-radius-31,
                text="● CLOSE NOW",
                fill=config.GREEN,
                font=("Arial", 9, "bold"))

    def draw_waveform(self, x, y, width, height):
        self.canvas.create_rectangle(
            x, y, x+width, y+height, outline="#263244")
        mid = y + height/2
        self.canvas.create_line(x, mid, x+width, mid, fill="#1f2937")

        df = self.simulation.frequency_difference()
        phase = self.simulation.phase_error()
        self.canvas.create_text(
            x+8, y+8, anchor="nw",
            text="VOLTAGE WAVEFORM • RELATIVE PHASE",
            fill=config.MUTED, font=("Arial", 8, "bold"))
        self.canvas.create_text(
            x+width-8, y+8, anchor="ne",
            text=f"ΔF {df:+.3f} Hz",
            fill=config.GREEN if abs(df) < config.SYNC_FREQUENCY_LIMIT_HZ else config.BLUE,
            font=("Arial", 8, "bold"))

        samples = 240
        for color, label, relative_phase, voltage in [
            (config.BUS_WAVEFORM, "BUS", 0.0, self.simulation.bus.voltage),
            (config.GEN_WAVEFORM, "GEN", phase, self.simulation.generator.voltage),
        ]:
            points = []
            amplitude = height * 0.30 * max(
                0.15, min(1.20, voltage / config.BUS_VOLTAGE))
            for i in range(samples):
                t = i / (samples - 1)
                local_phase = 2 * math.pi * 2.2 * t + relative_phase
                points.extend((
                    x + t * width,
                    mid - math.sin(local_phase) * amplitude,
                ))
            self.canvas.create_line(*points, fill=color, width=2, smooth=True)
            self.canvas.create_text(
                x+width-8, y+22 + (0 if label == "BUS" else 15),
                anchor="ne", text=f"{label} {voltage:.1f} kV",
                fill=color, font=("Arial", 8, "bold"))

    def draw_breaker(self, x, y, width):
        # Simplified one-line diagram:
        # BUS / GRID ---- [ BREAKER ] ---- INCOMING GENERATOR
        left = x - width / 2
        right = x + width / 2
        gap = 28
        left_contact = x - gap
        right_contact = x + gap
        line_y = y + 8

        # Bus side and generator side conductors.
        self.canvas.create_line(
            left, line_y, left_contact, line_y,
            fill=config.GREEN, width=5)
        self.canvas.create_line(
            right_contact, line_y, right, line_y,
            fill=config.BLUE, width=5)

        # Simple bus/grid marker.
        for offset in (-7, 0, 7):
            self.canvas.create_line(
                left + 18, line_y - 12 + offset,
                left + 18, line_y + 12 + offset,
                fill=config.GREEN, width=2)

        # Generator marker.
        self.canvas.create_oval(
            right - 25, line_y - 13, right - 1, line_y + 13,
            outline=config.BLUE, width=2)
        self.canvas.create_text(
            right - 13, line_y, text="G",
            fill=config.BLUE, font=("Arial", 9, "bold"))

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
            blade_color = config.AMBER
            state = "BREAKER CLOSING..."
        else:
            blade_color = config.GREEN if self.connected else config.RED
            blade_end_y = line_y if self.connected else line_y - 30
            state = "BREAKER CLOSED" if self.connected else "BREAKER OPEN"

        # Keep the original animated breaker blade.
        self.canvas.create_line(
            left_contact, line_y, right_contact, blade_end_y,
            fill=blade_color, width=7)

        self.canvas.create_text(
            left + 35, y - 18,
            text="BUS / GRID", fill=config.GREEN,
            font=("Arial", 9, "bold"), anchor="w")
        self.canvas.create_text(
            right - 35, y - 18,
            text="INCOMING GENERATOR", fill=config.BLUE,
            font=("Arial", 9, "bold"), anchor="e")
        self.canvas.create_text(
            x, y + 43, text=state, fill=blade_color,
            font=("Arial", 10, "bold"))

    def draw(self):
        self.canvas.delete("all")
        w = max(self.canvas.winfo_width(), 600)
        h = max(self.canvas.winfo_height(), 450)
        radius = min(w, h) * 0.16

        self.draw_vector(w*.22, h*.30, radius, "BUS / GRID", config.GREEN, 0.0)
        self.draw_vector(
            w*.78, h*.30, radius, "INCOMING GENERATOR",
            config.BLUE, self.simulation.phase_error())
        self.draw_synchroscope(w*.50, h*.30, radius*0.92)
        self.draw_waveform(w*.08, h*.52, w*.84, h*.25)
        self.draw_breaker(w*.50, h*.85, w*.70)

        phase_deg = self.simulation.phase_error_degrees()
        df = self.simulation.frequency_difference()
        dv = self.simulation.voltage_difference()
        phase_ok, freq_ok, volt_ok, ready = self.simulation.sync_state()

        mark = lambda ok: "✓ OK" if ok else "✕ WAIT"
        self.phase_big.config(
            text=f"PHASE  {phase_deg:+.1f}°  {'READY' if phase_ok else 'WAIT'}",
            fg=config.GREEN if phase_ok else config.AMBER)
        self.sync_check.config(
            text=(
                f"PHASE       {mark(phase_ok):<6}  ≤ 10°\n"
                f"ΔF          {mark(freq_ok):<6}  < 0.067 Hz\n"
                f"ΔV          {mark(volt_ok):<6}  ≤ 1.0 kV\n"
                f"\n{'READY TO CLOSE' if ready else 'NOT READY'}"
            ),
            fg=config.GREEN if ready else config.AMBER)

        self.gen_freq_label.config(
            text=f"{self.simulation.generator.frequency:.2f} Hz")
        self.measurements.config(
            text=(
                f"BUS/GEN   {self.simulation.bus.frequency:.2f}/{self.simulation.generator.frequency:.2f} Hz\n"
                f"ΔF        {df:+.3f} Hz\n"
                f"BUS/GEN V {self.simulation.bus.voltage:.2f}/{self.simulation.generator.voltage:.2f} kV\n"
                f"ΔV        {dv:+.2f} kV\n"
                f"PHASE     {phase_deg:+.1f}°\n"
                f"SLIP      {abs(df):.3f} Hz\n"
                f"STATUS    {'CLOSED' if self.connected else 'OPEN'}"
            ))
        self.slip_label.config(
            text=f"SLIP  {df:+.3f} Hz",
            fg=config.GREEN if abs(df) < config.SYNC_FREQUENCY_LIMIT_HZ else config.MUTED)

        if self.connected:
            self.status.config(text="CONNECTED — SYNCHRONIZED", fg=config.GREEN)
        elif self.breaker_animating:
            self.status.config(text="CLOSING BREAKER...", fg=config.AMBER)
        else:
            self.status.config(
                text="READY TO CLOSE" if ready else "SYNCHRONIZING",
                fg=config.GREEN if ready else config.AMBER)
