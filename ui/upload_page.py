"""
ResumeAI Platform — Resume Upload Page
Phase 3 will add full PDF parsing and section extraction.
For now this scaffolds the UI layout.
"""

from PyQt5.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QFileDialog, QWidget, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

from ui.base_page import BasePage
from ui.components import SectionHeader, Divider, Badge
from ui.styles import COLORS


class DropZone(QFrame):
    """
    Drag-and-drop / click-to-browse file drop zone.
    Emits file_selected(path) when a PDF is chosen.
    """
    file_selected = pyqtSignal(str)

    def __init__(self, label: str = "Drop your resume PDF here", parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("DropZone")
        self.setMinimumHeight(200)
        self._apply_style(active=False)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        self.icon_lbl = QLabel("📂")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setStyleSheet("font-size: 40px; background: transparent;")
        layout.addWidget(self.icon_lbl)

        self.label_lbl = QLabel(label)
        self.label_lbl.setAlignment(Qt.AlignCenter)
        self.label_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 14px; background: transparent;"
        )
        layout.addWidget(self.label_lbl)

        sub = QLabel("PDF files only · Max 10 MB")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 12px; background: transparent;"
        )
        layout.addWidget(sub)

        btn = QPushButton("Browse Files")
        btn.setObjectName("secondaryBtn")
        btn.setFixedSize(140, 36)
        btn.clicked.connect(self._open_dialog)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

    def _apply_style(self, active: bool):
        border_color = COLORS["accent"] if active else COLORS["border"]
        bg_color = COLORS["accent_light"] if active else COLORS["bg_card"]
        self.setStyleSheet(f"""
            QFrame#DropZone {{
                background-color: {bg_color};
                border: 2px dashed {border_color};
                border-radius: 14px;
            }}
        """)

    def _open_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Resume PDF", "", "PDF Files (*.pdf)"
        )
        if path:
            self.file_selected.emit(path)

    # ── Drag & Drop ───────────────────────────────────────────────────────────
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith(".pdf"):
                event.acceptProposedAction()
                self._apply_style(active=True)

    def dragLeaveEvent(self, event):
        self._apply_style(active=False)

    def dropEvent(self, event: QDropEvent):
        self._apply_style(active=False)
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path.lower().endswith(".pdf"):
                self.file_selected.emit(path)


class UploadPage(BasePage):
    PAGE_TITLE    = "Resume Upload"
    PAGE_SUBTITLE = "Upload your resume PDF to begin analysis"

    resume_uploaded = pyqtSignal(str)  # emits file path

    def build_ui(self):
        header = SectionHeader(
            "Resume Upload",
            "Upload your resume PDF. We'll extract text, sections, skills, and links."
        )
        self.content_layout.addWidget(header)

        # ── Drop Zone ─────────────────────────────────────────────────
        self.drop_zone = DropZone()
        self.drop_zone.file_selected.connect(self._on_file_selected)
        self.content_layout.addWidget(self.drop_zone)

        # ── File info row (hidden until file is loaded) ───────────────
        self.file_info_row = self._build_file_info_row()
        self.file_info_row.hide()
        self.content_layout.addWidget(self.file_info_row)

        self.content_layout.addWidget(Divider())

        # ── Instructions ──────────────────────────────────────────────
        self.content_layout.addWidget(self._build_instructions())
        self.content_layout.addStretch()

    def _build_file_info_row(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS["bg_card"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 10px;
            }}
        """)
        row = QHBoxLayout(frame)
        row.setContentsMargins(16, 12, 16, 12)
        row.setSpacing(12)

        icon = QLabel("📄")
        icon.setStyleSheet("font-size: 20px; background: transparent;")
        row.addWidget(icon)

        col = QVBoxLayout()
        col.setSpacing(2)
        self.file_name_lbl = QLabel("resume.pdf")
        self.file_name_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 13px; font-weight: 600;"
        )
        self.file_size_lbl = QLabel("")
        self.file_size_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 12px;"
        )
        col.addWidget(self.file_name_lbl)
        col.addWidget(self.file_size_lbl)
        row.addLayout(col, stretch=1)

        self.status_badge = Badge("Ready", "success")
        row.addWidget(self.status_badge)

        remove_btn = QPushButton("Remove")
        remove_btn.setObjectName("secondaryBtn")
        remove_btn.setFixedSize(80, 30)
        remove_btn.clicked.connect(self._remove_file)
        row.addWidget(remove_btn)

        return frame

    def _build_instructions(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("What happens after upload?")
        title.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 15px; font-weight: 700;"
        )
        layout.addWidget(title)

        steps = [
            ("🔍", "Text Extraction",    "We extract all text while preserving section structure."),
            ("📋", "Section Detection",  "Identifies Summary, Skills, Projects, Experience, and Education."),
            ("🔗", "Link Validation",    "Validates GitHub, LinkedIn, and portfolio URLs."),
            ("🏷️", "Skill Extraction",  "Pulls out technical skills, tools, and frameworks."),
        ]

        for icon, step_title, step_body in steps:
            row = QHBoxLayout()
            row.setSpacing(14)
            icon_lbl = QLabel(icon)
            icon_lbl.setFixedWidth(32)
            icon_lbl.setStyleSheet("font-size: 18px; background: transparent;")
            row.addWidget(icon_lbl, alignment=Qt.AlignTop)

            text_col = QVBoxLayout()
            text_col.setSpacing(2)
            t = QLabel(step_title)
            t.setStyleSheet(
                f"color: {COLORS['text_primary']}; font-size: 13px; font-weight: 600;"
            )
            b = QLabel(step_body)
            b.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
            text_col.addWidget(t)
            text_col.addWidget(b)
            row.addLayout(text_col)
            row.addStretch()

            layout.addLayout(row)

        return container

    # ── Handlers ──────────────────────────────────────────────────────────────
    def _on_file_selected(self, path: str):
        import os
        size_bytes = os.path.getsize(path)
        size_kb = size_bytes / 1024
        size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"

        self.file_name_lbl.setText(os.path.basename(path))
        self.file_size_lbl.setText(size_str)
        self.file_info_row.show()
        self.drop_zone.hide()
        self.resume_uploaded.emit(path)

    def _remove_file(self):
        self.file_info_row.hide()
        self.drop_zone.show()
