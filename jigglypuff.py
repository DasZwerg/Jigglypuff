import customtkinter as ctk
import pyautogui
import threading
import time
import random
import os
import subprocess
import platform
import sys
from datetime import datetime, time as dtime

pyautogui.FAILSAFE = True

if getattr(sys, 'frozen', False):
    DIR_PATH = sys._MEIPASS
else:
    DIR_PATH = os.path.dirname(os.path.realpath(__file__))

MUSIC_PATH = os.path.join(DIR_PATH, "audio/yay.mp3")

SPEED_MAP = {
    "Slow":   2.0,
    "Medium": 0.8,
    "Fast":   0.2,
}

INTENSITY_MAP = {
    "Small":  (10,  80),
    "Medium": (100, 300),
    "Wild":   (300, 900),
}


def play_sound(path: str) -> None:
    if platform.system() == "Darwin" and os.path.exists(path):
        subprocess.Popen(["afplay", path])


def get_random_coords(intensity: str, stealth: bool, current_x: int, current_y: int) -> tuple[int, int]:
    screen = pyautogui.size()
    if stealth:
        offset = random.randint(1, 5)
        x = max(10, min(screen[0] - 10, current_x + random.choice([-offset, offset])))
        y = max(10, min(screen[1] - 10, current_y + random.choice([-offset, offset])))
        return x, y
    lo, _ = INTENSITY_MAP.get(intensity, (100, 300))
    x = random.randint(lo, screen[0] - lo)
    y = random.randint(lo, screen[1] - lo)
    return x, y


