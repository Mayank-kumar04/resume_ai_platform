"""
ResumeAI Platform — Analysis Progress Dialog
Modal dialog that shows live progress while AnalysisWorker runs.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QFrame
)
from PyQt5.QtCore import Qt

from ui.styles import COLORS


class ProgressDialog(QDialog):
    """
    Non-closeable modal progress dialog.
    Call update(percent, message) from the worker's progress signal.
    Call finish() when the worker completes.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analyzing Resume…")
        self.setFixedSize(440, 220)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setModal(True)
        self.setStyleSheet(f"""
            QDialog {{
                background: {COLORS["bg_surface"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 14px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        icon = QLabel("🧠")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 36px; background: transparent;")
        layout.addWidget(icon)

        self.title_lbl = QLabel("Running Full Analysis…")
        self.title_lbl.setAlignment(Qt.AlignCenter)
        self.title_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 15px; font-weight: 700;"
        )
        layout.addWidget(self.title_lbl)

        self.status_lbl = QLabel("Starting…")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 13px;"
        )
        layout.addWidget(self.status_lbl)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setFixedHeight(10)
        self.bar.setTextVisible(False)
        self.bar.setStyleSheet(f"""
            QProgressBar {{
                background: {COLORS["border"]};
                border-radius: 5px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS["accent"]},
                    stop:1 #7C3AED
                );
                border-radius: 5px;
            }}
        """)
        layout.addWidget(self.bar)

        self.pct_lbl = QLabel("0%")
        self.pct_lbl.setAlignment(Qt.AlignCenter)
        self.pct_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 12px;"
        )
        layout.addWidget(self.pct_lbl)

    def update_progress(self, percent: int, message: str):
        self.bar.setValue(percent)
        self.pct_lbl.setText(f"{percent}%")
        self.status_lbl.setText(message)

    def finish(self):
        self.accept()
