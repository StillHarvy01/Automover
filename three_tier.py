import tkinter as tk
from tkinter import ttk
import threading
import pyautogui
import random
import time
import math
from pynput import mouse, keyboard

# ── Shared state ───────────────────────────────────────────────────────────────
running         = False
last_input_time = time.time()
worker_thread   = None

pyautogui.FAILSAFE = False
pyautogui.PAUSE    = 0
screen_w, screen_h = pyautogui.size()


# ── Input listeners (idle detection) ──────────────────────────────────────────
def on_activity(*args, **kwargs):
    global last_input_time
    last_input_time = time.time()

mouse_listener    = mouse.Listener(on_move=on_activity, on_click=on_activity, on_scroll=on_activity)
keyboard_listener = keyboard.Listener(on_press=on_activity)
mouse_listener.start()
keyboard_listener.start()


# ── Movement helpers ───────────────────────────────────────────────────────────
def gaussian_point():
    zone   = random.choices(["center", "upper_third", "anywhere"], weights=[50, 20, 30])[0]
    margin = 80
    if zone == "center":
        x = int(random.gauss(screen_w * 0.5, screen_w * 0.18))
        y = int(random.gauss(screen_h * 0.5, screen_h * 0.18))
    elif zone == "upper_third":
        x = int(random.gauss(screen_w * 0.5, screen_w * 0.20))
        y = int(random.gauss(screen_h * 0.3, screen_h * 0.12))
    else:
        x = random.randint(margin, screen_w - margin)
        y = random.randint(margin, screen_h - margin)
    return max(margin, min(screen_w - margin, x)), max(margin, min(screen_h - margin, y))


def human_duration(distance):
    base = 0.3 + (distance / max(screen_w, screen_h)) * 1.0
    return round(base * random.uniform(0.6, 1.1), 2)


def escape_if_stuck():
    """
    If cursor hasn't moved after landing (e.g. stuck on an image),
    nudge it to a safe nearby position to break free.
    """
    before = pyautogui.position()
    time.sleep(0.15)
    after  = pyautogui.position()
    if before == after:
        margin  = 80
        nudge_x = max(margin, min(screen_w - margin, before.x + random.randint(-60, 60)))
        nudge_y = max(margin, min(screen_h - margin, before.y + random.randint(-60, 60)))
        pyautogui.moveTo(nudge_x, nudge_y, duration=random.uniform(0.1, 0.25))


def bezier_move(x2, y2):
    x1, y1 = pyautogui.position()
    dist    = math.hypot(x2 - x1, y2 - y1)
    if dist < 5:
        return
    dur    = human_duration(dist)
    steps  = max(15, int(dist / 10))
    margin = 80
    cx1 = max(margin, min(screen_w - margin, x1 + random.randint(-200, 200)))
    cy1 = max(margin, min(screen_h - margin, y1 + random.randint(-200, 200)))
    cx2 = max(margin, min(screen_w - margin, x2 + random.randint(-200, 200)))
    cy2 = max(margin, min(screen_h - margin, y2 + random.randint(-200, 200)))
    for i in range(steps + 1):
        if not running:
            return
        t      = i / steps
        bx     = (1-t)**3*x1 + 3*(1-t)**2*t*cx1 + 3*(1-t)*t**2*cx2 + t**3*x2
        by     = (1-t)**3*y1 + 3*(1-t)**2*t*cy1 + 3*(1-t)*t**2*cy2 + t**3*y2
        safe_x = max(margin, min(screen_w - margin, int(bx)))
        safe_y = max(margin, min(screen_h - margin, int(by)))
        pyautogui.moveTo(safe_x, safe_y)
        time.sleep(dur / steps)

    # After arriving, check if stuck on an image and escape if so
    escape_if_stuck()


def micro_wiggle():
    cx, cy = pyautogui.position()
    margin = 80
    wx = max(margin, min(screen_w - margin, cx + random.randint(-14, 14)))
    wy = max(margin, min(screen_h - margin, cy + random.randint(-14, 14)))
    pyautogui.moveTo(wx, wy, duration=random.uniform(0.1, 0.25))


def random_scroll():
    margin = 80
    read_x = max(margin, min(screen_w - margin, int(random.gauss(screen_w * 0.5, screen_w * 0.15))))
    read_y = max(margin, min(screen_h - margin, int(random.gauss(screen_h * 0.5, screen_h * 0.20))))
    pyautogui.moveTo(read_x, read_y, duration=random.uniform(0.2, 0.5))
    time.sleep(random.uniform(0.1, 0.3))

    style = random.choices(
        ["slow_read", "fast_skim", "micro_jitter", "reverse_check"],
        weights=[40, 25, 20, 15]
    )[0]

    if style == "slow_read":
        for _ in range(random.randint(4, 8)):
            if not running: return
            pyautogui.scroll(-random.randint(5, 10))
            time.sleep(random.uniform(0.2, 0.6))

    elif style == "fast_skim":
        pyautogui.scroll(-random.randint(25, 50))
        time.sleep(random.uniform(0.3, 0.8))
        if random.random() < 0.3:
            pyautogui.scroll(random.randint(8, 18))

    elif style == "micro_jitter":
        for _ in range(random.randint(4, 8)):
            if not running: return
            pyautogui.scroll(random.choice([-4, -4, -4, -3, 2]))
            time.sleep(random.uniform(0.1, 0.25))

    elif style == "reverse_check":
        pyautogui.scroll(random.randint(15, 30))
        time.sleep(random.uniform(0.4, 1.0))
        pyautogui.scroll(-random.randint(10, 25))


