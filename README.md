# AutoMover — Mouse Jiggler + Scroller + Highlighter

> Keeps your computer looking active so you don't lose your session.

---

## What is AutoMover?

AutoMover is a lightweight desktop utility that simulates natural human activity on your computer when you step away. It moves your mouse in smooth curved paths, scrolls pages in realistic reading patterns, and highlights text — just like a real person browsing a page.

The moment you touch your mouse or keyboard, it stops automatically. The moment you step away again, it picks back up.

---

## Who is it for?

Built for freelancers and remote workers who deal with:

- Forced wait timers on gig platforms like Remotasks, Appen, Toloka, and similar tools
- Session timeouts that log you out mid-task
- Screen savers or lock screens triggering during long processes
- Status indicators on Teams, Slack, or Zoom going idle

---

## Features

- **Mouse Movement** — Smooth, curved, human-like mouse movement using Bézier curves and Gaussian point targeting
- **Page Scrolling** — 4 realistic scroll styles: slow read, fast skim, micro jitter, and reverse check
- **Text Highlighting** — Randomly highlights text in safe screen zones, avoiding buttons and links
- **Idle Detection** — Pauses instantly when you touch your mouse or keyboard
- **Clean Dashboard** — Simple tkinter UI with toggles for each feature, live status, and a log feed
- **Resizable Window** — Drag from any edge or corner to resize the dashboard

---

## Installation

**Requirements:**
- Windows 10 / 11 or macOS
- Python 3.8+

**Install dependencies:**
```bash
pip install pyautogui pynput
```

**Run the app:**
```bash
python auto_mover.py
```

---

## Usage

1. Launch `auto_mover.py`
2. Set your **idle threshold** — how many seconds before AutoMover kicks in (default: 5s)
3. Toggle on/off: **Mouse Movement**, **Page Scrolling**, **Text Highlighting**
4. Click **▶ START**
5. Walk away — AutoMover takes over. Touch your mouse or keyboard to pause it instantly.

---

## Running as a standalone app (no Python required)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="AutoMover" auto_mover.py
```

Your `.exe` (Windows) or `.app` (Mac) will be in the `/dist` folder. Share it with anyone — no Python installation needed.

> **Mac users:** After opening for the first time, go to **System Settings → Privacy & Security → Accessibility** and enable the app.

---

## Notes

- `FAILSAFE` is disabled by default — close the window or click **■ STOP** to stop the app
- Text highlighting stays within safe screen zones and never clicks links or buttons
- The app pauses immediately on any keyboard or mouse input

---

## License

Personal use only. Redistribution or resale requires explicit permission from the author.

---

*Built with Python, pyautogui, pynput and tkinter.*
