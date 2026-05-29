"""
ResumeAI Platform — Base Page
All page widgets inherit from BasePage.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy
from PyQt5.QtCore import Qt
from ui.styles import COLORS


class BasePage(QWidget):
    """
    Abstract base for all content pages.
    Wraps content in a scroll area and provides a standard
    padded content layout.

    Subclasses override build_ui() to populate self.content_layout.
    """

    PAGE_TITLE = "Page"
    PAGE_SUBTITLE = ""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._setup_scroll_wrapper()
        self.build_ui()

    def _setup_scroll_wrapper(self):
        """Wrap page content in a QScrollArea for overflow handling."""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._scroll_container = QWidget()
        self._scroll_container.setStyleSheet("background: transparent;")

        self.content_layout = QVBoxLayout(self._scroll_container)
        self.content_layout.setContentsMargins(32, 28, 32, 32)
        self.content_layout.setSpacing(24)
        self.content_layout.setAlignment(Qt.AlignTop)

        scroll.setWidget(self._scroll_container)
        outer_layout.addWidget(scroll)

    def build_ui(self):
        """Override in subclasses to add widgets to self.content_layout."""
        pass

    def on_activate(self):
        """Called by MainWindow when this page becomes visible. Override to refresh data."""
        pass
