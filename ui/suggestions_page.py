"""
ResumeAI Platform — Suggestions Page
Shows action verb improvements, impact quantification tips,
and skill gap learning path in a clean card layout.
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton
)
from PyQt5.QtCore import Qt

from ui.base_page import BasePage
from ui.components import SectionHeader, Badge, Divider, EmptyState
from ui.styles import COLORS


class SuggestionCard(QFrame):
    """Single suggestion with original text, recommendation, and category badge."""

    def __init__(self, original: str, suggestion: str,
                 category: str, variant: str = "warning", parent=None):
        super().__init__(parent)
        self.setObjectName("SuggCard")
        self.setStyleSheet(f"""
            QFrame#SuggCard {{
                background-color: {COLORS["bg_card"]};
                border: 1px solid {COLORS["border"]};
                border-left: 3px solid {COLORS[
                    "warning" if variant == "warning" else
                    "success" if variant == "success" else
                    "info"
                ]};
                border-radius: 10px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Header row
        top = QHBoxLayout()
        top.setSpacing(8)
        cat_badge = Badge(category, variant)
        top.addWidget(cat_badge)
        top.addStretch()
        layout.addLayout(top)

        # Original
        orig_row = QHBoxLayout()
        orig_row.setSpacing(8)
        orig_icon = QLabel("✖")
        orig_icon.setFixedWidth(16)
        orig_icon.setStyleSheet(f"color: {COLORS['danger']}; font-size: 11px;")
        orig_row.addWidget(orig_icon)
        orig_lbl = QLabel(original[:120])
        orig_lbl.setWordWrap(True)
        orig_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 12px; font-style: italic;"
        )
        orig_row.addWidget(orig_lbl, stretch=1)
        layout.addLayout(orig_row)

        # Suggestion
        sugg_row = QHBoxLayout()
        sugg_row.setSpacing(8)
        sugg_icon = QLabel("✔")
        sugg_icon.setFixedWidth(16)
        sugg_icon.setStyleSheet(f"color: {COLORS['success']}; font-size: 11px;")
        sugg_row.addWidget(sugg_icon)
        sugg_lbl = QLabel(suggestion[:160])
        sugg_lbl.setWordWrap(True)
        sugg_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px;")
        sugg_row.addWidget(sugg_lbl, stretch=1)
        layout.addLayout(sugg_row)


