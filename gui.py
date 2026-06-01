from __future__ import annotations

import math
import tkinter as tk

from acoustic_consensus.main import run_once


BG = "#1e1e2f"
FG = "#f4f4ff"
ACCENT = "#7a5cff"


class AcousticConsensusGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Acoustic Consensus")
        self.geometry("900x620")
        self.configure(bg=BG)
        self.current_screen: tk.Frame | None = None
        self.phase = 0
        self.context_id = 0
        self.show_start_screen()

    def _swap(self, frame: tk.Frame) -> None:
        if self.current_screen:
            self.current_screen.destroy()
        self.current_screen = frame
        frame.pack(fill="both", expand=True)

    def show_start_screen(self) -> None:
        frame = tk.Frame(self, bg=BG)
        canvas = tk.Canvas(frame, bg=BG, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        title = canvas.create_text(450, 80, text="Acoustic\nConsensus", fill=FG, font=("Helvetica", 40, "bold"))
        _ = title

        rings = [canvas.create_oval(0, 0, 0, 0, outline="#4c3ab3", width=2) for _ in range(4)]

        def animate(step: int = 0) -> None:
            center_x, center_y = 450, 260
            for idx, ring in enumerate(rings):
                radius = 40 + ((step + idx * 10) % 90) * 3
                alpha_color = ["#3a2b8a", "#4a39a6", "#5d48c4", "#7a5cff"][idx]
                canvas.itemconfig(ring, outline=alpha_color)
                canvas.coords(ring, center_x - radius, center_y - radius, center_x + radius, center_y + radius)
            frame.after(80, animate, step + 1)

        animate()

        button_points = [350, 430, 390, 390, 510, 390, 550, 430, 510, 470, 390, 470]
        button = canvas.create_polygon(button_points, fill=ACCENT, outline="#b5a9ff", width=3)
        label = canvas.create_text(450, 430, text="Begin Consensus", fill=FG, font=("Helvetica", 16, "bold"))

        def start(_event: object) -> None:
            self.show_transition_screen(self.show_recording_screen)

        canvas.tag_bind(button, "<Button-1>", start)
        canvas.tag_bind(label, "<Button-1>", start)

        self._swap(frame)

    def show_transition_screen(self, next_screen: callable) -> None:
        frame = tk.Frame(self, bg=BG)
        canvas = tk.Canvas(frame, bg=BG, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        dot = canvas.create_oval(430, 290, 470, 330, fill=ACCENT, outline="")

        def animate(radius: int = 20, shrinking: bool = True) -> None:
            if shrinking:
                radius -= 4
                if radius <= 4:
                    shrinking = False
            else:
                radius += 10
                if radius > 500:
                    next_screen()
                    return
            canvas.coords(dot, 450 - radius, 310 - radius, 450 + radius, 310 + radius)
            frame.after(30, animate, radius, shrinking)

        animate()
        self._swap(frame)

    def show_recording_screen(self) -> None:
        frame = tk.Frame(self, bg=BG)
        canvas = tk.Canvas(frame, bg=BG, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        canvas.create_text(450, 50, text="Recording & Feature Extraction", fill=FG, font=("Helvetica", 24, "bold"))

        gauge = canvas.create_arc(300, 130, 600, 430, start=90, extent=0, style="arc", outline=ACCENT, width=14)
        timeline_y = 500
        canvas.create_line(170, timeline_y, 730, timeline_y, fill="#6f67a6", width=3)

        stars = []
        for x in (260, 450, 640):
            stars.append(canvas.create_polygon([x, timeline_y - 22, x + 8, timeline_y - 6, x + 24, timeline_y - 6, x + 11, timeline_y + 4, x + 16, timeline_y + 20, x, timeline_y + 10, x - 16, timeline_y + 20, x - 11, timeline_y + 4, x - 24, timeline_y - 6, x - 8, timeline_y - 6], fill="#3f3966", outline="#b3abeb"))

        points = [canvas.create_oval(0, 0, 0, 0, fill="#88ffd7", outline="") for _ in range(20)]
        lines = [canvas.create_line(0, 0, 0, 0, fill="#88ffd788") for _ in range(10)]

        def animate(step: int = 0) -> None:
            extent = min(360, step * 6)
            canvas.itemconfig(gauge, extent=-extent)

            coords = []
            for i, point in enumerate(points):
                angle = (step * 0.06 + i * 0.35) % (2 * math.pi)
                radius = 70 + (i % 5) * 22
                x = 450 + int(math.cos(angle) * radius)
                y = 280 + int(math.sin(angle) * radius)
                canvas.coords(point, x - 4, y - 4, x + 4, y + 4)
                coords.append((x, y))

            for i, line in enumerate(lines):
                x1, y1 = coords[i]
                x2, y2 = coords[(i + 5) % len(coords)]
                canvas.coords(line, x1, y1, x2, y2)

            for idx, star in enumerate(stars):
                canvas.itemconfig(star, fill="#ffd166" if step > (idx + 1) * 20 else "#3f3966")

            if step < 60:
                frame.after(80, animate, step + 1)
            else:
                self.show_transition_screen(self.show_consensus_rounds)

        animate()
        self._swap(frame)

    def show_consensus_rounds(self) -> None:
        frame = tk.Frame(self, bg=BG)
        canvas = tk.Canvas(frame, bg=BG, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        canvas.create_text(450, 60, text="Consensus Rounds", fill=FG, font=("Helvetica", 24, "bold"))
        badge = canvas.create_polygon([700, 30, 860, 30, 860, 100, 745, 100, 700, 145], fill="#332c5d", outline="#9f94e0", width=2)
        _ = badge
        canvas.create_text(785, 70, text="Device\nLocal", fill=FG, font=("Helvetica", 12, "bold"))

        circles = [canvas.create_oval(180 + i * 180, 200, 280 + i * 180, 300, fill="#4b456d", outline="#aba3de", width=2) for i in range(3)]
        for i in range(3):
            canvas.create_text(230 + i * 180, 320, text=f"Round {i + 1}", fill=FG, font=("Helvetica", 13, "bold"))

        chain_boxes = [canvas.create_rectangle(220 + i * 56, 400, 260 + i * 56, 440, fill="#3d3664", outline="#8f86c9", width=2) for i in range(8)]
        for i in range(7):
            canvas.create_line(260 + i * 56, 420, 276 + i * 56, 420, fill="#8f86c9", width=3)

        def animate(round_step: int = 0) -> None:
            for i, circle in enumerate(circles):
                color = "#4b456d"
                if round_step > i:
                    color = "#ffbf47" if round_step == i + 1 else "#5dd39e"
                canvas.itemconfig(circle, fill=color)

            for i, box in enumerate(chain_boxes):
                canvas.itemconfig(box, fill="#7a5cff" if i < min(8, round_step * 3) else "#3d3664")

            if round_step < 3:
                frame.after(900, animate, round_step + 1)
            else:
                self.context_id = run_once(duration=0.2, rounds=1, round_seconds=0.1)
                self.show_transition_screen(self.show_result_screen)

        animate()
        self._swap(frame)

    def show_result_screen(self) -> None:
        frame = tk.Frame(self, bg=BG)
        canvas = tk.Canvas(frame, bg=BG, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        canvas.create_text(450, 70, text="Context ID", fill=FG, font=("Helvetica", 26, "bold"))
        ctx_text = f"{self.context_id:08X}"

        for i, ch in enumerate(ctx_text):
            x = 110 + i * 95
            poly = [x, 290, x + 25, 250, x + 70, 250, x + 95, 290, x + 70, 330, x + 25, 330]
            canvas.create_polygon(poly, fill="#2f2954", outline="#b6a9ff", width=2)
            canvas.create_text(x + 47, 290, text=ch, fill="#e8e3ff", font=("Courier", 22, "bold"))

        spiral = canvas.create_line(450, 430, 450, 430, fill="#79ffb2", width=6, smooth=True)

        def draw_check(step: int = 0) -> None:
            points = []
            for i in range(step):
                t = i / 50
                x = 350 + 200 * t
                y = 460 - 70 * math.sin(t * math.pi)
                points.extend([x, y])
            if points:
                canvas.coords(spiral, *points)
            if step < 50:
                frame.after(25, draw_check, step + 1)

        draw_check()

        share = canvas.create_polygon([360, 530, 420, 515, 480, 530, 540, 515, 540, 545, 480, 560, 420, 545, 360, 560], fill=ACCENT, outline="#d9d0ff", width=2)
        text = canvas.create_text(450, 538, text="Share", fill=FG, font=("Helvetica", 14, "bold"))

        def restart(_event: object) -> None:
            self.show_transition_screen(self.show_start_screen)

        canvas.tag_bind(share, "<Button-1>", restart)
        canvas.tag_bind(text, "<Button-1>", restart)

        self._swap(frame)


if __name__ == "__main__":
    app = AcousticConsensusGUI()
    app.mainloop()
