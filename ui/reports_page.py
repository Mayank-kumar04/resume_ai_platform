"""
ResumeAI Platform — Reports Page (Phase 11)
Displays past analysis reports from DB and provides HTML/TXT export.
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt

from ui.base_page import BasePage
from ui.components import SectionHeader, Badge, Divider, EmptyState
from ui.styles import COLORS


class ReportsPage(BasePage):
    PAGE_TITLE    = "Reports"
    PAGE_SUBTITLE = "Export and review past analysis reports"

    def __init__(self, parent=None):
        self._last_result = None
        super().__init__(parent)

    def build_ui(self):
        self.content_layout.addWidget(SectionHeader(
            "Reports",
            "Export your analysis as HTML or plain text, and review past sessions"
        ))

        # ── Export Card ───────────────────────────────────────────────
        self._export_card = self._build_export_card()
        self._export_card.setEnabled(False)
        self.content_layout.addWidget(self._export_card)

        self.content_layout.addWidget(Divider())

        # ── History Table ─────────────────────────────────────────────
        history_header = QLabel("Analysis History")
        history_header.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 16px; font-weight: 700;"
        )
        self.content_layout.addWidget(history_header)

        self._table = self._build_history_table()
        self.content_layout.addWidget(self._table)

        self.content_layout.addStretch()

    def _build_export_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("ExportCard")
        card.setStyleSheet(f"""
            QFrame#ExportCard {{
                background: {COLORS["bg_card"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 14px;
            }}
            QFrame#ExportCard:disabled {{
                opacity: 0.4;
            }}
        """)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(20)

        # Info
        col = QVBoxLayout()
        col.setSpacing(4)
        title = QLabel("Export Analysis Report")
        title.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 15px; font-weight: 700;"
        )
        sub = QLabel("Download a shareable report of your latest ATS analysis.")
        sub.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        col.addWidget(title)
        col.addWidget(sub)
        layout.addLayout(col, stretch=1)

        # Buttons
        self.html_btn = QPushButton("⬇  Export HTML")
        self.html_btn.setFixedSize(140, 38)
        self.html_btn.clicked.connect(self._export_html)
        layout.addWidget(self.html_btn)

        self.txt_btn = QPushButton("⬇  Export Text")
        self.txt_btn.setObjectName("secondaryBtn")
        self.txt_btn.setFixedSize(140, 38)
        self.txt_btn.clicked.connect(self._export_text)
        layout.addWidget(self.txt_btn)

        return card

    def _build_history_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Resume", "Date", "ATS Score", "Keyword", "Grammar", "Formatting"
        ])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, 6):
            table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)

        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setMinimumHeight(200)
        table.setStyleSheet(f"""
            QTableWidget {{
                background: {COLORS["bg_card"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 10px;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 10px 12px;
                border-bottom: 1px solid {COLORS["border"]};
            }}
            QTableWidget::item:selected {{
                background: {COLORS["accent_light"]};
                color: {COLORS["text_primary"]};
            }}
            QHeaderView::section {{
                background: {COLORS["bg_surface"]};
                color: {COLORS["text_secondary"]};
                border: none;
                border-bottom: 1px solid {COLORS["border"]};
                padding: 10px 12px;
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
        """)

        self._load_history(table)
        return table

    def _load_history(self, table: QTableWidget):
        """Load past reports from SQLite."""
        try:
            from database import DatabaseManager
            import json

            db = DatabaseManager.instance()
            resumes = db.list_resumes()
            table.setRowCount(0)

            for resume_row in resumes:
                report = db.get_latest_report(resume_row["id"])
                if not report:
                    continue

                row_idx = table.rowCount()
                table.insertRow(row_idx)

                def cell(text: str, align=Qt.AlignLeft) -> QTableWidgetItem:
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(align | Qt.AlignVCenter)
                    item.setForeground(Qt.white)
                    return item

                def score_item(score: int) -> QTableWidgetItem:
                    item = QTableWidgetItem(str(score))
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    color_map = {True: COLORS["success"], False: COLORS["warning"]}
                    col = COLORS["success"] if score >= 80 else \
                          COLORS["warning"] if score >= 50 else COLORS["danger"]
                    from PyQt5.QtGui import QColor
                    item.setForeground(QColor(col))
                    return item

                table.setItem(row_idx, 0, cell(resume_row["filename"]))
                table.setItem(row_idx, 1, cell(resume_row["upload_date"][:16]))
                table.setItem(row_idx, 2, score_item(report["ats_score"]))
                table.setItem(row_idx, 3, score_item(report["keyword_score"]))
                table.setItem(row_idx, 4, score_item(report["grammar_score"]))
                table.setItem(row_idx, 5, score_item(report["formatting_score"]))

        except Exception as e:
            print(f"[Reports] Could not load history: {e}")

    def on_activate(self):
        """Refresh history table when page becomes visible."""
        self._load_history(self._table)

    def set_result(self, result: dict):
        """Called by MainWindow after analysis completes."""
        self._last_result = result
        self._export_card.setEnabled(True)
        self._load_history(self._table)

    def _export_html(self):
        if not self._last_result:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save HTML Report", "reports/analysis_report.html",
            "HTML Files (*.html)"
        )
        if path:
            try:
                from utils.report_exporter import export_html
                export_html(self._last_result, path)
                QMessageBox.information(self, "Export Complete",
                    f"HTML report saved to:\n{path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", str(e))

    def _export_text(self):
        if not self._last_result:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Text Report", "reports/analysis_report.txt",
            "Text Files (*.txt)"
        )
        if path:
            try:
                from utils.report_exporter import export_text
                export_text(self._last_result, path)
                QMessageBox.information(self, "Export Complete",
                    f"Text report saved to:\n{path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", str(e))
