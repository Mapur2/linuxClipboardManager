"""
popup.py — The floating clipboard-history popup (Windows+V style).

Features:
  • Frameless, rounded, dark-themed window
  • Live search bar
  • Keyboard navigation (↑ ↓ Enter Del Esc)
  • Single-click  → copies to clipboard
  • Double-click / Enter → copies AND auto-pastes via xdotool (if available)
  • Del key → deletes selected entry
  • Dismisses on focus loss
"""

import subprocess
import shutil
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QApplication,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QKeyEvent, QFont, QColor, QPainter, QPainterPath


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

_XDOTOOL_AVAILABLE = shutil.which("xdotool") is not None


def _short_ts(iso: str) -> str:
    """Return human-friendly timestamp label."""
    try:
        dt = datetime.fromisoformat(iso)
        now = datetime.now()
        diff = now - dt
        if diff.total_seconds() < 60:
            return "just now"
        if diff.total_seconds() < 3600:
            return f"{int(diff.total_seconds() // 60)}m ago"
        if diff.days == 0:
            return dt.strftime("%H:%M")
        return dt.strftime("%b %d")
    except Exception:
        return ""


def _preview(text: str, max_len: int = 72) -> str:
    """Single-line preview of a clipboard entry."""
    line = text.replace("\n", "↵ ").replace("\r", "").strip()
    return line[:max_len] + ("…" if len(line) > max_len else "")


# ─────────────────────────────────────────────────────────────────────────────
#  Custom list item widget
# ─────────────────────────────────────────────────────────────────────────────

class EntryWidget(QWidget):
    def __init__(self, content: str, timestamp: str):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)

        # Content label
        self.content_label = QLabel(_preview(content))
        self.content_label.setObjectName("entryContent")
        self.content_label.setFont(QFont("Monospace", 11))

        # Timestamp label
        self.ts_label = QLabel(_short_ts(timestamp))
        self.ts_label.setObjectName("entryTs")
        self.ts_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.ts_label.setFixedWidth(56)

        layout.addWidget(self.content_label, stretch=1)
        layout.addWidget(self.ts_label)


# ─────────────────────────────────────────────────────────────────────────────
#  Main popup window
# ─────────────────────────────────────────────────────────────────────────────

