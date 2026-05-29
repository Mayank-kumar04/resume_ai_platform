"""
ResumeAI Platform — Main Window (Final)
Fully wired: sidebar navigation, analysis worker, progress dialog,
result propagation to all pages.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QLabel, QPushButton, QFrame,
    QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from ui.styles import STYLESHEET, COLORS
from ui.dashboard      import DashboardPage
from ui.upload_page    import UploadPage
from ui.jd_page        import JDPage
from ui.analysis_page  import AnalysisPage
from ui.benchmark_page import BenchmarkPage
from ui.suggestions_page import SuggestionsPage
from ui.reports_page   import ReportsPage
from ui.settings_page  import SettingsPage
from ui.progress_dialog import ProgressDialog


# ─── Nav Item ─────────────────────────────────────────────────────────────────
class NavItem(QPushButton):
    def __init__(self, icon: str, label: str, page_index: int, parent=None):
        super().__init__(parent)
        self.page_index = page_index
        self.setCheckable(False)
        self.setFixedHeight(44)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        self.icon_lbl = QLabel(icon)
        self.icon_lbl.setFixedWidth(22)
        self.icon_lbl.setStyleSheet("font-size: 16px; background: transparent;")
        layout.addWidget(self.icon_lbl)

        self.text_lbl = QLabel(label)
        layout.addWidget(self.text_lbl, stretch=1)

        self._set_style(False)

    def _set_style(self, active: bool):
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS["accent_light"]};
                    border: none;
                    border-left: 3px solid {COLORS["accent"]};
                    border-radius: 0px;
                }}
            """)
            self.text_lbl.setStyleSheet(
                f"color: {COLORS['text_primary']}; font-size: 13px; font-weight: 600; background: transparent;"
            )
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-left: 3px solid transparent;
                    border-radius: 0px;
                }}
                QPushButton:hover {{ background-color: {COLORS["bg_card"]}; }}
            """)
            self.text_lbl.setStyleSheet(
                f"color: {COLORS['text_secondary']}; font-size: 13px; background: transparent;"
            )

    def set_active(self, active: bool):
        self._set_style(active)


# ─── Sidebar ──────────────────────────────────────────────────────────────────
class Sidebar(QWidget):
    page_changed = pyqtSignal(int)

    NAV_ITEMS = [
        ("🏠", "Dashboard",       0),
        ("📄", "Resume Upload",   1),
        ("💼", "Job Description", 2),
        ("📊", "Analysis",        3),
        ("🔍", "Benchmark",       4),
        ("💡", "Suggestions",     5),
        ("📋", "Reports",         6),
        ("⚙️",  "Settings",       7),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setObjectName("Sidebar")
        self.setStyleSheet(f"""
            QWidget#Sidebar {{
                background-color: {COLORS["bg_surface"]};
                border-right: 1px solid {COLORS["border"]};
            }}
        """)
        self._btns: list[NavItem] = []
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo
        logo_frame = QFrame()
        logo_frame.setFixedHeight(64)
        logo_frame.setStyleSheet(
            f"background:{COLORS['bg_surface']}; border-bottom:1px solid {COLORS['border']};"
        )
        logo_row = QHBoxLayout(logo_frame)
        logo_row.setContentsMargins(16, 0, 16, 0)
        logo_row.setSpacing(10)
        logo_row.addWidget(self._lbl("🎯", "font-size:22px;"))
        logo_row.addWidget(self._lbl("ResumeAI",
            f"color:{COLORS['text_primary']};font-size:16px;font-weight:700;"))
        logo_row.addStretch()
        layout.addWidget(logo_frame)

        # Section label
        nav_lbl = QLabel("NAVIGATION")
        nav_lbl.setContentsMargins(16, 16, 16, 8)
        nav_lbl.setStyleSheet(
            f"color:{COLORS['text_muted']};font-size:10px;font-weight:700;letter-spacing:1.2px;"
        )
        layout.addWidget(nav_lbl)

        for icon, label, idx in self.NAV_ITEMS[:-1]:
            btn = NavItem(icon, label, idx)
            btn.clicked.connect(lambda _, i=idx: self._click(i))
            layout.addWidget(btn)
            self._btns.append(btn)

        layout.addStretch()

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{COLORS['border']};border:none;")
        layout.addWidget(sep)

        icon, label, idx = self.NAV_ITEMS[-1]
        settings_btn = NavItem(icon, label, idx)
        settings_btn.clicked.connect(lambda _, i=idx: self._click(i))
        layout.addWidget(settings_btn)
        self._btns.append(settings_btn)

        ver = QLabel("v1.0.0  ·  All Phases")
        ver.setContentsMargins(16, 6, 16, 10)
        ver.setStyleSheet(f"color:{COLORS['text_muted']};font-size:11px;")
        layout.addWidget(ver)

        self.set_active(0)

    def _lbl(self, text, style="") -> QLabel:
        l = QLabel(text)
        l.setStyleSheet(style + " background:transparent;")
        return l

    def _click(self, index: int):
        self.set_active(index)
        self.page_changed.emit(index)

    def set_active(self, index: int):
        for btn in self._btns:
            btn.set_active(btn.page_index == index)


# ─── Top Bar ──────────────────────────────────────────────────────────────────
class TopBar(QFrame):
    run_analysis_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(56)
        self.setObjectName("TopBar")
        self.setStyleSheet(f"""
            QFrame#TopBar {{
                background:{COLORS["bg_base"]};
                border-bottom:1px solid {COLORS["border"]};
            }}
        """)
        row = QHBoxLayout(self)
        row.setContentsMargins(28, 0, 28, 0)
        row.setSpacing(12)

        self.page_title = QLabel("Dashboard")
        self.page_title.setStyleSheet(
            f"color:{COLORS['text_primary']};font-size:14px;font-weight:600;"
        )
        row.addWidget(self.page_title)

        self.breadcrumb = QLabel("ResumeAI  /  Dashboard")
        self.breadcrumb.setStyleSheet(f"color:{COLORS['text_muted']};font-size:12px;")
        row.addWidget(self.breadcrumb)
        row.addStretch()

        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:12px;")
        row.addWidget(self.status_lbl)

        self.analyze_btn = QPushButton("▶  Run Analysis")
        self.analyze_btn.setFixedSize(148, 34)
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setToolTip("Upload a resume first.")
        self.analyze_btn.clicked.connect(self.run_analysis_clicked)
        row.addWidget(self.analyze_btn)

    def update_page(self, title: str):
        self.page_title.setText(title)
        self.breadcrumb.setText(f"ResumeAI  /  {title}")

    def set_status(self, msg: str):
        self.status_lbl.setText(msg)


# ─── Main Window ─────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):

    PAGE_MAP = [
        (DashboardPage,    "Dashboard"),
        (UploadPage,       "Resume Upload"),
        (JDPage,           "Job Description"),
        (AnalysisPage,     "Analysis"),
        (BenchmarkPage,    "Benchmark"),
        (SuggestionsPage,  "Suggestions"),
        (ReportsPage,      "Reports"),
        (SettingsPage,     "Settings"),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ResumeAI Platform")
        self.resize(1240, 800)
        self.setMinimumSize(960, 640)
        self.setStyleSheet(STYLESHEET)

        self._resume_path    = ""
        self._benchmark_path = ""
        self._last_result    = {}
        self._pages: list[QWidget] = []
        self._worker = None

        self._build_ui()
        self._connect_signals()

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar()
        root.addWidget(self.sidebar)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        self.topbar = TopBar()
        rl.addWidget(self.topbar)

        self.stack = QStackedWidget()
        rl.addWidget(self.stack, stretch=1)

        root.addWidget(right, stretch=1)

        for PageClass, _ in self.PAGE_MAP:
            page = PageClass()
            self._pages.append(page)
            self.stack.addWidget(page)

    # ── Connect Signals ───────────────────────────────────────────────────────
    def _connect_signals(self):
        self.sidebar.page_changed.connect(self._switch_page)
        self.topbar.run_analysis_clicked.connect(self._run_analysis)

        upload_page: UploadPage = self._pages[1]
        upload_page.resume_uploaded.connect(self._on_resume_uploaded)

        jd_page: JDPage = self._pages[2]
        jd_page.jd_submitted.connect(self._on_jd_saved)

        bench_page: BenchmarkPage = self._pages[4]
        bench_page.benchmark_path_selected.connect(self._on_benchmark_selected)

    # ── Slots ─────────────────────────────────────────────────────────────────
    def _switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
        _, title = self.PAGE_MAP[index]
        self.topbar.update_page(title)
        page = self._pages[index]
        if hasattr(page, "on_activate"):
            page.on_activate()

    def _on_resume_uploaded(self, path: str):
        self._resume_path = path
        self.topbar.analyze_btn.setEnabled(True)
        self.topbar.analyze_btn.setToolTip("Click to run full analysis.")
        import os
        self.topbar.set_status(f"📄 {os.path.basename(path)}")

    def _on_jd_saved(self, text: str):
        self._jd_text = text
        self.topbar.set_status(
            self.topbar.status_lbl.text() + "  ·  💼 JD Ready"
        )

    def _on_benchmark_selected(self, path: str):
        self._benchmark_path = path

    # ── Run Analysis ──────────────────────────────────────────────────────────
    def _run_analysis(self):
        if not self._resume_path:
            QMessageBox.warning(self, "No Resume", "Please upload a resume PDF first.")
            return

        from utils.analysis_worker import AnalysisWorker
        jd_text = getattr(self, "_jd_text", "")

        self._worker = AnalysisWorker(
            resume_path    = self._resume_path,
            jd_text        = jd_text,
            benchmark_path = self._benchmark_path,
        )

        self._progress_dialog = ProgressDialog(self)
        self._worker.progress.connect(self._progress_dialog.update_progress)
        self._worker.finished.connect(self._on_analysis_done)
        self._worker.error.connect(self._on_analysis_error)

        self._worker.start()
        self._progress_dialog.exec_()

    def _on_analysis_done(self, result: dict):
        self._progress_dialog.finish()
        self._last_result = result

        ats = result.get("ats")

        # ── Dashboard ─────────────────────────────────────────────────
        dash: DashboardPage = self._pages[0]
        if ats:
            dash.update_scores(ats.to_dict())

        # ── Analysis page ─────────────────────────────────────────────
        analysis_page: AnalysisPage = self._pages[3]
        analysis_page.populate(result)

        # ── Benchmark page ────────────────────────────────────────────
        bench_page: BenchmarkPage = self._pages[4]
        bench_page.populate(result)

        # ── Suggestions page ──────────────────────────────────────────
        sugg_page: SuggestionsPage = self._pages[5]
        sugg_page.populate(result)

        # ── Reports page ──────────────────────────────────────────────
        reports_page: ReportsPage = self._pages[6]
        reports_page.set_result(result)

        # Switch to Analysis page
        self.sidebar.set_active(3)
        self._switch_page(3)

        score = ats.overall if ats else 0
        self.topbar.set_status(f"✅ Analysis complete — ATS Score: {score}/100")

    def _on_analysis_error(self, error_msg: str):
        if hasattr(self, "_progress_dialog"):
            self._progress_dialog.finish()
        QMessageBox.critical(self, "Analysis Error", error_msg[:400])