def random_highlight():
    """
    Simulate highlighting text by clicking and dragging.
    - Stays in the safe middle zone of the screen (avoids nav bars,
      buttons, links typically found at top/bottom edges)
    - Never clicks — only mouseDown + drag + mouseUp (no click events)
    - Deselects by moving to safe blank area, not clicking a link
    """
    # Safe text zone — avoids top 20% and bottom 15% of screen
    # where nav bars, footers, and buttons typically live
    safe_top    = int(screen_h * 0.20)
    safe_bottom = int(screen_h * 0.85)
    safe_left   = int(screen_w * 0.10)
    safe_right  = int(screen_w * 0.90)

    style = random.choices(
        ["word", "sentence", "paragraph"],
        weights=[35, 45, 20]
    )[0]

    # Start point inside safe text zone
    start_x = random.randint(safe_left,  safe_right - 300)
    start_y = random.randint(safe_top,   safe_bottom)

    # Drag length varies by style — horizontal only, no vertical drag
    # to avoid accidentally spanning across clickable elements
    if style == "word":
        drag_len = random.randint(40, 120)
    elif style == "sentence":
        drag_len = random.randint(120, 320)
    else:
        drag_len = random.randint(300, 550)

    end_x = min(safe_right, start_x + drag_len)
    end_y = start_y  # strictly horizontal — no vertical drift

    # Move to start without clicking
    pyautogui.moveTo(start_x, start_y, duration=random.uniform(0.2, 0.5))
    time.sleep(random.uniform(0.1, 0.25))

    # Drag to highlight — no click, just press and drag
    pyautogui.mouseDown(button="left")
    pyautogui.moveTo(end_x, end_y, duration=random.uniform(0.3, 0.7))
    pyautogui.mouseUp(button="left")

    # Pause — like reading the selected text
    time.sleep(random.uniform(0.5, 2.0))

    # Deselect by pressing Escape — safest way, no click on anything
    pyautogui.press("escape")
    time.sleep(random.uniform(0.1, 0.3))


# ── Worker thread ──────────────────────────────────────────────────────────────
def worker(idle_var, mouse_var, scroll_var, highlight_var, status_label, activity_label):
    global running
    while running:
        idle = time.time() - last_input_time

        if idle >= idle_var.get():
            activity_label.config(text="● Active", fg="#00e676")

            action = random.choices(
                ["move", "scroll", "both", "highlight", "nothing"],
                weights=[18, 30, 35, 12, 5]
            )[0]

            if mouse_var.get() and action in ("move", "both"):
                status_label.config(text="Moving mouse...")
                tx, ty = gaussian_point()
                bezier_move(tx, ty)
                if random.random() < 0.35:
                    time.sleep(random.uniform(0.1, 0.4))
                    micro_wiggle()

            if scroll_var.get() and action in ("scroll", "both"):
                status_label.config(text="Scrolling...")
                time.sleep(random.uniform(0.2, 0.6))
                random_scroll()

            if highlight_var.get() and action == "highlight":
                status_label.config(text="Highlighting text...")
                random_highlight()

            if action == "nothing":
                status_label.config(text="Idle pause...")

            snooze = random.uniform(2, 8)
            if random.random() < 0.15:
                snooze += random.uniform(3, 7)
            time.sleep(snooze)

        else:
            activity_label.config(text="○ Waiting for idle", fg="#aaaaaa")
            status_label.config(text="User active — paused")
            time.sleep(0.2)

    status_label.config(text="Stopped")
    activity_label.config(text="○ Inactive", fg="#aaaaaa")


