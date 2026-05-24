"""
main.py — Entry point for the Clipboard Manager daemon.

Run:
    python main.py

Global hotkey: Ctrl + Alt + V
"""

import sys
import signal

from PyQt6.QtWidgets import QApplication, QMessageBox

from database import Database
from clipboard_watcher import ClipboardWatcher
from popup import ClipboardPopup
from tray import TrayIcon
from hotkey import HotkeyListener


def _check_tray(app: QApplication) -> bool:
    from PyQt6.QtWidgets import QSystemTrayIcon
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(
            None,
            "Clipboard Manager",
            "No system tray detected.\nPlease run a desktop environment that supports it.",
        )
        return False
    return True


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Clipboard Manager")
    app.setQuitOnLastWindowClosed(False)   # keep running after popup closes

    if not _check_tray(app):
        sys.exit(1)

    # Core components
    db      = Database()
    popup   = ClipboardPopup(db)
    _tray   = TrayIcon(app, popup, db)          # noqa: F841  (keeps reference alive)

    # Clipboard watcher — refreshes popup list on new copy
    watcher = ClipboardWatcher(db)
    watcher.new_entry.connect(popup.refresh_list)

    # Global hotkey (Ctrl+Alt+V) in background thread
    hotkey = HotkeyListener(hotkey="<ctrl>+<alt>+v")
    hotkey.activated.connect(popup.show_popup)
    hotkey.start()

    # Allow Ctrl+C in terminal to quit cleanly
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    print("✅  Clipboard Manager running.  Press Ctrl+Alt+V to open.")
    print("   Right-click the tray icon to quit.")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
