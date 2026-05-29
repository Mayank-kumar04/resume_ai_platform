"""
ResumeAI Platform — Chart Builder (Phase 4 / integrated)
Builds matplotlib figures embedded in PyQt5 widgets.
All chart methods return a QWidget (FigureCanvas) ready to add to any layout.
"""

from typing import Optional

try:
    import matplotlib
    matplotlib.use("Agg")   # non-interactive backend for embedding
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

# Dark theme palette matching the app
BG       = "#0D1117"
SURFACE  = "#1C2128"
TEXT     = "#E6EDF3"
TEXT_SEC = "#8B949E"
BORDER   = "#30363D"
ACCENT   = "#2563EB"
SUCCESS  = "#22C55E"
WARNING  = "#F59E0B"
DANGER   = "#EF4444"
INFO     = "#38BDF8"

CATEGORY_COLORS = [ACCENT, SUCCESS, WARNING, INFO, "#A78BFA", "#F472B6"]


def _apply_dark_style(fig: "Figure", ax):
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=TEXT_SEC, labelsize=9)
    ax.spines["bottom"].set_color(BORDER)
    ax.spines["left"].set_color(BORDER)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _fallback_widget(msg: str) -> QWidget:
    w = QWidget()
    lbl = QLabel(msg)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px;")
    QVBoxLayout(w).addWidget(lbl)
    return w


# ─── Category Score Bar Chart ─────────────────────────────────────────────────
def category_bar_chart(scores: dict[str, int]) -> QWidget:
    """Horizontal bar chart showing all 6 category scores."""
    if not MATPLOTLIB_AVAILABLE:
        return _fallback_widget("matplotlib not installed")

    labels = list(scores.keys())
    values = list(scores.values())
    colors = [SUCCESS if v >= 80 else WARNING if v >= 50 else DANGER for v in values]

    fig = Figure(figsize=(5, 3), tight_layout=True)
    ax = fig.add_subplot(111)
    _apply_dark_style(fig, ax)

    bars = ax.barh(labels, values, color=colors, height=0.55, zorder=2)
    ax.set_xlim(0, 110)
    ax.set_xlabel("Score", color=TEXT_SEC, fontsize=9)
    ax.xaxis.label.set_color(TEXT_SEC)

    # Value labels on bars
    for bar, val in zip(bars, values):
        ax.text(
            val + 2, bar.get_y() + bar.get_height() / 2,
            str(val), va="center", ha="left", color=TEXT, fontsize=9, fontweight="bold"
        )

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, color=TEXT, fontsize=9)
    ax.grid(axis="x", color=BORDER, linestyle="--", linewidth=0.5, zorder=1)

    canvas = FigureCanvas(fig)
    canvas.setStyleSheet(f"background-color: {SURFACE};")
    return canvas


# ─── Keyword Match Donut ──────────────────────────────────────────────────────
def keyword_donut(match_pct: float) -> QWidget:
    """Donut chart showing keyword match percentage."""
    if not MATPLOTLIB_AVAILABLE:
        return _fallback_widget("matplotlib not installed")

    matched  = max(0.0, min(100.0, match_pct))
    missing  = 100.0 - matched
    color    = SUCCESS if matched >= 80 else WARNING if matched >= 50 else DANGER

    fig = Figure(figsize=(3, 3), tight_layout=True)
    ax  = fig.add_subplot(111)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    wedges, _ = ax.pie(
        [matched, missing],
        colors=[color, BORDER],
        startangle=90,
        wedgeprops={"width": 0.45, "edgecolor": SURFACE, "linewidth": 2},
        counterclock=False,
    )

    ax.text(0, 0, f"{matched:.0f}%", ha="center", va="center",
            color=TEXT, fontsize=16, fontweight="bold")
    ax.text(0, -0.3, "Keyword\nMatch", ha="center", va="center",
            color=TEXT_SEC, fontsize=8)

    canvas = FigureCanvas(fig)
    canvas.setStyleSheet(f"background-color: {SURFACE};")
    return canvas


# ─── Benchmark Comparison Radar ───────────────────────────────────────────────
def benchmark_radar(user_scores: dict[str, int], bench_scores: dict[str, int]) -> QWidget:
    """Filled radar (spider) chart comparing user vs benchmark."""
    if not MATPLOTLIB_AVAILABLE:
        return _fallback_widget("matplotlib not installed")

    import numpy as np

    labels  = list(user_scores.keys())
    n       = len(labels)
    user_v  = list(user_scores.values())
    bench_v = list(bench_scores.values())

    # Close the polygon
    angles  = [i / n * 2 * np.pi for i in range(n)] + [0]
    user_v  += user_v[:1]
    bench_v += bench_v[:1]

    fig = Figure(figsize=(4, 4), tight_layout=True)
    ax  = fig.add_subplot(111, polar=True)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    ax.plot(angles, user_v,  color=ACCENT,  linewidth=2, label="Your Resume")
    ax.fill(angles, user_v,  color=ACCENT,  alpha=0.25)
    ax.plot(angles, bench_v, color=SUCCESS, linewidth=2, linestyle="--", label="Benchmark")
    ax.fill(angles, bench_v, color=SUCCESS, alpha=0.1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color=TEXT, fontsize=8)
    ax.set_yticklabels([])
    ax.set_ylim(0, 100)
    ax.spines["polar"].set_color(BORDER)
    ax.grid(color=BORDER, linewidth=0.5)

    ax.legend(loc="lower right", facecolor=SURFACE, edgecolor=BORDER,
              labelcolor=TEXT, fontsize=8)

    canvas = FigureCanvas(fig)
    canvas.setStyleSheet(f"background-color: {SURFACE};")
    return canvas


# ─── Section Quality Bar ──────────────────────────────────────────────────────
def section_quality_chart(section_scores: dict[str, int]) -> QWidget:
    """Vertical bar chart for section-wise quality scores."""
    if not MATPLOTLIB_AVAILABLE:
        return _fallback_widget("matplotlib not installed")

    labels = list(section_scores.keys())
    values = list(section_scores.values())
    colors = [SUCCESS if v >= 80 else WARNING if v >= 50 else DANGER for v in values]

    fig = Figure(figsize=(5, 2.8), tight_layout=True)
    ax  = fig.add_subplot(111)
    _apply_dark_style(fig, ax)

    bars = ax.bar(labels, values, color=colors, width=0.5, zorder=2)
    ax.set_ylim(0, 120)
    ax.set_ylabel("Score", color=TEXT_SEC, fontsize=9)

    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2, val + 3,
            str(val), ha="center", va="bottom", color=TEXT, fontsize=9, fontweight="bold"
        )

    ax.set_xticklabels(labels, color=TEXT, fontsize=8, rotation=15, ha="right")
    ax.grid(axis="y", color=BORDER, linestyle="--", linewidth=0.5, zorder=1)

    canvas = FigureCanvas(fig)
    canvas.setStyleSheet(f"background-color: {SURFACE};")
    return canvas
