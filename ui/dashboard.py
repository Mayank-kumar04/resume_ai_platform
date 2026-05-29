"""
ResumeAI Platform — Dashboard Page
Central view showing ATS score, category breakdowns, and quick actions.
All values are placeholder until an analysis is run.
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFrame, QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt

from ui.base_page import BasePage
from ui.components import (
    ScoreCard, MetricCard, SectionHeader,
    Divider, Badge, EmptyState
)
from ui.styles import COLORS


# ─── Quick Action Card ────────────────────────────────────────────────────────
class QuickActionCard(QFrame):
    """Small card with icon, title, description and a CTA button."""

    def __init__(self, icon: str, title: str, body: str,
                 btn_label: str, on_click=None, parent=None):
        super().__init__(parent)
        self.setObjectName("QuickCard")
        self.setStyleSheet(f"""
            QFrame#QuickCard {{
                background-color: {COLORS["bg_card"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 14px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 28px; background: transparent;")
        layout.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 700;"
        )
        layout.addWidget(title_lbl)

        body_lbl = QLabel(body)
        body_lbl.setWordWrap(True)
        body_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 12px; line-height: 1.5;"
        )
        layout.addWidget(body_lbl)

        layout.addStretch()

        btn = QPushButton(btn_label)
        btn.setObjectName("secondaryBtn")
        btn.setFixedHeight(34)
        if on_click:
            btn.clicked.connect(on_click)
        layout.addWidget(btn)


