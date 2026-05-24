#!/usr/bin/env bash
# install.sh — Sets up the Clipboard Manager on Linux (X11)
# Uses a Python virtual environment (required on Ubuntu 22.04+)
# Usage:  chmod +x install.sh && ./install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
AUTOSTART_DIR="$HOME/.config/autostart"
DESKTOP_FILE="$AUTOSTART_DIR/clipboard-manager.desktop"
LAUNCHER="$SCRIPT_DIR/run.sh"

echo "────────────────────────────────────────────"
echo "  Clipboard Manager — Installer"
echo "────────────────────────────────────────────"

# ── 1. Python check ──────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "❌  python3 not found. Please install Python 3.10+."
    exit 1
fi
echo "✅  Python3 found: $(python3 --version)"

# ── 2. Create virtual environment ────────────────────────────────────────────
echo ""
echo "🐍  Creating virtual environment at $VENV_DIR …"
python3 -m venv "$VENV_DIR"
echo "✅  Virtual environment created."

# ── 3. Install dependencies inside venv ──────────────────────────────────────
echo ""
echo "📦  Installing Python dependencies inside venv…"
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
echo "✅  PyQt6 and pynput installed."

# ── 4. Create launcher script ─────────────────────────────────────────────────
cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
# Auto-generated launcher — uses the venv Python
cd "$SCRIPT_DIR"
"$VENV_DIR/bin/python" "$SCRIPT_DIR/main.py" "\$@"
EOF
chmod +x "$LAUNCHER"
echo "✅  Launcher created: $LAUNCHER"

# ── 5. xdotool (optional, enables auto-paste) ────────────────────────────────
echo ""
if command -v xdotool &>/dev/null; then
    echo "✅  xdotool found — auto-paste on Enter/double-click enabled."
else
    echo "⚠️   xdotool not found. Auto-paste disabled (items will still be copied to clipboard)."
    echo "    Install with:  sudo apt install xdotool"
fi

# ── 6. Autostart .desktop entry ──────────────────────────────────────────────
echo ""
read -rp "🚀  Add to autostart (runs on login)? [Y/n]: " ans
ans="${ans:-Y}"
if [[ "$ans" =~ ^[Yy]$ ]]; then
    mkdir -p "$AUTOSTART_DIR"
    cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Clipboard Manager
Exec=$LAUNCHER
Icon=edit-paste
Comment=Linux clipboard history manager (Ctrl+Alt+V)
X-GNOME-Autostart-enabled=true
StartupNotify=false
Terminal=false
EOF
    echo "✅  Autostart entry created: $DESKTOP_FILE"
else
    echo "ℹ️   Skipped autostart."
fi

# ── 7. Done ───────────────────────────────────────────────────────────────────
echo ""
echo "────────────────────────────────────────────"
echo "  Installation complete!"
echo ""
echo "  ▶  Start now :  $LAUNCHER"
echo "      or run   :  bash $LAUNCHER"
echo ""
echo "  ⌨   Hotkey   :  Ctrl + Alt + V"
echo "  🖱   Or click the tray icon in your panel."
echo "────────────────────────────────────────────"
