"""
ResumeAI Platform — Stub Pages
These are clean placeholders for phases 5–11.
Each page is fully wired into the sidebar but shows an EmptyState
until its corresponding phase is implemented.
"""

from PyQt5.QtWidgets import QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

from ui.base_page import BasePage
from ui.components import SectionHeader, EmptyState
from ui.styles import COLORS


# ─── Job Description Page ─────────────────────────────────────────────────────
class JDPage(BasePage):
    PAGE_TITLE    = "Job Description"
    PAGE_SUBTITLE = "Paste the target job description"

    def build_ui(self):
        self.content_layout.addWidget(SectionHeader(
            "Job Description",
            "Paste the job description to extract keywords, skills, and match against your resume"
        ))
        self.content_layout.addWidget(EmptyState(
            "💼",
            "No Job Description Yet",
            "Coming in Phase 6 — paste a JD to extract required skills and match them against your resume.",
        ))
        self.content_layout.addStretch()


# ─── Analysis Page ────────────────────────────────────────────────────────────
class AnalysisPage(BasePage):
    PAGE_TITLE    = "Analysis"
    PAGE_SUBTITLE = "Full ATS analysis results"

    def build_ui(self):
        self.content_layout.addWidget(SectionHeader(
            "Analysis",
            "Detailed ATS scoring, keyword heatmap, and section-by-section feedback"
        ))
        self.content_layout.addWidget(EmptyState(
            "📊",
            "No Analysis Run Yet",
            "Coming in Phases 5 – 8 — upload a resume and job description, then run the full analysis engine.",
        ))
        self.content_layout.addStretch()


# ─── Benchmark Page ───────────────────────────────────────────────────────────
class BenchmarkPage(BasePage):
    PAGE_TITLE    = "Benchmark Comparison"
    PAGE_SUBTITLE = "Compare your resume against a high-quality benchmark"

    def build_ui(self):
        self.content_layout.addWidget(SectionHeader(
            "Benchmark Comparison",
            "Upload a successful resume to compare project quality, action verbs, and impact metrics"
        ))
        self.content_layout.addWidget(EmptyState(
            "🔍",
            "No Benchmark Loaded",
            "Coming in Phase 10 — upload a benchmark resume PDF to see structural and quality comparisons.",
        ))
        self.content_layout.addStretch()


# ─── Suggestions Page ─────────────────────────────────────────────────────────
class SuggestionsPage(BasePage):
    PAGE_TITLE    = "Suggestions"
    PAGE_SUBTITLE = "Actionable improvements for your resume"

    def build_ui(self):
        self.content_layout.addWidget(SectionHeader(
            "Suggestions",
            "Grammar fixes, stronger action verbs, quantified impact, and missing skills"
        ))
        self.content_layout.addWidget(EmptyState(
            "💡",
            "No Suggestions Yet",
            "Coming in Phases 7 – 8 — run an analysis to receive grammar corrections, "
            "verb improvements, and quantification tips.",
        ))
        self.content_layout.addStretch()


# ─── Reports Page ─────────────────────────────────────────────────────────────
class ReportsPage(BasePage):
    PAGE_TITLE    = "Reports"
    PAGE_SUBTITLE = "Export and download analysis reports"

    def build_ui(self):
        self.content_layout.addWidget(SectionHeader(
            "Reports",
            "Export your analysis as PDF or HTML for offline review"
        ))
        self.content_layout.addWidget(EmptyState(
            "📋",
            "No Reports Available",
            "Coming in Phase 11 — after running an analysis, export a full PDF or HTML report.",
        ))
        self.content_layout.addStretch()


# ─── Settings Page ────────────────────────────────────────────────────────────
class SettingsPage(BasePage):
    PAGE_TITLE    = "Settings"
    PAGE_SUBTITLE = "Application preferences"

    def build_ui(self):
        self.content_layout.addWidget(SectionHeader(
            "Settings",
            "Configure analysis preferences, export paths, and UI options"
        ))
        self.content_layout.addWidget(EmptyState(
            "⚙️",
            "Settings Coming Soon",
            "Phase 1 is complete. Settings will expand in later phases as features are added.",
        ))
        self.content_layout.addStretch()