class ClipboardPopup(QWidget):

    WINDOW_W = 460
    WINDOW_H = 520

    def __init__(self, db):
        super().__init__()
        self.db = db
        self._entries: list[tuple] = []   # (id, content, timestamp)
        self._setup_ui()
        self._apply_styles()

    # ------------------------------------------------------------------ #
    #  UI construction                                                     #
    # ------------------------------------------------------------------ #

    def _setup_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.WINDOW_W, self.WINDOW_H)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)   # shadow margin
        outer.setSpacing(0)

        # ── Card container ──────────────────────────────────────────────
        self.card = QWidget()
        self.card.setObjectName("card")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(14, 14, 14, 10)
        card_layout.setSpacing(10)

        # Header row
        header_row = QHBoxLayout()
        icon_lbl = QLabel("📋")
        icon_lbl.setObjectName("headerIcon")
        title_lbl = QLabel("Clipboard History")
        title_lbl.setObjectName("headerTitle")
        count_lbl = QLabel()
        count_lbl.setObjectName("headerCount")
        self._count_lbl = count_lbl

        clear_btn = QPushButton("🗑 Clear All")
        clear_btn.setObjectName("clearBtn")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        clear_btn.clicked.connect(self._clear_all)

        header_row.addWidget(icon_lbl)
        header_row.addWidget(title_lbl)
        header_row.addStretch()
        header_row.addWidget(count_lbl)
        header_row.addWidget(clear_btn)
        card_layout.addLayout(header_row)

        # Divider
        div = QWidget()
        div.setObjectName("divider")
        div.setFixedHeight(1)
        card_layout.addWidget(div)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("searchBar")
        self.search_bar.setPlaceholderText("  🔍  Search clipboard history…")
        self.search_bar.textChanged.connect(self.refresh_list)
        self.search_bar.installEventFilter(self)
        card_layout.addWidget(self.search_bar)

        # List
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("listWidget")
        self.list_widget.setSpacing(2)
        self.list_widget.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.list_widget.itemClicked.connect(self._on_click)
        self.list_widget.itemDoubleClicked.connect(self._on_double_click)
        card_layout.addWidget(self.list_widget)

        # Footer hint
        hint = "↵ Paste  •  Click Copy  •  Del Remove  •  Esc Close"
        if not _XDOTOOL_AVAILABLE:
            hint = "Click / ↵ Copy  •  Del Remove  •  Esc Close"
        footer = QLabel(hint)
        footer.setObjectName("footer")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(footer)

        outer.addWidget(self.card)

    def _apply_styles(self):
        self.setStyleSheet("""
            /* ── Card ─────────────────────────────────────────── */
            #card {
                background-color : #1e1e2e;
                border-radius    : 14px;
                border           : 1px solid #313244;
            }

            /* ── Clear All button ─────────────────────────────── */
            #clearBtn {
                background-color : #3d2a2a;
                color            : #f38ba8;
                border           : 1px solid #5a3a3a;
                border-radius    : 6px;
                padding          : 3px 10px;
                font-size        : 11px;
            }
            #clearBtn:hover {
                background-color : #5a2a2a;
                border           : 1px solid #f38ba8;
            }
            #clearBtn:pressed {
                background-color : #f38ba8;
                color            : #1e1e2e;
            }

            /* ── Header ───────────────────────────────────────── */
            #headerIcon  { font-size: 18px; }
            #headerTitle {
                color       : #cdd6f4;
                font-size   : 15px;
                font-weight : 700;
            }
            #headerCount {
                color     : #6c7086;
                font-size : 11px;
            }

            /* ── Divider ──────────────────────────────────────── */
            #divider { background-color: #313244; }

            /* ── Search bar ───────────────────────────────────── */
            #searchBar {
                background-color : #2a2a3d;
                color            : #cdd6f4;
                border           : 1.5px solid #45475a;
                border-radius    : 8px;
                padding          : 8px 12px;
                font-size        : 13px;
            }
            #searchBar:focus {
                border: 1.5px solid #89b4fa;
            }

            /* ── List ─────────────────────────────────────────── */
            QListWidget {
                background-color : transparent;
                border           : none;
                outline          : none;
            }
            QListWidget::item {
                background-color : #2a2a3d;
                border-radius    : 7px;
                color            : #cdd6f4;
            }
            QListWidget::item:selected {
                background-color : #3d5d8a;
            }
            QListWidget::item:hover:!selected {
                background-color : #313244;
            }

            /* ── Entry widget labels ──────────────────────────── */
            #entryContent {
                color     : #cdd6f4;
                font-size : 12px;
            }
            #entryTs {
                color     : #6c7086;
                font-size : 10px;
            }

            /* ── Footer ───────────────────────────────────────── */
            #footer {
                color     : #585b70;
                font-size : 10px;
                padding   : 4px;
            }

            /* ── Scrollbar ────────────────────────────────────── */
            QScrollBar:vertical {
                background : #1e1e2e;
                width      : 6px;
                margin     : 0;
            }
            QScrollBar::handle:vertical {
                background    : #45475a;
                border-radius : 3px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { height: 0; }
        """)

    # ------------------------------------------------------------------ #
    #  Popup show / hide                                                   #
    # ------------------------------------------------------------------ #

    @pyqtSlot()
    def show_popup(self):
        self.search_bar.clear()
        self.refresh_list()
        self._center_on_screen()
        self.show()
        self.raise_()
        self.activateWindow()
        self.search_bar.setFocus()

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.x() + (screen.width()  - self.WINDOW_W) // 2
        y = screen.y() + (screen.height() - self.WINDOW_H) // 2
        self.move(x, y)

    # ------------------------------------------------------------------ #
    #  List management                                                     #
    # ------------------------------------------------------------------ #

    @pyqtSlot()
    @pyqtSlot(str)
    def refresh_list(self, *_):
        search = self.search_bar.text() if hasattr(self, "search_bar") else ""
        self._entries = self.db.get_entries(search)
        total = self.db.count()

        self.list_widget.clear()
        self._count_lbl.setText(f"{total} items")

        for entry_id, content, timestamp in self._entries:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, (entry_id, content))
            item.setToolTip(content[:800])

            widget = EntryWidget(content, timestamp)
            item.setSizeHint(widget.sizeHint())

            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    # ------------------------------------------------------------------ #
    #  Actions                                                             #
    # ------------------------------------------------------------------ #

    def _copy_to_clipboard(self, content: str):
        QApplication.clipboard().setText(content)

    def _paste(self, content: str):
        """Copy to clipboard then simulate Ctrl+V via xdotool (if available)."""
        self._copy_to_clipboard(content)
        self.hide()
        if _XDOTOOL_AVAILABLE:
            # Small delay lets the window hide before xdotool fires
            QTimer.singleShot(
                120,
                lambda: subprocess.run(
                    ["xdotool", "key", "--clearmodifiers", "ctrl+v"],
                    capture_output=True,
                ),
            )

    def _on_click(self, item: QListWidgetItem):
        """Single click → copy only."""
        _, content = item.data(Qt.ItemDataRole.UserRole)
        self._copy_to_clipboard(content)
        self.hide()

    def _on_double_click(self, item: QListWidgetItem):
        """Double click → copy + paste."""
        _, content = item.data(Qt.ItemDataRole.UserRole)
        self._paste(content)

    def _delete_selected(self):
        item = self.list_widget.currentItem()
        if not item:
            return
        entry_id, _ = item.data(Qt.ItemDataRole.UserRole)
        self.db.delete_entry(entry_id)
        self.refresh_list()

    def _clear_all(self):
        self.db.clear_all()
        self.refresh_list()

    # ------------------------------------------------------------------ #
    #  Keyboard handling                                                   #
    # ------------------------------------------------------------------ #

    def eventFilter(self, obj, event):
        """Forward ↑ ↓ Enter Esc from search bar to the list."""
        from PyQt6.QtCore import QEvent
        if obj is self.search_bar and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key == Qt.Key.Key_Down:
                row = self.list_widget.currentRow()
                self.list_widget.setCurrentRow(
                    min(row + 1, self.list_widget.count() - 1)
                )
                return True
            if key == Qt.Key.Key_Up:
                row = self.list_widget.currentRow()
                self.list_widget.setCurrentRow(max(row - 1, 0))
                return True
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                item = self.list_widget.currentItem()
                if item:
                    _, content = item.data(Qt.ItemDataRole.UserRole)
                    self._paste(content)
                return True
            if key == Qt.Key.Key_Escape:
                self.hide()
                return True
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()

        if key == Qt.Key.Key_Escape:
            self.hide()

        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            item = self.list_widget.currentItem()
            if item:
                _, content = item.data(Qt.ItemDataRole.UserRole)
                self._paste(content)

        elif key == Qt.Key.Key_Delete:
            self._delete_selected()

        elif key == Qt.Key.Key_Down:
            row = self.list_widget.currentRow()
            self.list_widget.setCurrentRow(
                min(row + 1, self.list_widget.count() - 1)
            )

        elif key == Qt.Key.Key_Up:
            row = self.list_widget.currentRow()
            self.list_widget.setCurrentRow(max(row - 1, 0))

        else:
            super().keyPressEvent(event)

    # ------------------------------------------------------------------ #
    #  Auto-dismiss on focus loss                                          #
    # ------------------------------------------------------------------ #

    def focusOutEvent(self, event):
        # Only hide if neither child widget has focus
        QTimer.singleShot(150, self._maybe_hide)
        super().focusOutEvent(event)

    def _maybe_hide(self):
        if not self.isActiveWindow():
            self.hide()

    # ------------------------------------------------------------------ #
    #  Rounded-corner painting                                             #
    # ------------------------------------------------------------------ #

    def paintEvent(self, event):
        """Transparent background so the card's border-radius shows."""
        super().paintEvent(event)
