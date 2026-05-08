"""공용 위젯 헬퍼"""
from PyQt6.QtWidgets import (
    QLabel, QFrame, QHBoxLayout, QVBoxLayout, QWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QSizePolicy, QProgressBar,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from gui.style import STATUS_BADGE_ID


# ── 상태 컬러 맵 ────────────────────────────────────────────────────
STATUS_COLORS = {
    "RESERVED":  ("#f9e2af", "#1e1e2e"),
    "PRODUCING": ("#89b4fa", "#1e1e2e"),
    "CONFIRMED": ("#a6e3a1", "#1e1e2e"),
    "RELEASE":   ("#94e2d5", "#1e1e2e"),
    "REJECTED":  ("#f38ba8", "#1e1e2e"),
    "IDLE":      ("#45475a", "#cdd6f4"),
    "RUNNING":   ("#89b4fa", "#1e1e2e"),
    "여유":      ("#a6e3a1", "#1e1e2e"),
    "부족":      ("#f9e2af", "#1e1e2e"),
    "고갈":      ("#f38ba8", "#1e1e2e"),
}

# ── 상태 뱃지 위젯 (setCellWidget 용) ─────────────────────────────
def status_widget(text: str) -> QWidget:
    """테이블 셀에 넣는 컬러 뱃지 — hover/선택에 영향받지 않음."""
    bg, fg = STATUS_COLORS.get(text, ("#45475a", "#cdd6f4"))
    container = QWidget()
    container.setStyleSheet("background: transparent;")
    lay = QHBoxLayout(container)
    lay.setContentsMargins(6, 3, 6, 3)
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(
        f"background-color: {bg}; color: {fg}; "
        f"border-radius: 5px; padding: 2px 10px; "
        f"font-weight: bold; font-size: 11px;"
    )
    lay.addWidget(lbl)
    return container


# ── 수율 게이지 바 위젯 ────────────────────────────────────────────
def yield_bar_widget(value: float) -> QWidget:
    """value: 0.0 ~ 1.0"""
    pct = int(value * 100)
    if pct >= 90:
        color = "#a6e3a1"
    elif pct >= 80:
        color = "#f9e2af"
    else:
        color = "#f38ba8"

    container = QWidget()
    container.setStyleSheet("background: transparent;")
    lay = QHBoxLayout(container)
    lay.setContentsMargins(8, 6, 8, 6)

    bar = QProgressBar()
    bar.setRange(0, 100)
    bar.setValue(pct)
    bar.setTextVisible(True)
    bar.setFormat(f"{value * 100:.1f}%")
    bar.setFixedHeight(18)
    bar.setStyleSheet(f"""
        QProgressBar {{
            background-color: #1e1e2e;
            border: 1px solid #45475a;
            border-radius: 5px;
            text-align: center;
            color: #cdd6f4;
            font-size: 11px;
            font-weight: bold;
        }}
        QProgressBar::chunk {{
            background-color: {color};
            border-radius: 4px;
        }}
    """)
    lay.addWidget(bar)
    return container


# ── 요약 카드 ──────────────────────────────────────────────────────
def summary_card(title: str, value: str, color: str = "#cdd6f4") -> QFrame:
    card = QFrame()
    card.setObjectName("card")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(16, 14, 16, 14)
    lay.setSpacing(6)

    t = QLabel(title.upper())
    t.setObjectName("card_title")
    lay.addWidget(t)

    v = QLabel(value)
    v.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
    lay.addWidget(v)
    return card


# ── 섹션 헤더 ──────────────────────────────────────────────────────
def section_header(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("page_title")
    return lbl


# ── 구분선 ─────────────────────────────────────────────────────────
def h_line() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    return line


# ── 테이블 공통 설정 ────────────────────────────────────────────────
def make_table(headers: list[str]) -> QTableWidget:
    tbl = QTableWidget()
    tbl.setColumnCount(len(headers))
    tbl.setHorizontalHeaderLabels(headers)
    tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    tbl.setAlternatingRowColors(False)
    tbl.verticalHeader().setVisible(False)
    tbl.horizontalHeader().setStretchLastSection(True)
    tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    tbl.setShowGrid(False)
    tbl.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    tbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    return tbl


def cell(text: str, align=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft) -> QTableWidgetItem:
    item = QTableWidgetItem(str(text))
    item.setTextAlignment(align)
    return item


def cell_c(text: str) -> QTableWidgetItem:
    return cell(text, Qt.AlignmentFlag.AlignCenter)


# ── 하위 호환 (item 방식, setCellWidget 불가할 때) ──────────────────
def colored_cell(text: str) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    if text in STATUS_COLORS:
        bg, fg = STATUS_COLORS[text]
        item.setBackground(QColor(bg))
        item.setForeground(QColor(fg))
    return item