# ── GUI ────────────────────────────────────────────────────────────────────────
def build_gui():
    global running, worker_thread

    root = tk.Tk()
    root.title("Auto Mover")
    root.geometry("400x560")
    root.minsize(340, 480)
    root.resizable(True, True)
    root.configure(bg="#1a1a2e")

    BG      = "#1a1a2e"
    CARD    = "#16213e"
    ACCENT  = "#00e676"
    TEXT    = "#e0e0e0"
    SUBTEXT = "#888888"
    DANGER  = "#ff5252"
    FONT    = ("Consolas", 10)
    TITLE_F = ("Consolas", 16, "bold")
    SMALL_F = ("Consolas", 9)

    header = tk.Frame(root, bg=BG)
    header.pack(fill="x", padx=24, pady=(24, 8))
    tk.Label(header, text="AUTO MOVER", font=TITLE_F, bg=BG, fg=ACCENT).pack(anchor="w")
    tk.Label(header, text="Mouse & scroll simulator", font=SMALL_F, bg=BG, fg=SUBTEXT).pack(anchor="w")

    ttk.Separator(root, orient="horizontal").pack(fill="x", padx=24, pady=4)

    card = tk.Frame(root, bg=CARD, bd=0, relief="flat")
    card.pack(fill="x", padx=24, pady=8)
    card.pack_propagate(False)
    card.config(height=72)

    activity_label = tk.Label(card, text="○ Inactive", font=("Consolas", 11, "bold"),
                               bg=CARD, fg=SUBTEXT)
    activity_label.pack(anchor="w", padx=16, pady=(14, 0))

    status_label = tk.Label(card, text="Press Start to begin", font=SMALL_F,
                             bg=CARD, fg=SUBTEXT)
    status_label.pack(anchor="w", padx=16)

    settings = tk.Frame(root, bg=BG)
    settings.pack(fill="x", padx=24, pady=(12, 0))

    tk.Label(settings, text="SETTINGS", font=("Consolas", 9, "bold"),
             bg=BG, fg=SUBTEXT).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

    tk.Label(settings, text="Idle threshold (sec)", font=FONT, bg=BG, fg=TEXT).grid(
        row=1, column=0, sticky="w", pady=4)
    idle_var  = tk.IntVar(value=5)
    idle_spin = tk.Spinbox(settings, from_=1, to=60, textvariable=idle_var, width=6,
                           font=FONT, bg=CARD, fg=ACCENT, insertbackground=ACCENT,
                           buttonbackground=CARD, relief="flat")
    idle_spin.grid(row=1, column=1, sticky="e", pady=4)

    mouse_var     = tk.BooleanVar(value=True)
    scroll_var    = tk.BooleanVar(value=True)
    highlight_var = tk.BooleanVar(value=True)

    def styled_check(parent, text, var, row):
        tk.Checkbutton(parent, text=text, variable=var, font=FONT,
                       bg=BG, fg=TEXT, selectcolor=CARD,
                       activebackground=BG, activeforeground=ACCENT,
                       highlightthickness=0, bd=0, cursor="hand2").grid(
            row=row, column=0, columnspan=2, sticky="w", pady=4)

    styled_check(settings, "  Enable mouse movement",   mouse_var,     2)
    styled_check(settings, "  Enable page scrolling",    scroll_var,    3)
    styled_check(settings, "  Enable text highlighting", highlight_var, 4)
    settings.columnconfigure(0, weight=1)

    ttk.Separator(root, orient="horizontal").pack(fill="x", padx=24, pady=12)

    tk.Label(root, text="LOG", font=("Consolas", 9, "bold"), bg=BG, fg=SUBTEXT).pack(
        anchor="w", padx=24)

    log_frame = tk.Frame(root, bg=CARD)
    log_frame.pack(fill="both", expand=True, padx=24, pady=(4, 0))

    log_box = tk.Text(log_frame, height=5, font=("Consolas", 8), bg=CARD, fg="#666666",
                      relief="flat", state="disabled", wrap="word",
                      insertbackground=ACCENT, bd=0)
    log_box.pack(fill="both", expand=True, padx=8, pady=8)

    def log(msg):
        log_box.config(state="normal")
        log_box.insert("end", f"  {msg}\n")
        log_box.see("end")
        log_box.config(state="disabled")

    btn_frame = tk.Frame(root, bg=BG)
    btn_frame.pack(fill="x", padx=24, pady=16)

    start_btn = tk.Button(btn_frame, text="▶  START", font=("Consolas", 11, "bold"),
                          bg=ACCENT, fg="#000000", activebackground="#69f0ae",
                          activeforeground="#000000", relief="flat", bd=0,
                          cursor="hand2", height=2)
    start_btn.pack(fill="x")

    def toggle():
        global running, worker_thread
        if not running:
            running = True
            start_btn.config(text="■  STOP", bg=DANGER, activebackground="#ff867c")
            log(f"Started — idle threshold: {idle_var.get()}s")
            log(f"Mouse: {'ON' if mouse_var.get() else 'OFF'}  |  "
                f"Scroll: {'ON' if scroll_var.get() else 'OFF'}  |  "
                f"Highlight: {'ON' if highlight_var.get() else 'OFF'}")
            worker_thread = threading.Thread(
                target=worker,
                args=(idle_var, mouse_var, scroll_var, highlight_var,
                      status_label, activity_label),
                daemon=True
            )
            worker_thread.start()
        else:
            running = False
            start_btn.config(text="▶  START", bg=ACCENT, activebackground="#69f0ae")
            log("Stopped.")

    start_btn.config(command=toggle)

    def on_close():
        global running
        running = False
        mouse_listener.stop()
        keyboard_listener.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    log("Ready. Configure settings and press Start.")
    root.mainloop()


if __name__ == "__main__":
    build_gui()
