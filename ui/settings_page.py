"""
ResumeAI Platform — Settings Page
Application preferences: grammar engine toggle, export path, DB info.
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QLineEdit, QCheckBox, QFileDialog
)
from PyQt5.QtCore import Qt

from ui.base_page import BasePage
from ui.components import SectionHeader, Divider
from ui.styles import COLORS
from database import DatabaseManager


class SettingRow(QFrame):
    """A single settings row with label, description, and control widget."""

    def __init__(self, title: str, description: str, control: QWidget, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS["bg_card"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 10px;
            }}
        """)
        row = QHBoxLayout(self)
        row.setContentsMargins(18, 14, 18, 14)
        row.setSpacing(16)

        col = QVBoxLayout()
        col.setSpacing(3)
        t = QLabel(title)
        t.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 13px; font-weight: 700;")
        d = QLabel(description)
        d.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        d.setWordWrap(True)
        col.addWidget(t)
        col.addWidget(d)
        row.addLayout(col, stretch=1)
        row.addWidget(control)


class SettingsPage(BasePage):
    PAGE_TITLE = "Settings"

    def build_ui(self):
        self.content_layout.addWidget(SectionHeader(
            "Settings",
            "Configure analysis preferences, export options, and application behaviour"
        ))

        db = DatabaseManager.instance()

        # ── Analysis Settings ─────────────────────────────────────────
        self._section("Analysis")

        lt_toggle = QCheckBox()
        lt_toggle.setChecked(db.get_setting("use_language_tool", "1") == "1")
        lt_toggle.setStyleSheet(f"""
            QCheckBox::indicator {{ width:38px; height:22px; border-radius:11px;
                background:{COLORS["border"]}; }}
            QCheckBox::indicator:checked {{ background:{COLORS["accent"]}; }}
        """)
        lt_toggle.stateChanged.connect(
            lambda v: db.set_setting("use_language_tool", "1" if v else "0")
        )
        self.content_layout.addWidget(SettingRow(
            "LanguageTool Grammar Engine",
            "Use LanguageTool for grammar checking (requires Java). "
            "Disable to use the built-in regex checker.",
            lt_toggle
        ))

        link_toggle = QCheckBox()
        link_toggle.setChecked(db.get_setting("validate_links", "1") == "1")
        link_toggle.setStyleSheet(lt_toggle.styleSheet())
        link_toggle.stateChanged.connect(
            lambda v: db.set_setting("validate_links", "1" if v else "0")
        )
        self.content_layout.addWidget(SettingRow(
            "Validate Resume Links",
            "Check GitHub, LinkedIn, and portfolio URLs for accessibility during analysis.",
            link_toggle
        ))

        # ── Export Settings ───────────────────────────────────────────
        self.content_layout.addWidget(Divider())
        self._section("Export")

        export_path_input = QLineEdit()
        export_path_input.setFixedWidth(220)
        export_path_input.setPlaceholderText("reports/")
        export_path_input.setText(db.get_setting("export_path", "reports/"))
        export_path_input.textChanged.connect(
            lambda t: db.set_setting("export_path", t)
        )
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("secondaryBtn")
        browse_btn.setFixedSize(80, 32)

        path_widget = QWidget()
        path_row = QHBoxLayout(path_widget)
        path_row.setContentsMargins(0, 0, 0, 0)
        path_row.setSpacing(8)
        path_row.addWidget(export_path_input)
        path_row.addWidget(browse_btn)

        def _browse():
            d = QFileDialog.getExistingDirectory(self, "Select Export Folder")
            if d:
                export_path_input.setText(d)
        browse_btn.clicked.connect(_browse)

        self.content_layout.addWidget(SettingRow(
            "Default Export Path",
            "Where HTML and TXT reports are saved by default.",
            path_widget
        ))

        # ── Database Info ─────────────────────────────────────────────
        self.content_layout.addWidget(Divider())
        self._section("Database")

        import os
        from database import DB_PATH
        db_size = os.path.getsize(DB_PATH) / 1024 if os.path.exists(DB_PATH) else 0
        resumes = len(db.list_resumes())

        db_info = QLabel(f"{DB_PATH}\n{db_size:.1f} KB  ·  {resumes} resumes stored")
        db_info.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 12px; font-family: monospace;"
        )

        clear_btn = QPushButton("Clear Database")
        clear_btn.setObjectName("dangerBtn")
        clear_btn.setFixedSize(130, 34)
        clear_btn.clicked.connect(self._clear_db)

        self.content_layout.addWidget(SettingRow(
            "Database Location",
            "SQLite database storing all resume scans, JDs, and reports.",
            clear_btn
        ))

        # ── About ─────────────────────────────────────────────────────
        self.content_layout.addWidget(Divider())
        about = QLabel(
            "ResumeAI Platform  v1.0.0\n"
            "Built with PyQt5, pdfplumber, spaCy, scikit-learn, matplotlib\n"
            "Phase 1–11 complete"
        )
        about.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px; line-height: 1.8;")
        self.content_layout.addWidget(about)
        self.content_layout.addStretch()

    def _section(self, title: str):
        lbl = QLabel(title.upper())
        lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 11px; "
            f"font-weight: 700; letter-spacing: 1px;"
        )
        self.content_layout.addWidget(lbl)

    def _clear_db(self):
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Clear Database",
            "This will delete all stored resumes and reports. Are you sure?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            db = DatabaseManager.instance()
            db._conn.executescript("""
                DELETE FROM analysis_reports;
                DELETE FROM resumes;
                DELETE FROM job_descriptions;
                DELETE FROM benchmark_comparisons;
            """)
            db._conn.commit()
            QMessageBox.information(self, "Done", "Database cleared.")
