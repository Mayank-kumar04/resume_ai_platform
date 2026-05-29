"""
ResumeAI Platform — Reusable UI Components
ScoreCard, MetricBadge, SectionHeader, EmptyState, etc.
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QPushButton, QProgressBar, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush, QConicalGradient

from ui.styles import COLORS


# ─── Divider ──────────────────────────────────────────────────────────────────
class Divider(QFrame):
    """Thin horizontal separator."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background-color: {COLORS['border']}; border: none;")


# ─── Section Header ───────────────────────────────────────────────────────────
class SectionHeader(QWidget):
    """Page section title with optional subtitle and action button."""

    def __init__(self, title: str, subtitle: str = "", action_label: str = "", parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 20px; font-weight: 700;"
        )
        text_col.addWidget(title_lbl)

        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setStyleSheet(
                f"color: {COLORS['text_secondary']}; font-size: 13px;"
            )
            text_col.addWidget(sub_lbl)

        layout.addLayout(text_col)
        layout.addStretch()

        if action_label:
            self.action_btn = QPushButton(action_label)
            self.action_btn.setFixedHeight(36)
            layout.addWidget(self.action_btn)


# ─── Score Ring Widget ─────────────────────────────────────────────────────────
class ScoreRing(QWidget):
    """
    Circular ring that displays a numeric score.
    Color shifts green → amber → red based on value.
    """

    def __init__(self, score: int = 0, size: int = 140, parent=None):
        super().__init__(parent)
        self._score = score
        self._ring_size = size
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def set_score(self, score: int):
        self._score = max(0, min(100, score))
        self.update()

    def _score_color(self) -> QColor:
        if self._score >= 80:
            return QColor(COLORS["score_high"])
        elif self._score >= 50:
            return QColor(COLORS["score_mid"])
        return QColor(COLORS["score_low"])

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        size = self._ring_size
        margin = 10
        rect_size = size - 2 * margin
        x = margin
        y = margin

        # Track (background ring)
        track_pen = QPen(QColor(COLORS["border"]), 10, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(x, y, rect_size, rect_size, 0, 360 * 16)

        # Progress arc
        if self._score > 0:
            progress_pen = QPen(self._score_color(), 10, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(progress_pen)
            start_angle = 90 * 16           # 12 o'clock
            span_angle = -int((self._score / 100) * 360 * 16)
            painter.drawArc(x, y, rect_size, rect_size, start_angle, span_angle)

        # Score text
        painter.setPen(QPen(QColor(COLORS["text_primary"])))
        score_font = QFont("Segoe UI", int(size * 0.18), QFont.Bold)
        painter.setFont(score_font)
        painter.drawText(
            0, 0, size, size,
            Qt.AlignCenter,
            str(self._score)
        )

        # "/100" label
        label_font = QFont("Segoe UI", int(size * 0.08))
        painter.setFont(label_font)
        painter.setPen(QPen(QColor(COLORS["text_secondary"])))
        painter.drawText(
            0, int(size * 0.55), size, int(size * 0.25),
            Qt.AlignCenter,
            "/ 100"
        )

        painter.end()


# ─── Score Card ───────────────────────────────────────────────────────────────
class ScoreCard(QFrame):
    """
    Large card with ScoreRing, title, and description.
    Used on the dashboard for the ATS score.
    """

    def __init__(self, title: str, score: int = 0, description: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("ScoreCard")
        self.setStyleSheet(f"""
            QFrame#ScoreCard {{
                background-color: {COLORS["bg_card"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 16px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)

        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 12px; "
            f"font-weight: 600; text-transform: uppercase; letter-spacing: 1px;"
        )
        layout.addWidget(title_lbl)

        self.ring = ScoreRing(score, size=140)
        layout.addWidget(self.ring, alignment=Qt.AlignCenter)

        if description:
            desc_lbl = QLabel(description)
            desc_lbl.setAlignment(Qt.AlignCenter)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
            layout.addWidget(desc_lbl)

    def set_score(self, score: int):
        self.ring.set_score(score)


# ─── Metric Card ──────────────────────────────────────────────────────────────
class MetricCard(QFrame):
    """
    Small card showing a category score with a progress bar.
    Used for keyword match %, grammar, formatting, etc.
    """

    def __init__(self, label: str, score: int = 0, icon: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("MetricCard")
        self._score = score
        self.setMinimumWidth(160)
        self.setStyleSheet(f"""
            QFrame#MetricCard {{
                background-color: {COLORS["bg_card"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 12px;
            }}
            QFrame#MetricCard:hover {{
                border-color: {COLORS["accent"]};
                background-color: {COLORS["bg_card_hover"]};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        # Icon + label row
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 18px; background: transparent;")
            top_row.addWidget(icon_lbl)

        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 600;"
        )
        top_row.addWidget(lbl)
        top_row.addStretch()
        layout.addLayout(top_row)

        # Score value
        self.score_lbl = QLabel(f"{score}")
        self.score_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 28px; font-weight: 700;"
        )
        layout.addWidget(self.score_lbl)

        # Progress bar
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(score)
        self.bar.setFixedHeight(6)
        self.bar.setTextVisible(False)
        self._apply_bar_style()
        layout.addWidget(self.bar)

    def _apply_bar_style(self):
        if self._score >= 80:
            color = COLORS["score_high"]
        elif self._score >= 50:
            color = COLORS["score_mid"]
        else:
            color = COLORS["score_low"]

        self.bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS["bg_surface"]};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)

    def set_score(self, score: int):
        self._score = max(0, min(100, score))
        self.score_lbl.setText(str(self._score))
        self.bar.setValue(self._score)
        self._apply_bar_style()


# ─── Info Badge ───────────────────────────────────────────────────────────────
class Badge(QLabel):
    """
    Colored pill badge for tags, status labels, skill chips.
    variant: 'success' | 'warning' | 'danger' | 'info' | 'neutral'
    """

    VARIANTS = {
        "success": (COLORS["success_bg"], COLORS["success"]),
        "warning": (COLORS["warning_bg"], COLORS["warning"]),
        "danger":  (COLORS["danger_bg"],  COLORS["danger"]),
        "info":    ("#0C2340",            COLORS["info"]),
        "neutral": (COLORS["bg_card"],    COLORS["text_secondary"]),
    }

    def __init__(self, text: str, variant: str = "neutral", parent=None):
        super().__init__(text, parent)
        bg, fg = self.VARIANTS.get(variant, self.VARIANTS["neutral"])
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {fg};
                border-radius: 10px;
                padding: 3px 10px;
                font-size: 11px;
                font-weight: 600;
            }}
        """)
        self.setFixedHeight(22)


# ─── Empty State ──────────────────────────────────────────────────────────────
class EmptyState(QWidget):
    """
    Centered placeholder shown when no data is available.
    """

    action_clicked = pyqtSignal()

    def __init__(self, icon: str, title: str, subtitle: str = "",
                 action_label: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 48px; background: transparent;")
        layout.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 16px; font-weight: 600;"
        )
        layout.addWidget(title_lbl)

        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setAlignment(Qt.AlignCenter)
            sub_lbl.setWordWrap(True)
            sub_lbl.setStyleSheet(
                f"color: {COLORS['text_secondary']}; font-size: 13px;"
            )
            sub_lbl.setMaximumWidth(360)
            layout.addWidget(sub_lbl, alignment=Qt.AlignCenter)

        if action_label:
            btn = QPushButton(action_label)
            btn.setFixedSize(180, 40)
            btn.clicked.connect(self.action_clicked)
            layout.addWidget(btn, alignment=Qt.AlignCenter)
