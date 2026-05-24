#!/usr/bin/env bash
# packaging/appimage/build.sh
# Builds a universal .AppImage (runs on any Linux, no install needed)
#
# Requirements: PyInstaller binary must exist at dist/clipboard-manager
#               Run packaging/pyinstaller/build.sh first!
#
# Output: ClipboardManager-x86_64.AppImage
# Usage : bash packaging/appimage/build.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
APPDIR="$ROOT/packaging/appimage/AppDir"
BINARY="$ROOT/dist/clipboard-manager"
APPIMAGETOOL="$ROOT/packaging/appimage/appimagetool-x86_64.AppImage"

echo "═══════════════════════════════════════════"
echo "  AppImage Builder"
echo "═══════════════════════════════════════════"

# ── Check binary exists ───────────────────────────────────────────────────────
if [ ! -f "$BINARY" ]; then
    echo "❌  Binary not found at dist/clipboard-manager"
    echo "    Run PyInstaller build first:"
    echo "    bash packaging/pyinstaller/build.sh"
    exit 1
fi

# ── Download appimagetool if needed ──────────────────────────────────────────
if [ ! -f "$APPIMAGETOOL" ]; then
    echo "📥  Downloading appimagetool…"
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" \
         -O "$APPIMAGETOOL"
    chmod +x "$APPIMAGETOOL"
    echo "✅  appimagetool downloaded."
fi

# ── Build AppDir structure ────────────────────────────────────────────────────
echo ""
echo "📁  Building AppDir structure…"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# Copy binary
cp "$BINARY" "$APPDIR/usr/bin/clipboard-manager"

# Desktop file
cat > "$APPDIR/usr/share/applications/clipboard-manager.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Clipboard Manager
Exec=clipboard-manager
Icon=clipboard-manager
Comment=Linux clipboard history (Ctrl+Alt+V)
Categories=Utility;
StartupNotify=false
Terminal=false
EOF

# Copy desktop file to AppDir root (required by AppImage spec)
cp "$APPDIR/usr/share/applications/clipboard-manager.desktop" "$APPDIR/"

# Create a simple SVG icon (replace with a real PNG if you have one)
cat > "$APPDIR/usr/share/icons/hicolor/256x256/apps/clipboard-manager.svg" <<'SVGEOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <rect width="256" height="256" rx="48" fill="#1e1e2e"/>
  <rect x="72" y="48" width="112" height="144" rx="12" fill="#313244"/>
  <rect x="96" y="32" width="64" height="28" rx="8" fill="#45475a"/>
  <rect x="88" y="96" width="80" height="8" rx="4" fill="#89b4fa"/>
  <rect x="88" y="116" width="64" height="8" rx="4" fill="#6c7086"/>
  <rect x="88" y="136" width="72" height="8" rx="4" fill="#6c7086"/>
  <rect x="88" y="156" width="56" height="8" rx="4" fill="#6c7086"/>
</svg>
SVGEOF

# Symlink icon to AppDir root
ln -sf "usr/share/icons/hicolor/256x256/apps/clipboard-manager.svg" \
       "$APPDIR/clipboard-manager.svg"

# AppRun entry point
cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE="${SELF%/*}"
export PATH="$HERE/usr/bin:$PATH"
exec "$HERE/usr/bin/clipboard-manager" "$@"
EOF
chmod +x "$APPDIR/AppRun"

echo "✅  AppDir ready."

# ── Package into .AppImage ────────────────────────────────────────────────────
echo ""
echo "📦  Packaging AppImage…"
cd "$ROOT"
ARCH=x86_64 "$APPIMAGETOOL" "$APPDIR" "ClipboardManager-x86_64.AppImage"

echo ""
echo "═══════════════════════════════════════════"
echo "  ✅  AppImage ready!"
echo ""
echo "  File : $ROOT/ClipboardManager-x86_64.AppImage"
echo "  Size : $(du -sh "$ROOT/ClipboardManager-x86_64.AppImage" | cut -f1)"
echo ""
echo "  Share this single file — users just run:"
echo "  chmod +x ClipboardManager-x86_64.AppImage"
echo "  ./ClipboardManager-x86_64.AppImage"
echo "═══════════════════════════════════════════"
