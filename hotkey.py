"""
hotkey.py — Global hotkey listener.

Runs pynput's GlobalHotKeys in a background QThread so it doesn't
block the Qt event loop.

Default hotkey: Ctrl + Alt + V
(Super/Win key combos are DE-dependent on Linux; Ctrl+Alt+V is safer.)
"""

from PyQt6.QtCore import QThread, pyqtSignal
from pynput import keyboard


class HotkeyListener(QThread):
    """Emits `activated` when the global hotkey is pressed."""

    activated = pyqtSignal()

    def __init__(self, hotkey: str = "<ctrl>+<alt>+v"):
        super().__init__()
        self.hotkey = hotkey
        self.daemon = True     # die with the main process

    def run(self):
        def _on_activate():
            self.activated.emit()

        with keyboard.GlobalHotKeys({self.hotkey: _on_activate}) as listener:
            listener.join()