class SkillChip(QLabel):
    def __init__(self, skill: str, priority: str = "high", parent=None):
        super().__init__(skill, parent)
        colors = {
            "high":   (COLORS["danger_bg"],   COLORS["danger"]),
            "medium": (COLORS["warning_bg"],  COLORS["warning"]),
            "low":    (COLORS["success_bg"],  COLORS["success"]),
        }
        bg, fg = colors.get(priority, colors["low"])
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {fg};
                border-radius: 10px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: 600;
            }}
        """)
        self.setFixedHeight(26)


class FlowLayout(QWidget):
    """Wrapping chip grid."""
    def __init__(self, chips: list[QWidget], parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignLeft)
        for chip in chips:
            layout.addWidget(chip)
        layout.addStretch()


class SuggestionsPage(BasePage):
    PAGE_TITLE    = "Suggestions"
    PAGE_SUBTITLE = "Actionable improvements for your resume"

    def build_ui(self):
        self.content_layout.addWidget(SectionHeader(
            "Suggestions",
            "Action verb improvements, impact quantification, and skill gap recommendations"
        ))

        self._empty = EmptyState(
            "💡", "No Suggestions Yet",
            "Run an analysis first — suggestions will appear here."
        )
        self.content_layout.addWidget(self._empty)

        self._results = QWidget()
        self._rlayout = QVBoxLayout(self._results)
        self._rlayout.setContentsMargins(0, 0, 0, 0)
        self._rlayout.setSpacing(24)
        self._results.hide()
        self.content_layout.addWidget(self._results)
        self.content_layout.addStretch()

    def populate(self, result: dict):
        self._empty.hide()

        while self._rlayout.count():
            item = self._rlayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        verb_suggestions   = result.get("verb_suggestions", [])
        impact_suggestions = result.get("impact_suggestions", [])
        skill_gap          = result.get("skill_gap")
        ats                = result.get("ats")

        # ── ATS Improvements Summary ──────────────────────────────────
        if ats and ats.improvements:
            self._rlayout.addWidget(self._build_improvements(ats.improvements))

        # ── Action Verb Improvements ──────────────────────────────────
        if verb_suggestions:
            self._rlayout.addWidget(self._build_verb_section(verb_suggestions))

        # ── Impact Quantification ─────────────────────────────────────
        if impact_suggestions:
            self._rlayout.addWidget(self._build_impact_section(impact_suggestions))

        # ── Skill Gap ─────────────────────────────────────────────────
        if skill_gap:
            self._rlayout.addWidget(self._build_skill_gap(skill_gap))

        self._results.show()

    def _build_improvements(self, improvements: list) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("📋  Overall Recommendations")
        header.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 16px; font-weight: 700;"
        )
        layout.addWidget(header)

        for tip in improvements:
            row = QHBoxLayout()
            row.setSpacing(10)
            dot = QLabel("→")
            dot.setFixedWidth(16)
            dot.setStyleSheet(f"color: {COLORS['accent']}; font-size: 13px;")
            row.addWidget(dot)
            lbl = QLabel(tip)
            lbl.setWordWrap(True)
            lbl.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 13px;")
            row.addWidget(lbl, stretch=1)

            w = QWidget()
            w.setLayout(row)
            layout.addWidget(w)

        return container

    def _build_verb_section(self, suggestions: list) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel(f"✍️  Action Verb Improvements ({len(suggestions)})")
        header.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 16px; font-weight: 700;"
        )
        layout.addWidget(header)

        for s in suggestions[:12]:
            alts = ", ".join(s.alternatives) if s.alternatives else "Use a strong action verb"
            card = SuggestionCard(
                original   = f"Starts with '{s.original}': {s.line}",
                suggestion = f"Try: {alts}",
                category   = s.context.title(),
                variant    = "warning",
            )
            layout.addWidget(card)

        return container

    def _build_impact_section(self, suggestions: list) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel(f"🚀  Impact Quantification ({len(suggestions)})")
        header.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 16px; font-weight: 700;"
        )
        layout.addWidget(header)

        for s in suggestions[:12]:
            card = SuggestionCard(
                original   = s.original,
                suggestion = s.suggestion,
                category   = s.category.title(),
                variant    = "info",
            )
            layout.addWidget(card)

        return container

    def _build_skill_gap(self, gap) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("🎯  Skill Gap & Learning Path")
        header.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 16px; font-weight: 700;"
        )
        layout.addWidget(header)

        if gap.high_priority:
            lbl = QLabel("🔴  High Priority (Required by JD)")
            lbl.setStyleSheet(f"color: {COLORS['danger']}; font-size: 13px; font-weight: 600;")
            layout.addWidget(lbl)
            chips = [SkillChip(i["skill"], "high") for i in gap.high_priority[:10]]
            layout.addWidget(FlowLayout(chips))

        if gap.medium_priority:
            lbl = QLabel("🟡  Medium Priority (Preferred by JD)")
            lbl.setStyleSheet(f"color: {COLORS['warning']}; font-size: 13px; font-weight: 600;")
            layout.addWidget(lbl)
            chips = [SkillChip(i["skill"], "medium") for i in gap.medium_priority[:10]]
            layout.addWidget(FlowLayout(chips))

        if gap.low_priority:
            lbl = QLabel("🟢  Industry Standards to Consider")
            lbl.setStyleSheet(f"color: {COLORS['success']}; font-size: 13px; font-weight: 600;")
            layout.addWidget(lbl)
            chips = [SkillChip(i["skill"], "low") for i in gap.low_priority[:8]]
            layout.addWidget(FlowLayout(chips))

        if gap.learning_path:
            layout.addWidget(Divider())
            path_lbl = QLabel("📚  Suggested Learning Order")
            path_lbl.setStyleSheet(
                f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 700;"
            )
            layout.addWidget(path_lbl)

            for step in gap.learning_path:
                lbl = QLabel(step)
                lbl.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 13px; padding: 2px 0;")
                layout.addWidget(lbl)

        return container
