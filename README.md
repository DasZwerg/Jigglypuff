# 🎵 JigglyPuff

A macOS mouse jiggler with a modern dark mode GUI. Keeps your machine awake, your status green, and your screen from locking — with enough features to actually be kinda useful.

This was migrated from an old deralict Github account.

---

## Features

### Core
| Feature | Description |
|---|---|
| **Keep Screen Alive** | Moves the mouse at a configurable interval to prevent sleep and screensaver activation |
| **App Switching** | Cycles through open windows using Cmd+Tab (randomised 1–5 switches per tick) |
| **Stealth Mode** | Moves the mouse ≤5px from its current position — nearly undetectable to observers |

### Movement Controls
| Control | Options |
|---|---|
| **Interval** | Slider from 5s to 300s — sets how often the mouse moves |
| **Speed** | Slow / Medium / Fast — controls how quickly the mouse travels to its destination |
| **Intensity** | Small / Medium / Wild — controls how far across the screen the mouse travels |

> Stealth Mode overrides Intensity — the intensity selector is automatically disabled when Stealth is on.

### Schedule
- **Active Hours Only** toggle — when enabled, JigglyPuff only runs within a configurable time window
- Set a From/To hour in 24h format (e.g. `09` to `17` for 9am–5pm)
- Outside the window, the engine idles but stays running — it resumes automatically when the window opens again

### Session Stats
Live counters updated every second while running:
- **Jiggles** — total mouse moves in the current session
- **Uptime** — how long the current session has been active
- **Switches** — total app switches performed
- **Last action** — exactly what the engine last did

### Controls
- **▶ START / ⏹ STOP** — toggle the jiggler on/off
- **🚨 PANIC** — immediately stops everything, snaps the mouse to the center of the screen, and plays the exit sound

### Safety
- `pyautogui` failsafe is hardcoded **ON** — slam the mouse to any corner of the screen to abort instantly
- Cannot be disabled from the UI

---

## Requirements

- macOS (Apple Silicon or Intel)
- Python 3.10+ (3.14 recommended)
- Tcl/Tk support compiled into Python (see [Installation](#installation))

---

## Installation

### 1. Install Tcl/Tk

> **Important:** If you're using pyenv, Python must be built with Tcl/Tk support or the GUI will fail to launch. Skip this if you're using the prebuilt `.app` bundle.

```bash
brew install tcl-tk
```

Then rebuild your Python version with Tk support:

```bash
TCLTK_PREFIX="$(brew --prefix tcl-tk)"
PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I${TCLTK_PREFIX}/include' --with-tcltk-libs='-L${TCLTK_PREFIX}/lib -ltcl9.0 -ltcl9tk9.0'" \
pyenv install --force 3.14.4
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run

```bash
python jigglypuff.py
```

---

## macOS Accessibility Permission

`pyautogui` requires **Accessibility** access to move the mouse and send keystrokes.

On first run, macOS will prompt you. If it doesn't, grant it manually:

**System Settings → Privacy & Security → Accessibility → enable your Python or JigglyPuff.app**

Without this permission, the engine will start but mouse/keyboard actions will silently fail.

---

## Building a Standalone .app

JigglyPuff can be packaged into a double-clickable `.app` bundle using PyInstaller. The bundle includes Python, all dependencies, and the audio file — no Python installation required on the target machine.

### 1. Install PyInstaller

```bash
pip install pyinstaller
```

### 2. Build

```bash
pyinstaller --clean jigglypuff.spec
```

The app will be output to `dist/JigglyPuff.app`.

### 3. Run

Double-click `dist/JigglyPuff.app` in Finder, or:

```bash
open dist/JigglyPuff.app
```

---

## Distributing to Other Macs

| Consideration | Detail |
|---|---|
| **Gatekeeper** | The app is unsigned. Recipients must right click → Open → Open to bypass the "unidentified developer" warning on first launch. |
| **Architecture** | The build targets the architecture of the machine it was built on. An Apple Silicon build will **not** run on Intel Macs. Build on the target arch, or use `lipo` to merge two builds into a universal binary. |
| **Accessibility** | Every Mac will prompt for Accessibility permission on first use — this cannot be pregranted. |
| **macOS version** | Requires macOS High Sierra (10.13) or newer. |

To check your build's architecture:

```bash
file dist/JigglyPuff.app/Contents/MacOS/JigglyPuff
```

---

## Project Structure

```
jigglypuff/
├── jigglypuff.py       # Main application (GUI + engine)
├── jigglypuff.spec     # PyInstaller build spec
├── requirements.txt    # Python dependencies
├── setup.py            # py2app config (legacy, use PyInstaller instead)
├── audio/
│   └── yay.mp3         # Exit sound (plays on PANIC)
└── dist/               # Built .app output (gitignored)
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `PyAutoGUI` | Mouse movement, keyboard simulation, screen size detection |
| `customtkinter` | Modern dark-mode GUI framework (built on tkinter) |

---

## License

See [LICENSE](LICENSE).
