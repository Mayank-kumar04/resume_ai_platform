"""
ResumeAI Platform — Benchmark Comparison Page
Upload a benchmark PDF, run comparison, display radar chart + dimension cards.
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QFileDialog, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal

from ui.base_page import BasePage
from ui.components import SectionHeader, Badge, Divider, EmptyState
from ui.styles import COLORS


class DeltaCard(QFrame):
    """Shows one benchmark dimension: user score vs benchmark score + delta."""

    def __init__(self, dimension, parent=None):
        super().__init__(parent)
        self.setObjectName("DeltaCard")
        delta = dimension.delta
        border_color = COLORS["success"] if delta >= 0 else COLORS["danger"]
        self.setStyleSheet(f"""
            QFrame#DeltaCard {{
                background-color: {COLORS["bg_card"]};
                border: 1px solid {border_color};
                border-radius: 10px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        # Title + delta badge
        top = QHBoxLayout()
        name = QLabel(dimension.name)
        name.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 13px; font-weight: 700;"
        )
        top.addWidget(name)
        top.addStretch()

        delta_str = f"{delta:+d}"
        variant = "success" if delta >= 0 else "danger"
        badge = Badge(delta_str, variant)
        top.addWidget(badge)
        layout.addLayout(top)

        # Score bar comparison
        scores_row = QHBoxLayout()
        scores_row.setSpacing(20)

        for label, score, color in [
            ("You",       dimension.user_score,  COLORS["accent"]),
            ("Benchmark", dimension.bench_score, COLORS["success"]),
        ]:
            col = QVBoxLayout()
            col.setSpacing(4)

            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
            col.addWidget(lbl)

            score_lbl = QLabel(str(score))
            score_lbl.setStyleSheet(
                f"color: {color}; font-size: 22px; font-weight: 700;"
            )
            col.addWidget(score_lbl)

            bar_container = QFrame()
            bar_container.setFixedHeight(6)
            bar_container.setStyleSheet(
                f"background: {COLORS['border']}; border-radius: 3px;"
            )
            fill = QFrame(bar_container)
            fill.setFixedHeight(6)
            fill_w = max(4, int((score / 100) * 120))
            fill.setFixedWidth(fill_w)
            fill.setStyleSheet(f"background: {color}; border-radius: 3px;")
            col.addWidget(bar_container)

            scores_row.addLayout(col)
        scores_row.addStretch()
        layout.addLayout(scores_row)

        # Insight
        insight_lbl = QLabel(dimension.insight)
        insight_lbl.setWordWrap(True)
        insight_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 11px;"
        )
        layout.addWidget(insight_lbl)


