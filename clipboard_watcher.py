"""
clipboard_watcher.py — Monitors the system clipboard for changes.

Uses Qt's own `QClipboard.dataChanged` signal (no polling thread needed).
Only text entries are stored; images are ignored.
"""

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication


class ClipboardWatcher(QObject):
    """Emits `new_entry(text)` whenever new text is copied."""

    new_entry = pyqtSignal(str)

    def __init__(self, db):
        super().__init__()
        self.db = db
        self._last_text = ""

        clipboard = QApplication.clipboard()
        clipboard.dataChanged.connect(self._on_change)

    # ------------------------------------------------------------------ #

    def _on_change(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()

        if text and text != self._last_text:
            self._last_text = text
            self.db.add_entry(text)
            self.new_entry.emit(text)
