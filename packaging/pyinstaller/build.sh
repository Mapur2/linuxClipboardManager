#!/usr/bin/env bash
# packaging/pyinstaller/build.sh
# Builds a single self-contained binary using PyInstaller
#
# Output: dist/clipboard-manager  (single executable, ~60-80 MB)
# Usage : cd clipboard_manager && bash packaging/pyinstaller/build.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV="$ROOT/.venv"

echo "═══════════════════════════════════════════"
echo "  PyInstaller — Single Binary Build"
echo "═══════════════════════════════════════════"

# ── Install PyInstaller into venv ────────────────────────────────────────────
echo "📦  Installing PyInstaller…"
"$VENV/bin/pip" install pyinstaller --quiet
echo "✅  PyInstaller ready."

# ── Build ────────────────────────────────────────────────────────────────────
echo ""
echo "🔨  Building binary…"
cd "$ROOT"
"$VENV/bin/pyinstaller" \
    --onefile \
    --noconsole \
    --name clipboard-manager \
    --hidden-import "pynput.keyboard._xorg" \
    --hidden-import "pynput.mouse._xorg" \
    --hidden-import "PyQt6.QtCore" \
    --hidden-import "PyQt6.QtGui" \
    --hidden-import "PyQt6.QtWidgets" \
    --exclude-module tkinter \
    --exclude-module matplotlib \
    --exclude-module numpy \
    main.py

echo ""
echo "═══════════════════════════════════════════"
echo "  ✅  Build complete!"
echo ""
echo "  Binary : $ROOT/dist/clipboard-manager"
echo "  Size   : $(du -sh "$ROOT/dist/clipboard-manager" | cut -f1)"
echo ""
echo "  Run it : ./dist/clipboard-manager"
echo "═══════════════════════════════════════════"