# ─── Tip Row ──────────────────────────────────────────────────────────────────
class TipRow(QWidget):
    """Single row in the Tips list with a colored dot, text, and badge."""

    def __init__(self, text: str, category: str, variant: str = "neutral", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(12)

        dot = QLabel("●")
        dot.setFixedWidth(14)
        color_map = {
            "danger":  COLORS["danger"],
            "warning": COLORS["warning"],
            "success": COLORS["success"],
            "info":    COLORS["info"],
        }
        dot.setStyleSheet(
            f"color: {color_map.get(variant, COLORS['text_muted'])}; font-size: 10px;"
        )
        layout.addWidget(dot, alignment=Qt.AlignTop | Qt.AlignLeft)

        text_lbl = QLabel(text)
        text_lbl.setWordWrap(True)
        text_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 13px;")
        layout.addWidget(text_lbl, stretch=1)

        badge = Badge(category, variant)
        layout.addWidget(badge, alignment=Qt.AlignRight | Qt.AlignVCenter)


# ─── Dashboard Page ───────────────────────────────────────────────────────────
class DashboardPage(BasePage):
    PAGE_TITLE = "Dashboard"
    PAGE_SUBTITLE = "Resume health overview and ATS score"

    # Emitted when user wants to navigate to another page (page_index)
    navigate_requested = None  # set externally by MainWindow

    def build_ui(self):
        # ── Page Header ───────────────────────────────────────────────
        header = SectionHeader(
            "Dashboard",
            "Upload a resume and job description to generate your ATS score"
        )
        self.content_layout.addWidget(header)

        # ── Status banner (shown until analysis runs) ─────────────────
        self._build_status_banner()

        # ── Score Overview Row ────────────────────────────────────────
        self.content_layout.addWidget(self._build_score_overview())

        # ── Category Breakdown ────────────────────────────────────────
        cat_header = QLabel("Category Breakdown")
        cat_header.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 16px; font-weight: 700;"
        )
        self.content_layout.addWidget(cat_header)
        self.content_layout.addWidget(self._build_category_grid())

        # ── Getting Started ───────────────────────────────────────────
        self.content_layout.addWidget(Divider())
        gs_header = QLabel("Get Started")
        gs_header.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 16px; font-weight: 700;"
        )
        self.content_layout.addWidget(gs_header)
        self.content_layout.addWidget(self._build_quick_actions())

        self.content_layout.addStretch()

    # ── Status Banner ─────────────────────────────────────────────────────────
    def _build_status_banner(self):
        banner = QFrame()
        banner.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS["accent_light"]};
                border: 1px solid {COLORS["accent"]};
                border-radius: 10px;
            }}
        """)
        row = QHBoxLayout(banner)
        row.setContentsMargins(16, 12, 16, 12)
        row.setSpacing(12)

        icon = QLabel("ℹ️")
        icon.setStyleSheet("font-size: 16px; background: transparent;")
        row.addWidget(icon)

        msg = QLabel(
            "No analysis yet.  Upload your resume and paste a job description to get started."
        )
        msg.setStyleSheet(
            f"color: {COLORS['info']}; font-size: 13px; background: transparent;"
        )
        row.addWidget(msg, stretch=1)

        self.content_layout.addWidget(banner)

    # ── Score Overview ────────────────────────────────────────────────────────
    def _build_score_overview(self) -> QWidget:
        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(16)

        # ATS Score Ring
        self.ats_score_card = ScoreCard(
            "ATS Score",
            score=0,
            description="Run analysis to calculate your score"
        )
        self.ats_score_card.setFixedWidth(210)
        row.addWidget(self.ats_score_card)

        # Right-side metric cards stacked 2×2
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(12)

        self.keyword_card  = MetricCard("Keyword Match",  0, "🔑")
        self.grammar_card  = MetricCard("Grammar Score",  0, "✍️")
        self.format_card   = MetricCard("Formatting",     0, "🗂️")
        self.impact_card   = MetricCard("Impact Writing", 0, "🚀")

        metrics_grid.addWidget(self.keyword_card,  0, 0)
        metrics_grid.addWidget(self.grammar_card,  0, 1)
        metrics_grid.addWidget(self.format_card,   1, 0)
        metrics_grid.addWidget(self.impact_card,   1, 1)

        metrics_widget = QWidget()
        metrics_widget.setLayout(metrics_grid)
        row.addWidget(metrics_widget, stretch=1)

        return container

    # ── Category Grid ─────────────────────────────────────────────────────────
    def _build_category_grid(self) -> QWidget:
        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(12)
        grid.setContentsMargins(0, 0, 0, 0)

        categories = [
            ("Keyword Match",    0, "🔑", "30% weight"),
            ("Formatting",       0, "🗂️", "20% weight"),
            ("Grammar",          0, "✍️", "15% weight"),
            ("Resume Structure", 0, "🏗️", "15% weight"),
            ("Impact Writing",   0, "🚀", "10% weight"),
            ("ATS Compliance",   0, "🤖", "10% weight"),
        ]

        self.category_cards = {}
        for i, (label, score, icon, weight) in enumerate(categories):
            card = self._make_category_card(label, score, icon, weight)
            row, col = divmod(i, 3)
            grid.addWidget(card, row, col)
            self.category_cards[label] = card

        return container

    def _make_category_card(self, label: str, score: int,
                             icon: str, weight: str) -> QFrame:
        card = QFrame()
        card.setObjectName("CategoryCard")
        card.setStyleSheet(f"""
            QFrame#CategoryCard {{
                background-color: {COLORS["bg_card"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 12px;
            }}
            QFrame#CategoryCard:hover {{
                border-color: {COLORS["accent"]};
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Icon + weight row
        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 20px; background: transparent;")
        top.addWidget(icon_lbl)
        top.addStretch()
        weight_lbl = QLabel(weight)
        weight_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 11px;"
        )
        top.addWidget(weight_lbl)
        layout.addLayout(top)

        # Category name
        name_lbl = QLabel(label)
        name_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 600;"
        )
        layout.addWidget(name_lbl)

        # Score
        score_lbl = QLabel("—")
        score_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 24px; font-weight: 700;"
        )
        layout.addWidget(score_lbl)

        # Bar
        bar = QFrame()
        bar.setFixedHeight(4)
        bar.setStyleSheet(
            f"background-color: {COLORS['border']}; border-radius: 2px;"
        )
        layout.addWidget(bar)

        return card

    # ── Quick Actions ─────────────────────────────────────────────────────────
    def _build_quick_actions(self) -> QWidget:
        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(14)

        actions = [
            ("📄", "Upload Resume",
             "Start by uploading your resume PDF. We'll extract text, sections, and links.",
             "Upload Resume"),
            ("💼", "Add Job Description",
             "Paste the job description to match keywords and identify skill gaps.",
             "Add JD"),
            ("📊", "Compare Benchmark",
             "Upload a successful resume to benchmark your formatting and impact writing.",
             "Upload Benchmark"),
        ]

        for icon, title, body, btn in actions:
            card = QuickActionCard(icon, title, body, btn)
            row.addWidget(card, stretch=1)

        return container

    # ── Public: update scores after analysis ─────────────────────────────────
    def update_scores(self, scores: dict):
        """
        Called by the analysis engine after scoring.
        scores = {
            'ats': int,
            'keyword': int,
            'grammar': int,
            'formatting': int,
            'impact': int,
            'structure': int,
            'compliance': int,
        }
        """
        self.ats_score_card.set_score(scores.get("ats", 0))
        self.keyword_card.set_score(scores.get("keyword", 0))
        self.grammar_card.set_score(scores.get("grammar", 0))
        self.format_card.set_score(scores.get("formatting", 0))
        self.impact_card.set_score(scores.get("impact", 0))
