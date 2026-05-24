"""
tray.py — System tray icon and context menu.
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QRect


def _make_tray_icon() -> QIcon:
    """Draw a simple clipboard icon as QIcon."""
    size = 32
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)

    painter = QPainter(px)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Rounded background
    painter.setBrush(QColor("#89b4fa"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(QRect(2, 2, size - 4, size - 4), 6, 6)

    # Clipboard symbol
    painter.setPen(QColor("#1e1e2e"))
    font = QFont("Arial", 16, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(QRect(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, "📋")

    painter.end()
    return QIcon(px)


class TrayIcon:
    def __init__(self, app: QApplication, popup, db):
        self.app = app
        self.popup = popup
        self.db = db

        self.tray = QSystemTrayIcon(_make_tray_icon(), app)
        self.tray.setToolTip("Clipboard Manager  |  Ctrl+Alt+V")

        menu = QMenu()

        show_act = menu.addAction("📋  Show History")
        show_act.triggered.connect(popup.show_popup)

        menu.addSeparator()

        clear_act = menu.addAction("🗑  Clear All History")
        clear_act.triggered.connect(self._clear_history)

        menu.addSeparator()

        quit_act = menu.addAction("✕  Quit")
        quit_act.triggered.connect(app.quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_activate)
        self.tray.show()

    def _on_activate(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.popup.show_popup()

    def _clear_history(self):
        self.db.clear_all()
        self.popup.refresh_list()
        self.tray.showMessage(
            "Clipboard Manager",
            "History cleared.",
            QSystemTrayIcon.MessageIcon.Information,
            2000,
        )
