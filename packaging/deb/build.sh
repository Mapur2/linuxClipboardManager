#!/usr/bin/env bash
# packaging/deb/build.sh
# Builds a .deb package installable via apt/dpkg on Ubuntu/Debian
#
# Requirements: PyInstaller binary must exist at dist/clipboard-manager
#               Run packaging/pyinstaller/build.sh first!
#
# Output: clipboard-manager_1.0.0_amd64.deb
# Usage : bash packaging/deb/build.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BINARY="$ROOT/dist/clipboard-manager"
VERSION="1.0.0"
PKGNAME="clipboard-manager"
ARCH="amd64"
PKGDIR="$ROOT/packaging/deb/${PKGNAME}_${VERSION}_${ARCH}"

echo "═══════════════════════════════════════════"
echo "  .deb Package Builder"
echo "═══════════════════════════════════════════"

# ── Check binary exists ───────────────────────────────────────────────────────
if [ ! -f "$BINARY" ]; then
    echo "❌  Binary not found. Run PyInstaller build first:"
    echo "    bash packaging/pyinstaller/build.sh"
    exit 1
fi

# ── Build package directory structure ────────────────────────────────────────
echo "📁  Building package structure…"
rm -rf "$PKGDIR"
mkdir -p "$PKGDIR/DEBIAN"
mkdir -p "$PKGDIR/usr/bin"
mkdir -p "$PKGDIR/usr/share/applications"
mkdir -p "$PKGDIR/usr/share/doc/$PKGNAME"
mkdir -p "$PKGDIR/etc/xdg/autostart"

# ── Copy binary ──────────────────────────────────────────────────────────────
cp "$BINARY" "$PKGDIR/usr/bin/clipboard-manager"
chmod 755 "$PKGDIR/usr/bin/clipboard-manager"

# ── Desktop entry ─────────────────────────────────────────────────────────────
cat > "$PKGDIR/usr/share/applications/clipboard-manager.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Clipboard Manager
Exec=/usr/bin/clipboard-manager
Icon=edit-paste
Comment=Linux clipboard history manager (Ctrl+Alt+V)
Categories=Utility;
StartupNotify=false
Terminal=false
EOF

# ── Autostart entry ───────────────────────────────────────────────────────────
cat > "$PKGDIR/etc/xdg/autostart/clipboard-manager.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Clipboard Manager
Exec=/usr/bin/clipboard-manager
Icon=edit-paste
Comment=Linux clipboard history manager (Ctrl+Alt+V)
X-GNOME-Autostart-enabled=true
StartupNotify=false
Terminal=false
EOF

# ── Changelog / copyright ─────────────────────────────────────────────────────
cat > "$PKGDIR/usr/share/doc/$PKGNAME/copyright" <<EOF
Clipboard Manager $VERSION
A Windows+V style clipboard history manager for Linux.
Built with Python + PyQt6.
EOF

# ── DEBIAN/control ────────────────────────────────────────────────────────────
INSTALLED_SIZE=$(du -sk "$PKGDIR" | cut -f1)
cat > "$PKGDIR/DEBIAN/control" <<EOF
Package: $PKGNAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Installed-Size: $INSTALLED_SIZE
Depends: libxcb-cursor0, libxcb1, libxcb-icccm4, libxcb-image0, libxcb-keysyms1, libxcb-randr0, libxcb-render-util0, libxcb-shape0
Recommends: xdotool
Maintainer: Your Name <your@email.com>
Description: Clipboard history manager for Linux
 A Windows+V style floating clipboard history popup.
 Press Ctrl+Alt+V anywhere to open your clipboard history,
 search through it, and paste any previous entry.
 .
 Features: persistent SQLite history, live search,
 keyboard navigation, system tray icon.
EOF

# ── DEBIAN/postinst (runs after install) ──────────────────────────────────────
cat > "$PKGDIR/DEBIAN/postinst" <<'EOF'
#!/bin/bash
echo "✅  Clipboard Manager installed."
echo "   Start it from your app menu or run: clipboard-manager"
echo "   Hotkey: Ctrl+Alt+V"
EOF
chmod 755 "$PKGDIR/DEBIAN/postinst"

# ── Build .deb ────────────────────────────────────────────────────────────────
echo "📦  Building .deb package…"
cd "$ROOT"
dpkg-deb --build --root-owner-group "$PKGDIR"

DEB_FILE="${PKGDIR}.deb"
echo ""
echo "═══════════════════════════════════════════"
echo "  ✅  .deb package ready!"
echo ""
echo "  File    : $DEB_FILE"
echo "  Size    : $(du -sh "$DEB_FILE" | cut -f1)"
echo ""
echo "  Install : sudo dpkg -i $DEB_FILE"
echo "  Remove  : sudo apt remove clipboard-manager"
echo "═══════════════════════════════════════════"