class JigglerEngine:
    def __init__(self, on_stop):
        self.on_stop = on_stop
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

        self.keep_alive = True
        self.app_switching = False
        self.stealth_mode = False
        self.intensity = "Medium"
        self.speed = "Medium"
        self.interval = 30
        self.schedule_enabled = False
        self.schedule_start = dtime(9, 0)
        self.schedule_end = dtime(17, 0)

        self.total_jiggles = 0
        self.total_switches = 0
        self.session_start: float | None = None
        self.last_action = "—"

    def _within_schedule(self) -> bool:
        if not self.schedule_enabled:
            return True
        now = datetime.now().time()
        return self.schedule_start <= now <= self.schedule_end

    def _jiggle_once(self) -> None:
        try:
            cx, cy = pyautogui.position()
            x, y = get_random_coords(self.intensity, self.stealth_mode, cx, cy)
            duration = SPEED_MAP.get(self.speed, 0.8)
            pyautogui.moveTo(x, y, duration=duration)
            self.total_jiggles += 1
            self.last_action = f"Moved to ({x}, {y})"
        except pyautogui.FailSafeException:
            self._stop_event.set()
        except Exception as e:
            self.last_action = f"Move error: {e}"

    def _switch_apps(self) -> None:
        try:
            switches = random.randint(1, 5)
            pyautogui.keyDown('command')
            for _ in range(switches):
                pyautogui.press('tab')
            pyautogui.keyUp('command')
            self.total_switches += switches
            self.last_action = f"Switched apps ({switches}x)"
        except pyautogui.FailSafeException:
            self._stop_event.set()
        except Exception as e:
            self.last_action = f"Switch error: {e}"

    def _run(self) -> None:
        self.session_start = time.time()
        try:
            cx, cy = pyautogui.position()
            pyautogui.moveTo(cx, cy, duration=0)
        except Exception as e:
            self.last_action = f"Permission error: {e}"
            self.on_stop()
            return
        try:
            while not self._stop_event.is_set():
                if self._within_schedule():
                    if self.keep_alive:
                        self._jiggle_once()
                    if self.app_switching:
                        self._switch_apps()
                interval = self.interval
                elapsed = 0
                while elapsed < interval and not self._stop_event.is_set():
                    time.sleep(0.5)
                    elapsed += 0.5
        except Exception as e:
            self.last_action = f"Engine error: {e}"
        finally:
            self.on_stop()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def panic(self) -> None:
        self.stop()
        screen = pyautogui.size()
        pyautogui.moveTo(screen[0] // 2, screen[1] // 2, duration=0.3)
        self.last_action = "PANIC — moved to center"

    def uptime(self) -> str:
        if self.session_start is None:
            return "0s"
        secs = int(time.time() - self.session_start)
        h, rem = divmod(secs, 3600)
        m, s = divmod(rem, 60)
        if h:
            return f"{h}h {m}m {s}s"
        if m:
            return f"{m}m {s}s"
        return f"{s}s"


class JigglyPuffApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.engine = JigglerEngine(
            on_stop=self._on_engine_stop,
        )

        self.title("JigglyPuff")
        self.geometry("480x720")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self._running = False
        self._build_ui()
        self._start_stats_loop()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        # ── Header ──────────────────────────────────────────────
        header = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 4))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="🎵 JigglyPuff",
            font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        self._status_pill = ctk.CTkLabel(
            header, text="  IDLE  ",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#444444", corner_radius=10,
            text_color="#aaaaaa", width=70
        )
        self._status_pill.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            header, text="Keep your machine awake and looking busy.",
            font=ctk.CTkFont(size=12), text_color="#888888"
        ).grid(row=1, column=0, columnspan=2, sticky="w")

        # ── Start / Stop ─────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self._start_btn = ctk.CTkButton(
            btn_frame, text="▶  START",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=44, corner_radius=10,
            command=self._toggle_running
        )
        self._start_btn.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        ctk.CTkButton(
            btn_frame, text="🚨 PANIC",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=44, corner_radius=10,
            fg_color="#c62828", hover_color="#b71c1c",
            command=self._panic
        ).grid(row=0, column=1, padx=(6, 0), sticky="ew")

        # ── Core Toggles ─────────────────────────────────────────
        self._section("Core Features", row=2)
        core = self._card(row=3)

        self._keep_alive_var = ctk.BooleanVar(value=True)
        self._row_toggle(core, 0, "🖥  Keep Screen Alive",
                         "Move mouse to prevent sleep", self._keep_alive_var,
                         self._on_keep_alive)

        self._app_switch_var = ctk.BooleanVar(value=False)
        self._row_toggle(core, 1, "⇥  App Switching",
                         "Cycle through open windows (Cmd+Tab)", self._app_switch_var,
                         self._on_app_switch)

        self._stealth_var = ctk.BooleanVar(value=False)
        self._row_toggle(core, 2, "👁  Stealth Mode",
                         "Move mouse ≤5px — nearly undetectable", self._stealth_var,
                         self._on_stealth)

        # ── Interval Slider ───────────────────────────────────────
        self._section("Movement Interval", row=4)
        interval_card = self._card(row=5)

        self._interval_label = ctk.CTkLabel(
            interval_card, text="30s between moves",
            font=ctk.CTkFont(size=12), text_color="#aaaaaa"
        )
        self._interval_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(10, 2))

        self._interval_slider = ctk.CTkSlider(
            interval_card, from_=5, to=300, number_of_steps=59,
            command=self._on_interval_change
        )
        self._interval_slider.set(30)
        self._interval_slider.grid(row=1, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 12))

        # ── Movement Settings ─────────────────────────────────────
        self._section("Movement Settings", row=6)
        move_card = self._card(row=7)

        ctk.CTkLabel(move_card, text="Speed",
                     font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(10, 2))
        self._speed_seg = ctk.CTkSegmentedButton(
            move_card, values=["Slow", "Medium", "Fast"],
            command=self._on_speed_change
        )
        self._speed_seg.set("Medium")
        self._speed_seg.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 8))

        ctk.CTkLabel(move_card, text="Intensity",
                     font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=2, column=0, sticky="w", padx=14, pady=(4, 2))
        self._intensity_seg = ctk.CTkSegmentedButton(
            move_card, values=["Small", "Medium", "Wild"],
            command=self._on_intensity_change
        )
        self._intensity_seg.set("Medium")
        self._intensity_seg.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 12))

        move_card.grid_columnconfigure(0, weight=1)

        # ── Schedule ──────────────────────────────────────────────
        self._section("Schedule", row=8)
        sched_card = self._card(row=9)
        sched_card.grid_columnconfigure(0, weight=1)

        self._schedule_var = ctk.BooleanVar(value=False)
        self._row_toggle(sched_card, 0, "🕐  Active Hours Only",
                         "Only jiggle within a set time window", self._schedule_var,
                         self._on_schedule_toggle)

        time_row = ctk.CTkFrame(sched_card, fg_color="transparent")
        time_row.grid(row=1, column=0, columnspan=4, sticky="ew", padx=14, pady=(4, 12))
        time_row.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        ctk.CTkLabel(time_row, text="From", font=ctk.CTkFont(size=11),
                     text_color="#888888").grid(row=0, column=0, sticky="e", padx=(0, 4))

        self._start_hour = ctk.CTkEntry(time_row, width=48, placeholder_text="09")
        self._start_hour.grid(row=0, column=1, padx=2)
        self._start_hour.insert(0, "09")

        ctk.CTkLabel(time_row, text="to", font=ctk.CTkFont(size=11),
                     text_color="#888888").grid(row=0, column=2, padx=4)

        self._end_hour = ctk.CTkEntry(time_row, width=48, placeholder_text="17")
        self._end_hour.grid(row=0, column=3, padx=2)
        self._end_hour.insert(0, "17")

        ctk.CTkLabel(time_row, text="(24h)", font=ctk.CTkFont(size=10),
                     text_color="#555555").grid(row=0, column=4, sticky="w", padx=(4, 0))

        # ── Stats ─────────────────────────────────────────────────
        self._section("Session Stats", row=10)
        stats_card = self._card(row=11)
        stats_card.grid_columnconfigure((0, 1, 2), weight=1)

        self._stat_jiggles = self._stat_cell(stats_card, "Jiggles", "0", col=0)
        self._stat_uptime = self._stat_cell(stats_card, "Uptime", "0s", col=1)
        self._stat_switches = self._stat_cell(stats_card, "Switches", "0", col=2)
        self._last_action_label = ctk.CTkLabel(
            stats_card, text="Last: —",
            font=ctk.CTkFont(size=10), text_color="#666666"
        )
        self._last_action_label.grid(row=1, column=0, columnspan=3, pady=(0, 10), padx=14, sticky="w")

        # ── Footer ────────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Failsafe: slam mouse to any screen corner to abort.",
            font=ctk.CTkFont(size=10), text_color="#444444"
        ).grid(row=12, column=0, pady=(8, 14))

    # ── UI helpers ──────────────────────────────────────────────

    def _section(self, title: str, row: int) -> None:
        ctk.CTkLabel(
            self, text=title.upper(),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#555555"
        ).grid(row=row, column=0, sticky="w", padx=24, pady=(12, 2))

    def _card(self, row: int) -> ctk.CTkFrame:
        card = ctk.CTkFrame(self, corner_radius=12)
        card.grid(row=row, column=0, sticky="ew", padx=16, pady=2)
        card.grid_columnconfigure(0, weight=1)
        return card

    def _row_toggle(self, parent, row: int, title: str, subtitle: str,
                    var: ctk.BooleanVar, command) -> None:
        parent.grid_columnconfigure(0, weight=1)
        text_col = ctk.CTkFrame(parent, fg_color="transparent")
        text_col.grid(row=row, column=0, sticky="w", padx=14, pady=(10, 10))
        ctk.CTkLabel(text_col, text=title,
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(text_col, text=subtitle,
                     font=ctk.CTkFont(size=11), text_color="#666666").pack(anchor="w")
        ctk.CTkSwitch(parent, text="", variable=var, command=command,
                      width=44).grid(row=row, column=1, padx=14)

    def _stat_cell(self, parent, label: str, value: str, col: int) -> ctk.CTkLabel:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, padx=10, pady=(12, 4), sticky="nsew")
        val_label = ctk.CTkLabel(frame, text=value,
                                 font=ctk.CTkFont(size=22, weight="bold"))
        val_label.pack()
        ctk.CTkLabel(frame, text=label,
                     font=ctk.CTkFont(size=10), text_color="#666666").pack()
        return val_label

    # ── Engine callbacks ─────────────────────────────────────────

    def _on_engine_stop(self) -> None:
        self.after(0, self._set_stopped_state)

    def _set_stopped_state(self) -> None:
        self._running = False
        self._start_btn.configure(text="▶  START", fg_color=("#2CC985", "#2FA572"))
        self._status_pill.configure(text="  IDLE  ", fg_color="#444444", text_color="#aaaaaa")

    # ── Control callbacks ────────────────────────────────────────

    def _toggle_running(self) -> None:
        if self._running:
            self.engine.stop()
            self._running = False
            self._start_btn.configure(text="▶  START", fg_color=("#2CC985", "#2FA572"))
            self._status_pill.configure(text="  IDLE  ", fg_color="#444444", text_color="#aaaaaa")
        else:
            self._apply_schedule_settings()
            self.engine.session_start = None
            self.engine.total_jiggles = 0
            self.engine.total_switches = 0
            self.engine.start()
            self._running = True
            self._start_btn.configure(text="⏹  STOP", fg_color=("#c62828", "#b71c1c"))
            self._status_pill.configure(text=" ACTIVE ", fg_color="#1b5e20", text_color="#00e676")

    def _panic(self) -> None:
        self.engine.panic()
        self._running = False
        self._start_btn.configure(text="▶  START", fg_color=("#2CC985", "#2FA572"))
        self._status_pill.configure(text="  IDLE  ", fg_color="#444444", text_color="#aaaaaa")
        play_sound(MUSIC_PATH)

    def _on_keep_alive(self) -> None:
        self.engine.keep_alive = self._keep_alive_var.get()

    def _on_app_switch(self) -> None:
        self.engine.app_switching = self._app_switch_var.get()

    def _on_stealth(self) -> None:
        self.engine.stealth_mode = self._stealth_var.get()
        if self._stealth_var.get():
            self._intensity_seg.configure(state="disabled")
        else:
            self._intensity_seg.configure(state="normal")

    def _on_interval_change(self, value: float) -> None:
        secs = int(value)
        self.engine.interval = secs
        self._interval_label.configure(text=f"{secs}s between moves")

    def _on_speed_change(self, value: str) -> None:
        self.engine.speed = value

    def _on_intensity_change(self, value: str) -> None:
        self.engine.intensity = value

    def _on_schedule_toggle(self) -> None:
        self.engine.schedule_enabled = self._schedule_var.get()

    def _apply_schedule_settings(self) -> None:
        try:
            start_h = max(0, min(23, int(self._start_hour.get())))
            end_h = max(0, min(23, int(self._end_hour.get())))
            self.engine.schedule_start = dtime(start_h, 0)
            self.engine.schedule_end = dtime(end_h, 59)
        except ValueError:
            pass

    # ── Stats loop ───────────────────────────────────────────────

    def _start_stats_loop(self) -> None:
        self._update_stats()

    def _update_stats(self) -> None:
        self._stat_jiggles.configure(text=str(self.engine.total_jiggles))
        self._stat_uptime.configure(text=self.engine.uptime() if self._running else "—")
        self._stat_switches.configure(text=str(self.engine.total_switches))
        self._last_action_label.configure(text=f"Last: {self.engine.last_action}")
        self.after(1000, self._update_stats)


def bring_to_front(window: ctk.CTk) -> None:
    if platform.system() == "Darwin":
        try:
            from AppKit import NSApp
            NSApp.activateIgnoringOtherApps_(True)
        except Exception:
            pass
    window.lift()
    window.focus_force()
    window.attributes("-topmost", True)
    window.after(200, lambda: window.attributes("-topmost", False))


if __name__ == "__main__":
    app = JigglyPuffApp()
    app.after(100, lambda: bring_to_front(app))
    app.mainloop()