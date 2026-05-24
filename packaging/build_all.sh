#!/usr/bin/env bash
# packaging/build_all.sh
# One script to build everything: binary → AppImage + .deb
#
# Usage: bash packaging/build_all.sh [--appimage] [--deb] [--all]
#
# With no flags, builds everything.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

BUILD_APPIMAGE=false
BUILD_DEB=false

# ── Parse args ────────────────────────────────────────────────────────────────
if [ $# -eq 0 ]; then
    BUILD_APPIMAGE=true
    BUILD_DEB=true
fi
for arg in "$@"; do
    case $arg in
        --appimage) BUILD_APPIMAGE=true ;;
        --deb)      BUILD_DEB=true ;;
        --all)      BUILD_APPIMAGE=true; BUILD_DEB=true ;;
    esac
done

echo "╔═══════════════════════════════════════════╗"
echo "║   Clipboard Manager — Full Build          ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# ── Step 1: PyInstaller binary (always required) ──────────────────────────────
echo "[ 1/3 ]  Building binary with PyInstaller…"
bash "$SCRIPT_DIR/pyinstaller/build.sh"
echo ""

# ── Step 2: AppImage ──────────────────────────────────────────────────────────
if $BUILD_APPIMAGE; then
    echo "[ 2/3 ]  Building AppImage…"
    bash "$SCRIPT_DIR/appimage/build.sh"
    echo ""
fi

# ── Step 3: .deb ──────────────────────────────────────────────────────────────
if $BUILD_DEB; then
    echo "[ 3/3 ]  Building .deb package…"
    bash "$SCRIPT_DIR/deb/build.sh"
    echo ""
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo "╔═══════════════════════════════════════════╗"
echo "║   Build Summary                           ║"
echo "╚═══════════════════════════════════════════╝"
echo ""
[ -f "$ROOT/dist/clipboard-manager" ] && \
    echo "  🔵  Binary   : dist/clipboard-manager  ($(du -sh "$ROOT/dist/clipboard-manager" | cut -f1))"
[ -f "$ROOT/ClipboardManager-x86_64.AppImage" ] && \
    echo "  🟢  AppImage : ClipboardManager-x86_64.AppImage  ($(du -sh "$ROOT/ClipboardManager-x86_64.AppImage" | cut -f1))"
DEB=$(ls "$ROOT"/packaging/deb/*.deb 2>/dev/null | head -1)
[ -n "$DEB" ] && \
    echo "  🟠  .deb     : $(basename "$DEB")  ($(du -sh "$DEB" | cut -f1))"
echo ""
echo "  ✅  All builds complete!"
