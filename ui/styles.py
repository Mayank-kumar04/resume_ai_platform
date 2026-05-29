"""
ResumeAI Platform — Global Stylesheet
All QSS rules live here. Import COLORS for programmatic use in widgets.
"""

# ─── Color Palette ────────────────────────────────────────────────────────────
COLORS = {
    "bg_base":       "#0D1117",   # deepest background
    "bg_surface":    "#161B22",   # sidebar, panels
    "bg_card":       "#1C2128",   # cards, inputs
    "bg_card_hover": "#21262D",   # card hover state
    "border":        "#30363D",   # subtle borders
    "border_focus":  "#58A6FF",   # focused input border

    "accent":        "#2563EB",   # primary blue
    "accent_hover":  "#1D4ED8",
    "accent_light":  "#1E3A5F",   # tinted backgrounds

    "success":       "#22C55E",
    "success_bg":    "#14532D",
    "warning":       "#F59E0B",
    "warning_bg":    "#451A03",
    "danger":        "#EF4444",
    "danger_bg":     "#450A0A",
    "info":          "#38BDF8",

    "text_primary":  "#E6EDF3",
    "text_secondary":"#8B949E",
    "text_muted":    "#484F58",

    "score_high":    "#22C55E",   # 80+
    "score_mid":     "#F59E0B",   # 50–79
    "score_low":     "#EF4444",   # <50
}

# ─── Main Stylesheet ──────────────────────────────────────────────────────────
STYLESHEET = f"""
/* ── Base ──────────────────────────────────────────────────── */
QMainWindow, QDialog, QWidget {{
    background-color: {COLORS["bg_base"]};
    color: {COLORS["text_primary"]};
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}}

QScrollArea {{
    border: none;
    background: transparent;
}}

QScrollBar:vertical {{
    background: {COLORS["bg_surface"]};
    width: 6px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS["border"]};
    border-radius: 3px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS["text_secondary"]};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: {COLORS["bg_surface"]};
    height: 6px;
    border-radius: 3px;
}}

QScrollBar::handle:horizontal {{
    background: {COLORS["border"]};
    border-radius: 3px;
}}

/* ── Labels ─────────────────────────────────────────────────── */
QLabel {{
    color: {COLORS["text_primary"]};
    background: transparent;
}}

/* ── Buttons ─────────────────────────────────────────────────── */
QPushButton {{
    background-color: {COLORS["accent"]};
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {COLORS["accent_hover"]};
}}

QPushButton:pressed {{
    background-color: {COLORS["accent"]};
    opacity: 0.9;
}}

QPushButton:disabled {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_muted"]};
}}

QPushButton#secondaryBtn {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
}}

QPushButton#secondaryBtn:hover {{
    background-color: {COLORS["bg_card_hover"]};
    border-color: {COLORS["text_secondary"]};
}}

QPushButton#dangerBtn {{
    background-color: {COLORS["danger_bg"]};
    color: {COLORS["danger"]};
    border: 1px solid {COLORS["danger"]};
}}

QPushButton#dangerBtn:hover {{
    background-color: {COLORS["danger"]};
    color: #ffffff;
}}

/* ── Text Inputs ─────────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    selection-background-color: {COLORS["accent"]};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {COLORS["border_focus"]};
    background-color: {COLORS["bg_card_hover"]};
}}

QLineEdit::placeholder, QTextEdit::placeholder {{
    color: {COLORS["text_muted"]};
}}

/* ── ComboBox ────────────────────────────────────────────────── */
QComboBox {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px;
    min-width: 120px;
}}

QComboBox:hover {{
    border-color: {COLORS["text_secondary"]};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    selection-background-color: {COLORS["accent_light"]};
    padding: 4px;
}}

/* ── Tab Widget ──────────────────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    background: {COLORS["bg_card"]};
}}

QTabBar::tab {{
    background: transparent;
    color: {COLORS["text_secondary"]};
    padding: 10px 20px;
    border-bottom: 2px solid transparent;
    font-size: 13px;
}}

QTabBar::tab:selected {{
    color: {COLORS["text_primary"]};
    border-bottom: 2px solid {COLORS["accent"]};
}}

QTabBar::tab:hover:!selected {{
    color: {COLORS["text_primary"]};
}}

/* ── Progress Bar ────────────────────────────────────────────── */
QProgressBar {{
    background-color: {COLORS["bg_card"]};
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
    color: transparent;
}}

QProgressBar::chunk {{
    background-color: {COLORS["accent"]};
    border-radius: 4px;
}}

QProgressBar#successBar::chunk {{
    background-color: {COLORS["success"]};
}}

QProgressBar#warningBar::chunk {{
    background-color: {COLORS["warning"]};
}}

QProgressBar#dangerBar::chunk {{
    background-color: {COLORS["danger"]};
}}

/* ── Tooltip ─────────────────────────────────────────────────── */
QToolTip {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}

/* ── Table ───────────────────────────────────────────────────── */
QTableWidget {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    gridline-color: {COLORS["border"]};
    selection-background-color: {COLORS["accent_light"]};
}}

QTableWidget::item {{
    padding: 8px 12px;
}}

QTableWidget::item:selected {{
    background-color: {COLORS["accent_light"]};
    color: {COLORS["text_primary"]};
}}

QHeaderView::section {{
    background-color: {COLORS["bg_surface"]};
    color: {COLORS["text_secondary"]};
    border: none;
    border-bottom: 1px solid {COLORS["border"]};
    padding: 10px 12px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ── Splitter ────────────────────────────────────────────────── */
QSplitter::handle {{
    background: {COLORS["border"]};
}}

/* ── Menu ────────────────────────────────────────────────────── */
QMenu {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 20px;
    border-radius: 6px;
}}

QMenu::item:selected {{
    background-color: {COLORS["accent_light"]};
}}

/* ── CheckBox ────────────────────────────────────────────────── */
QCheckBox {{
    color: {COLORS["text_primary"]};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {COLORS["border"]};
    border-radius: 4px;
    background: {COLORS["bg_card"]};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS["accent"]};
    border-color: {COLORS["accent"]};
}}
"""
