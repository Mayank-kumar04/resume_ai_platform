"""
ResumeAI Platform — Job Description Page
Paste JD text, extract skills/keywords, view role requirements.
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QPlainTextEdit, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal

from ui.base_page import BasePage
from ui.components import SectionHeader, Badge, Divider
from ui.styles import COLORS


class JDPage(BasePage):
    PAGE_TITLE    = "Job Description"
    PAGE_SUBTITLE = "Paste the target job description"

    jd_submitted = pyqtSignal(str)   # emits the raw JD text

    def build_ui(self):
        self.content_layout.addWidget(SectionHeader(
            "Job Description",
            "Paste the full job description — we extract keywords, skills, and requirements"
        ))

        # ── Input Card ────────────────────────────────────────────────
        input_card = QFrame()
        input_card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS["bg_card"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 14px;
            }}
        """)
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(20, 18, 20, 18)
        input_layout.setSpacing(12)

        paste_lbl = QLabel("Paste Job Description Text")
        paste_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 700;"
        )
        input_layout.addWidget(paste_lbl)

        self.jd_input = QPlainTextEdit()
        self.jd_input.setPlaceholderText(
            "Paste the full job description here…\n\n"
            "Include role requirements, responsibilities, and preferred qualifications."
        )
        self.jd_input.setMinimumHeight(220)
        self.jd_input.setStyleSheet(f"""
            QPlainTextEdit {{
                background: {COLORS["bg_base"]};
                color: {COLORS["text_primary"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
                line-height: 1.5;
            }}
            QPlainTextEdit:focus {{
                border-color: {COLORS["border_focus"]};
            }}
        """)
        input_layout.addWidget(self.jd_input)

        # Char count + submit row
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)

        self.char_count_lbl = QLabel("0 characters")
        self.char_count_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 12px;"
        )
        self.jd_input.textChanged.connect(self._update_char_count)
        bottom_row.addWidget(self.char_count_lbl)
        bottom_row.addStretch()

        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("secondaryBtn")
        clear_btn.setFixedSize(80, 34)
        clear_btn.clicked.connect(self.jd_input.clear)
        bottom_row.addWidget(clear_btn)

        self.save_btn = QPushButton("Save JD")
        self.save_btn.setFixedSize(100, 34)
        self.save_btn.clicked.connect(self._submit)
        bottom_row.addWidget(self.save_btn)

        input_layout.addLayout(bottom_row)
        self.content_layout.addWidget(input_card)

        # ── Analysis Results ──────────────────────────────────────────
        self._results = QWidget()
        self._rlayout = QVBoxLayout(self._results)
        self._rlayout.setContentsMargins(0, 0, 0, 0)
        self._rlayout.setSpacing(16)
        self._results.hide()
        self.content_layout.addWidget(self._results)
        self.content_layout.addStretch()

    def _update_char_count(self):
        count = len(self.jd_input.toPlainText())
        self.char_count_lbl.setText(f"{count:,} characters")

    def _submit(self):
        text = self.jd_input.toPlainText().strip()
        if text:
            self.jd_submitted.emit(text)
            self._preview_jd(text)

    def _preview_jd(self, text: str):
        """Show a quick keyword preview after saving."""
        from analysis.jd_analyzer import JDAnalyzer
        jd = JDAnalyzer().analyze(text)

        while self._rlayout.count():
            item = self._rlayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._rlayout.addWidget(Divider())

        # Role summary card
        summary_card = QFrame()
        summary_card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS["bg_card"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 12px;
            }}
        """)
        sl = QVBoxLayout(summary_card)
        sl.setContentsMargins(18, 16, 18, 16)
        sl.setSpacing(10)

        title_lbl = QLabel(f"Role: {jd.title or 'Detected'}")
        title_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 15px; font-weight: 700;"
        )
        sl.addWidget(title_lbl)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)
        for label, value in [
            ("Seniority", jd.seniority.title()),
            ("Experience", f"{jd.experience_years}+ yrs" if jd.experience_years else "Not specified"),
            ("Education",  jd.education_req or "Not specified"),
            ("Remote",     "Yes" if jd.is_remote else "No"),
        ]:
            chip_frame = QFrame()
            chip_frame.setStyleSheet(f"""
                QFrame {{
                    background: {COLORS["bg_surface"]};
                    border: 1px solid {COLORS["border"]};
                    border-radius: 8px;
                }}
            """)
            chip_l = QVBoxLayout(chip_frame)
            chip_l.setContentsMargins(10, 6, 10, 6)
            chip_l.setSpacing(2)
            l1 = QLabel(label)
            l1.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; font-weight: 600;")
            l2 = QLabel(value)
            l2.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; font-weight: 700;")
            chip_l.addWidget(l1)
            chip_l.addWidget(l2)
            meta_row.addWidget(chip_frame)
        meta_row.addStretch()
        sl.addLayout(meta_row)

        # Required skills chips
        if jd.required_skills:
            req_lbl = QLabel("Required Skills")
            req_lbl.setStyleSheet(
                f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 600;"
            )
            sl.addWidget(req_lbl)

            chip_row = QHBoxLayout()
            chip_row.setSpacing(6)
            chip_row.setAlignment(Qt.AlignLeft)
            for skill in jd.required_skills[:16]:
                badge = Badge(skill, "info")
                chip_row.addWidget(badge)
            chip_row.addStretch()
            chip_widget = QWidget()
            chip_widget.setLayout(chip_row)
            sl.addWidget(chip_widget)

        # Preferred skills
        if jd.preferred_skills:
            pref_lbl = QLabel("Preferred Skills")
            pref_lbl.setStyleSheet(
                f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 600;"
            )
            sl.addWidget(pref_lbl)

            chip_row2 = QHBoxLayout()
            chip_row2.setSpacing(6)
            chip_row2.setAlignment(Qt.AlignLeft)
            for skill in jd.preferred_skills[:12]:
                badge = Badge(skill, "neutral")
                chip_row2.addWidget(badge)
            chip_row2.addStretch()
            chip_widget2 = QWidget()
            chip_widget2.setLayout(chip_row2)
            sl.addWidget(chip_widget2)

        self._rlayout.addWidget(summary_card)
        self._results.show()

    def get_jd_text(self) -> str:
        return self.jd_input.toPlainText().strip()
