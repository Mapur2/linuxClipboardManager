# clipboard_manager.spec
# Build with: pyinstaller clipboard_manager.spec

import sys
from pathlib import Path

ROOT = Path("../../")   # points to clipboard_manager/

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[],
    hiddenimports=[
        "pynput.keyboard._xorg",
        "pynput.mouse._xorg",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="clipboard-manager",
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,          # compress binary (install upx for smaller size)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,     # no terminal window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