class BenchmarkPage(BasePage):
    PAGE_TITLE    = "Benchmark Comparison"
    PAGE_SUBTITLE = "Compare your resume against a high-quality benchmark"

    benchmark_path_selected = pyqtSignal(str)

    def build_ui(self):
        self.content_layout.addWidget(SectionHeader(
            "Benchmark Comparison",
            "Upload a successful resume PDF to compare structure, impact, and skill depth"
        ))

        # Upload strip
        self.content_layout.addWidget(self._build_upload_strip())
        self.content_layout.addWidget(Divider())

        self._empty = EmptyState(
            "🔍", "No Benchmark Loaded",
            "Upload a benchmark resume PDF above, then run analysis to see the comparison."
        )
        self.content_layout.addWidget(self._empty)

        self._results = QWidget()
        self._rlayout = QVBoxLayout(self._results)
        self._rlayout.setContentsMargins(0, 0, 0, 0)
        self._rlayout.setSpacing(20)
        self._results.hide()
        self.content_layout.addWidget(self._results)
        self.content_layout.addStretch()

    def _build_upload_strip(self) -> QFrame:
        strip = QFrame()
        strip.setStyleSheet(f"""
            QFrame {{
                background: {COLORS["bg_card"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 10px;
            }}
        """)
        row = QHBoxLayout(strip)
        row.setContentsMargins(16, 14, 16, 14)
        row.setSpacing(14)

        icon = QLabel("📄")
        icon.setStyleSheet("font-size: 22px; background: transparent;")
        row.addWidget(icon)

        col = QVBoxLayout()
        col.setSpacing(2)
        title = QLabel("Benchmark Resume PDF")
        title.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 700;"
        )
        sub = QLabel("Upload a resume from someone who got the role you're targeting.")
        sub.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        col.addWidget(title)
        col.addWidget(sub)
        row.addLayout(col, stretch=1)

        self.bench_status = Badge("Not Loaded", "neutral")
        row.addWidget(self.bench_status)

        btn = QPushButton("Browse PDF")
        btn.setObjectName("secondaryBtn")
        btn.setFixedSize(110, 34)
        btn.clicked.connect(self._pick_benchmark)
        row.addWidget(btn)

        return strip

    def _pick_benchmark(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Benchmark Resume PDF", "", "PDF Files (*.pdf)"
        )
        if path:
            self.bench_status.setText("Loaded ✓")
            self.bench_status.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORS["success_bg"]};
                    color: {COLORS["success"]};
                    border-radius: 10px;
                    padding: 3px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }}
            """)
            self.benchmark_path_selected.emit(path)

    def populate(self, result: dict):
        bench = result.get("benchmark")
        if not bench:
            return

        self._empty.hide()

        while self._rlayout.count():
            item = self._rlayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # ── Summary Banner ─────────────────────────────────────────────
        delta = bench.overall_delta
        color = COLORS["success"] if delta >= 0 else COLORS["danger"]
        banner = QFrame()
        banner.setStyleSheet(f"""
            QFrame {{
                background: {COLORS["bg_card"]};
                border: 1px solid {color};
                border-radius: 10px;
            }}
        """)
        brow = QHBoxLayout(banner)
        brow.setContentsMargins(20, 14, 20, 14)
        brow.setSpacing(16)

        icon = QLabel("📊")
        icon.setStyleSheet("font-size: 28px; background: transparent;")
        brow.addWidget(icon)

        summary_lbl = QLabel(bench.summary)
        summary_lbl.setWordWrap(True)
        summary_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 14px;"
        )
        brow.addWidget(summary_lbl, stretch=1)

        delta_lbl = QLabel(f"{delta:+d}")
        delta_lbl.setStyleSheet(
            f"color: {color}; font-size: 28px; font-weight: 800;"
        )
        brow.addWidget(delta_lbl)
        self._rlayout.addWidget(banner)

        # ── Radar Chart ────────────────────────────────────────────────
        try:
            from charts.chart_builder import benchmark_radar
            user_scores  = {d.name: d.user_score  for d in bench.dimensions}
            bench_scores = {d.name: d.bench_score for d in bench.dimensions}
            chart = benchmark_radar(user_scores, bench_scores)
            chart.setFixedHeight(320)
            self._rlayout.addWidget(chart)
        except Exception:
            pass

        # ── Dimension Cards Grid ───────────────────────────────────────
        grid_widget = QWidget()
        grid_layout = QHBoxLayout(grid_widget)
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        for i, dim in enumerate(bench.dimensions):
            card = DeltaCard(dim)
            grid_layout.addWidget(card, stretch=1)
            if (i + 1) % 3 == 0 and i < len(bench.dimensions) - 1:
                self._rlayout.addWidget(grid_widget)
                grid_widget  = QWidget()
                grid_layout  = QHBoxLayout(grid_widget)
                grid_layout.setSpacing(12)
                grid_layout.setContentsMargins(0, 0, 0, 0)

        if grid_layout.count() > 0:
            self._rlayout.addWidget(grid_widget)

        # ── Advantages / Gaps ──────────────────────────────────────────
        if bench.advantages or bench.gaps:
            split = QHBoxLayout()
            split.setSpacing(16)

            if bench.advantages:
                adv_card = self._list_card(
                    "✅  Your Advantages", bench.advantages, COLORS["success"]
                )
                split.addWidget(adv_card, stretch=1)

            if bench.gaps:
                gap_card = self._list_card(
                    "📈  Areas to Improve", bench.gaps, COLORS["warning"]
                )
                split.addWidget(gap_card, stretch=1)

            wrapper = QWidget()
            wrapper.setLayout(split)
            self._rlayout.addWidget(wrapper)

        self._results.show()

    def _list_card(self, title: str, items: list, accent: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS["bg_card"]};
                border: 1px solid {COLORS["border"]};
                border-top: 3px solid {accent};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        t = QLabel(title)
        t.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 700;")
        layout.addWidget(t)

        for item in items:
            l = QLabel(f"• {item}")
            l.setWordWrap(True)
            l.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
            layout.addWidget(l)

        return card
