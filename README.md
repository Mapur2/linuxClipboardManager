# 📋 Clipboard Manager for Linux

A **Windows+V style** clipboard history manager for Linux, built with Python + PyQt6.

---

## ✨ Features

| Feature | Detail |
|---|---|
| **Global hotkey** | `Ctrl + Alt + V` opens the popup from anywhere |
| **Live search** | Filter history as you type |
| **Keyboard nav** | ↑ ↓ to move, Enter to paste, Del to remove, Esc to close |
| **Auto-paste** | If `xdotool` is installed, pastes directly into focused window |
| **Persistent** | SQLite history survives reboots, stores last 100 entries |
| **System tray** | Right-click to clear history or quit |
| **Dark theme** | Clean Catppuccin-inspired dark UI |

---

## 🗂 Project Structure

```
clipboard_manager/
├── main.py              ← Entry point
├── database.py          ← SQLite persistence
├── clipboard_watcher.py ← Monitors clipboard via Qt signal
├── hotkey.py            ← Global hotkey listener (pynput)
├── popup.py             ← PyQt6 floating popup UI
├── tray.py              ← System tray icon
├── requirements.txt     ← Python dependencies
└── install.sh           ← Setup + autostart script
```

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional) Install xdotool for auto-paste

```bash
# Debian / Ubuntu
sudo apt install xdotool

# Fedora
sudo dnf install xdotool

# Arch
sudo pacman -S xdotool
```

### 3. Run

```bash
python3 main.py
```

### 4. Or use the installer (sets up autostart too)

```bash
chmod +x install.sh
./install.sh
```

---

## ⌨️ Controls

| Key / Action | Effect |
|---|---|
| `Ctrl + Alt + V` | Open popup |
| `↑` / `↓` | Navigate items |
| `Enter` | Copy + paste selected item |
| `Click` | Copy selected item |
| `Double-click` | Copy + paste item |
| `Del` | Delete selected item |
| `Esc` | Close popup |
| Tray → Clear | Wipe all history |

---

## ⚙️ Customising the Hotkey

Edit `hotkey.py` and change the `hotkey` parameter in `main.py`:

```python
# main.py
hotkey = HotkeyListener(hotkey="<super>+v")   # Win/Super key
# or
hotkey = HotkeyListener(hotkey="<ctrl>+<shift>+v")
```

Valid key names follow `pynput` syntax: `<ctrl>`, `<alt>`, `<shift>`, `<super>`, plus regular keys.

---

## ⚠️ Notes

- **X11 only** — `pynput` global hotkeys don't work on Wayland out of the box.  
  On Wayland, consider using your DE's custom shortcut to run `python3 main.py --show`.
- Auto-paste requires **`xdotool`** to be installed. Without it, items are copied to clipboard and you paste manually with `Ctrl+V`.
- History is stored at `~/.local/share/clipboard_manager/clipboard.db`.
