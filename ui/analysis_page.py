"""
ResumeAI Platform — Analysis Page (Full)
Displays all ATS analysis results: scores, keyword match,
grammar issues, link validation, section quality, template compliance.
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QProgressBar, QScrollArea, QSizePolicy,
    QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor

from ui.base_page import BasePage
from ui.components import (
    SectionHeader, MetricCard, Badge, Divider, EmptyState
)
from ui.styles import COLORS


# ─── Small Collapsible Card ───────────────────────────────────────────────────
class ResultCard(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("ResultCard")
        self.setStyleSheet(f"""
            QFrame#ResultCard {{
                background-color: {COLORS["bg_card"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 12px;
            }}
        """)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 16, 20, 16)
        self.main_layout.setSpacing(12)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 700;"
        )
        self.main_layout.addWidget(title_lbl)

    def add_row(self, text: str, variant: str = "neutral"):
        row = QHBoxLayout()
        row.setSpacing(10)

        dot_colors = {
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "danger":  COLORS["danger"],
            "neutral": COLORS["text_muted"],
        }
        dot = QLabel("●")
        dot.setFixedWidth(12)
        dot.setStyleSheet(f"color: {dot_colors.get(variant, COLORS['text_muted'])}; font-size: 9px;")
        row.addWidget(dot, alignment=Qt.AlignTop)

        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px;")
        row.addWidget(lbl, stretch=1)
        self.main_layout.addLayout(row)

    def add_widget(self, widget: QWidget):
        self.main_layout.addWidget(widget)


# ─── Issue Row ────────────────────────────────────────────────────────────────
class IssueRow(QFrame):
    def __init__(self, title: str, body: str, badge_text: str,
                 badge_variant: str = "warning", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS["bg_card_hover"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 8px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        text_col = QVBoxLayout()
        text_col.setSpacing(3)

        t = QLabel(title)
        t.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; font-weight: 600;")
        b = QLabel(body)
        b.setWordWrap(True)
        b.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        text_col.addWidget(t)
        text_col.addWidget(b)
        layout.addLayout(text_col, stretch=1)

        badge = Badge(badge_text, badge_variant)
        layout.addWidget(badge, alignment=Qt.AlignRight | Qt.AlignVCenter)


# ─── Analysis Page ────────────────────────────────────────────────────────────
class AnalysisPage(BasePage):
    PAGE_TITLE    = "Analysis"
    PAGE_SUBTITLE = "Full ATS analysis results"

    def build_ui(self):
        self.content_layout.addWidget(SectionHeader(
            "Analysis",
            "Detailed ATS scoring, keyword breakdown, grammar, and compliance"
        ))

        # Default: show empty state until analysis runs
        self._empty = EmptyState(
            "📊", "No Analysis Yet",
            "Upload a resume and paste a job description, then click 'Run Analysis'."
        )
        self.content_layout.addWidget(self._empty)

        # Container for results (hidden until analysis done)
        self._results_widget = QWidget()
        self._results_layout = QVBoxLayout(self._results_widget)
        self._results_layout.setContentsMargins(0, 0, 0, 0)
        self._results_layout.setSpacing(20)
        self._results_widget.hide()
        self.content_layout.addWidget(self._results_widget)

        self.content_layout.addStretch()

    # ── Called by MainWindow when analysis finishes ───────────────────────────
    def populate(self, result: dict):
        self._empty.hide()

        # Clear previous results
        while self._results_layout.count():
            item = self._results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        ats   = result.get("ats")
        match = result.get("match")

        if ats:
            self._build_score_overview(ats)
        if match:
            self._build_keyword_section(match)

        grammar_issues = result.get("grammar_issues", [])
        if grammar_issues:
            self._build_grammar_section(grammar_issues)

        link_results = result.get("link_results", [])
        if link_results:
            self._build_link_section(link_results)

        section_feedback = result.get("section_feedback", [])
        if section_feedback:
            self._build_section_quality(section_feedback)

        template_issues = result.get("template_issues", [])
        if template_issues:
            self._build_template_section(template_issues)

        self._results_widget.show()

    # ── Score Overview Row ────────────────────────────────────────────────────
    def _build_score_overview(self, ats):
        card = ResultCard("ATS Score Breakdown")

        row = QHBoxLayout()
        row.setSpacing(12)

        metrics = [
            ("Keyword",    ats.keyword,    "🔑"),
            ("Formatting", ats.formatting, "🗂️"),
            ("Grammar",    ats.grammar,    "✍️"),
            ("Structure",  ats.structure,  "🏗️"),
            ("Impact",     ats.impact,     "🚀"),
            ("Compliance", ats.compliance, "🤖"),
        ]
        for label, score, icon in metrics:
            mc = MetricCard(label, score, icon)
            mc.setMinimumWidth(120)
            row.addWidget(mc, stretch=1)

        container = QWidget()
        container.setLayout(row)
        card.add_widget(container)

        # Reasoning notes
        for cat, reason in ats.reasoning.items():
            card.add_row(f"{cat.title()}: {reason}", "neutral")

        # Strengths
        for s in ats.strengths:
            card.add_row(f"✓ {s}", "success")

        self._results_layout.addWidget(card)

    # ── Keyword Section ───────────────────────────────────────────────────────
    def _build_keyword_section(self, match):
        card = ResultCard(f"Keyword Match — {match.match_pct:.1f}%")

        # Progress bar
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(int(match.match_pct))
        bar.setFixedHeight(10)
        bar.setTextVisible(False)
        color = COLORS["success"] if match.match_pct >= 80 else \
                COLORS["warning"] if match.match_pct >= 50 else COLORS["danger"]
        bar.setStyleSheet(f"""
            QProgressBar {{ background: {COLORS["border"]}; border-radius: 5px; border: none; }}
            QProgressBar::chunk {{ background: {color}; border-radius: 5px; }}
        """)
        card.add_widget(bar)

        # Matched keywords chips
        if match.matched:
            card.add_row("Matched Keywords:", "success")
            chip_row = self._keyword_chips(match.matched[:20], "success")
            card.add_widget(chip_row)

        # Missing keywords
        if match.missing:
            card.add_row(f"Missing Keywords ({len(match.missing)}):", "danger")
            chip_row = self._keyword_chips(
                match.high_priority_gaps[:15] or match.missing[:15], "danger"
            )
            card.add_widget(chip_row)

        self._results_layout.addWidget(card)

    def _keyword_chips(self, keywords: list, variant: str) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignLeft)

        for kw in keywords:
            badge = Badge(kw, variant)
            layout.addWidget(badge)
        layout.addStretch()
        return container

    # ── Grammar Section ───────────────────────────────────────────────────────
    def _build_grammar_section(self, issues: list):
        card = ResultCard(f"Grammar & Writing Issues ({len(issues)})")

        # Show up to 10 issues
        for issue in issues[:10]:
            d = issue.to_dict() if hasattr(issue, "to_dict") else {}
            severity = d.get("severity", "warning")
            variant_map = {"error": "danger", "warning": "warning", "style": "info"}
            row = IssueRow(
                title       = d.get("message", "Issue")[:80],
                body        = d.get("context", "")[:100],
                badge_text  = severity.upper(),
                badge_variant = variant_map.get(severity, "warning"),
            )
            card.add_widget(row)

        if len(issues) > 10:
            card.add_row(f"…and {len(issues) - 10} more issues. See Suggestions page.", "neutral")

        self._results_layout.addWidget(card)

    # ── Link Validation ───────────────────────────────────────────────────────
    def _build_link_section(self, link_results: list):
        card = ResultCard(f"Link Validation ({len(link_results)} URLs)")

        for lr in link_results:
            row = IssueRow(
                title       = lr.url[:70],
                body        = lr.note,
                badge_text  = lr.status.upper(),
                badge_variant = lr.badge_variant,
            )
            card.add_widget(row)

        self._results_layout.addWidget(card)

    # ── Section Quality ───────────────────────────────────────────────────────
    def _build_section_quality(self, feedbacks: list):
        card = ResultCard("Section Quality")

        for fb in feedbacks:
            score = fb.score
            color = COLORS["success"] if score >= 80 else \
                    COLORS["warning"] if score >= 50 else COLORS["danger"]

            row = QHBoxLayout()
            row.setSpacing(12)

            name_lbl = QLabel(fb.section)
            name_lbl.setFixedWidth(120)
            name_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 13px; font-weight: 600;")
            row.addWidget(name_lbl)

            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(score)
            bar.setFixedHeight(8)
            bar.setTextVisible(False)
            bar.setStyleSheet(f"""
                QProgressBar {{ background: {COLORS["border"]}; border-radius: 4px; border: none; }}
                QProgressBar::chunk {{ background: {color}; border-radius: 4px; }}
            """)
            row.addWidget(bar, stretch=1)

            score_lbl = QLabel(f"{score}/100")
            score_lbl.setFixedWidth(55)
            score_lbl.setAlignment(Qt.AlignRight)
            score_lbl.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 700;")
            row.addWidget(score_lbl)

            container = QWidget()
            container.setLayout(row)
            card.add_widget(container)

            for issue in fb.issues:
                card.add_row(f"⚠  {issue}", "warning")
            for tip in fb.tips:
                card.add_row(f"💡 {tip}", "info")

        self._results_layout.addWidget(card)

    # ── Template Compliance ───────────────────────────────────────────────────
    def _build_template_section(self, issues: list):
        if not issues:
            return
        card = ResultCard(f"ATS Template Compliance ({len(issues)} issues)")

        severity_map = {"critical": "danger", "warning": "warning", "info": "info"}
        for issue in issues:
            row = IssueRow(
                title       = issue.issue[:80],
                body        = issue.fix,
                badge_text  = issue.severity.upper(),
                badge_variant = severity_map.get(issue.severity, "warning"),
            )
            card.add_widget(row)

        self._results_layout.addWidget(card)
