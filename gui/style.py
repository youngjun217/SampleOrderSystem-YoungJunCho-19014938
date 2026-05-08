"""전역 QSS 스타일시트"""

DARK = """
/* ── 전역 ─────────────────────────────────────────── */
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", "Malgun Gothic", sans-serif;
    font-size: 13px;
}
QMainWindow { background-color: #181825; }

/* ── 사이드바 ────────────────────────────────────────── */
#sidebar {
    background-color: #11111b;
    border-right: 1px solid #313244;
    min-width: 200px;
    max-width: 200px;
}
#logo_label {
    color: #89b4fa;
    font-size: 15px;
    font-weight: bold;
    padding: 20px 16px 10px 16px;
    border-bottom: 1px solid #313244;
}
#nav_btn {
    background-color: transparent;
    color: #a6adc8;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: left;
    font-size: 13px;
}
#nav_btn:hover  { background-color: #313244; color: #cdd6f4; }
#nav_btn:checked {
    background-color: #313244;
    color: #89b4fa;
    font-weight: bold;
    border-left: 3px solid #89b4fa;
}

/* ── 콘텐츠 영역 ────────────────────────────────────── */
#content { background-color: #1e1e2e; }
#page_title {
    color: #cdd6f4;
    font-size: 18px;
    font-weight: bold;
    padding: 8px 0px;
}

/* ── 카드 ─────────────────────────────────────────── */
#card {
    background-color: #313244;
    border-radius: 10px;
    padding: 16px;
}
#card_title {
    color: #a6adc8;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
}
#card_value {
    color: #cdd6f4;
    font-size: 24px;
    font-weight: bold;
    padding-top: 4px;
}
#card_value_sm {
    color: #89b4fa;
    font-size: 14px;
    font-weight: bold;
}

/* ── 테이블 ────────────────────────────────────────── */
QTableWidget {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 8px;
    gridline-color: #313244;
    selection-background-color: #45475a;
    selection-color: #cdd6f4;
    outline: none;
}
QTableWidget::item { padding: 6px 10px; border: none; }
QTableWidget::item:hover { background-color: #313244; }
QHeaderView::section {
    background-color: #11111b;
    color: #a6adc8;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid #313244;
}
QTableWidget::item:selected { background-color: #45475a; }

/* ── 버튼 ─────────────────────────────────────────── */
QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton:hover   { background-color: #b4d0ff; }
QPushButton:pressed { background-color: #74a0e8; }
#btn_danger {
    background-color: #f38ba8;
    color: #1e1e2e;
}
#btn_danger:hover { background-color: #f5a0b5; }
#btn_success {
    background-color: #a6e3a1;
    color: #1e1e2e;
}
#btn_success:hover { background-color: #bff0ba; }
#btn_warn {
    background-color: #f9e2af;
    color: #1e1e2e;
}
#btn_warn:hover { background-color: #fcecc9; }
#btn_secondary {
    background-color: #45475a;
    color: #cdd6f4;
}
#btn_secondary:hover { background-color: #585b70; }

/* ── 입력 ─────────────────────────────────────────── */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 7px 10px;
    color: #cdd6f4;
    selection-background-color: #89b4fa;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #89b4fa;
}
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background-color: #313244;
    border: 1px solid #45475a;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background-color: #585b70;
    border-radius: 3px;
    width: 20px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #89b4fa;
}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-bottom: 6px solid #cdd6f4;
    width: 0; height: 0;
}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #cdd6f4;
    width: 0; height: 0;
}
QSpinBox::up-arrow:hover, QDoubleSpinBox::up-arrow:hover {
    border-bottom-color: #1e1e2e;
}
QSpinBox::down-arrow:hover, QDoubleSpinBox::down-arrow:hover {
    border-top-color: #1e1e2e;
}

/* ── 라벨 ─────────────────────────────────────────── */
QLabel { color: #cdd6f4; }
#label_muted  { color: #6c7086; font-size: 11px; }
#label_hint   { color: #a6adc8; font-size: 12px; }

/* ── 구분선 ────────────────────────────────────────── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: #313244;
}

/* ── 스크롤바 ──────────────────────────────────────── */
QScrollBar:vertical {
    background-color: #1e1e2e;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background-color: #585b70; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }

/* ── 다이얼로그 ────────────────────────────────────── */
QDialog {
    background-color: #1e1e2e;
    border: 1px solid #45475a;
    border-radius: 10px;
}

/* ── 상태 뱃지 ────────────────────────────────────── */
#badge_reserved  { background:#f9e2af; color:#1e1e2e; border-radius:4px; padding:2px 8px; font-weight:bold; font-size:11px; }
#badge_producing { background:#89b4fa; color:#1e1e2e; border-radius:4px; padding:2px 8px; font-weight:bold; font-size:11px; }
#badge_confirmed { background:#a6e3a1; color:#1e1e2e; border-radius:4px; padding:2px 8px; font-weight:bold; font-size:11px; }
#badge_release   { background:#94e2d5; color:#1e1e2e; border-radius:4px; padding:2px 8px; font-weight:bold; font-size:11px; }
#badge_rejected  { background:#f38ba8; color:#1e1e2e; border-radius:4px; padding:2px 8px; font-weight:bold; font-size:11px; }
#badge_idle      { background:#45475a; color:#cdd6f4; border-radius:4px; padding:2px 8px; font-weight:bold; font-size:11px; }
#badge_running   { background:#89b4fa; color:#1e1e2e; border-radius:4px; padding:2px 8px; font-weight:bold; font-size:11px; }
#badge_surplus   { background:#a6e3a1; color:#1e1e2e; border-radius:4px; padding:2px 8px; font-weight:bold; font-size:11px; }
#badge_short     { background:#f9e2af; color:#1e1e2e; border-radius:4px; padding:2px 8px; font-weight:bold; font-size:11px; }
#badge_depleted  { background:#f38ba8; color:#1e1e2e; border-radius:4px; padding:2px 8px; font-weight:bold; font-size:11px; }
"""

STATUS_BADGE_ID = {
    "RESERVED":  "badge_reserved",
    "PRODUCING": "badge_producing",
    "CONFIRMED": "badge_confirmed",
    "RELEASE":   "badge_release",
    "REJECTED":  "badge_rejected",
    "IDLE":      "badge_idle",
    "RUNNING":   "badge_running",
    "여유":      "badge_surplus",
    "부족":      "badge_short",
    "고갈":      "badge_depleted",
}
