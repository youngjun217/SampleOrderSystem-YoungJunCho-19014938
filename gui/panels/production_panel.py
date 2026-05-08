import math
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QMessageBox, QTabWidget,
)
from PyQt6.QtCore import Qt, QTimer
from gui.widgets import section_header, make_table, cell, cell_c, h_line, status_widget
from controller.order_controller import OrderController
from controller.production_controller import ProductionController
from model.production import ProductionStatus
from model.production_line import LineStatus


def _fmt_time(h: float) -> str:
    hi = int(h); m = int((h - hi) * 60)
    return f"{hi}h {m:02d}m"


def _eta_str(started_at: str, total_time: float) -> str:
    if not started_at:
        return "대기 중"
    try:
        eta = datetime.fromisoformat(started_at) + timedelta(hours=total_time)
        now = datetime.now()
        if eta < now:
            return "⚠ 초과"
        diff = eta - now
        h, r = divmod(int(diff.total_seconds()), 3600)
        return f"약 {h}h {r//60:02d}m 후"
    except Exception:
        return "-"


class ProductionPanel(QWidget):
    def __init__(self, pc: ProductionController, oc: OrderController):
        super().__init__()
        self._pc = pc; self._oc = oc
        self._build()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(10_000)

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 20, 28, 20)
        lay.setSpacing(16)

        hdr = QHBoxLayout()
        hdr.addWidget(section_header("생산 라인"))
        hdr.addStretch()
        btn_r = QPushButton("새로고침"); btn_r.setObjectName("btn_secondary")
        btn_r.setFixedWidth(100); btn_r.clicked.connect(self._refresh)
        hdr.addWidget(btn_r)
        lay.addLayout(hdr)
        lay.addWidget(h_line())

        # 라인 현황 카드
        self._line_cards = QHBoxLayout(); self._line_cards.setSpacing(10)
        lay.addLayout(self._line_cards)

        # 탭
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border:1px solid #313244; border-radius:8px; top:-1px; }
            QTabBar::tab { background:#313244; color:#a6adc8; padding:8px 20px;
                           border-top-left-radius:6px; border-top-right-radius:6px; margin-right:2px; }
            QTabBar::tab:selected { background:#1e1e2e; color:#89b4fa; font-weight:bold; }
        """)

        self._run_tbl  = make_table(["생산 ID", "라인", "시료명", "주문ID", "부족분", "실생산량", "총시간", "완료예정"])
        self._wait_tbl = make_table(["순위", "생산 ID", "주문ID", "시료명", "부족분", "실생산량", "총시간"])

        tabs.addTab(self._run_tbl,  "생산 중  (RUNNING)")
        tabs.addTab(self._wait_tbl, "대기 큐  (FIFO)")
        lay.addWidget(tabs)
        self._tabs = tabs

        # 완료 버튼
        btn_row = QHBoxLayout(); btn_row.addStretch()
        btn_done = QPushButton("✔  생산 완료 처리"); btn_done.setObjectName("btn_success")
        btn_done.clicked.connect(self._complete)
        btn_row.addWidget(btn_done)
        lay.addLayout(btn_row)

        self._refresh()

    def _refresh(self):
        lines   = self._pc.get_lines()
        running = self._pc.get_running()
        waiting = self._pc.get_waiting()
        line_map = {l.id: l for l in lines}

        # ── 라인 카드 ──────────────────────────────────────────────
        while self._line_cards.count():
            item = self._line_cards.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        for line in lines:
            card = QFrame(); card.setObjectName("card")
            cl = QVBoxLayout(card); cl.setContentsMargins(14, 12, 14, 12); cl.setSpacing(6)
            name_lbl = QLabel(line.name); name_lbl.setObjectName("card_title")
            cl.addWidget(name_lbl)
            if line.status == LineStatus.IDLE:
                st_lbl = QLabel("● 유휴"); st_lbl.setStyleSheet("color:#45475a; font-weight:bold;")
            else:
                prod = next((p for p in running if p.line_id == line.id), None)
                sample_name = prod.sample_name if prod else "-"
                st_lbl = QLabel(f"● 가동 중"); st_lbl.setStyleSheet("color:#89b4fa; font-weight:bold;")
                sub = QLabel(sample_name); sub.setObjectName("label_muted"); cl.addWidget(sub)
            cl.addWidget(st_lbl)
            self._line_cards.addWidget(card)
        self._line_cards.addStretch()

        # ── RUNNING 테이블 ─────────────────────────────────────────
        self._run_tbl.setRowCount(len(running))
        for r, p in enumerate(running):
            line = line_map.get(p.line_id)
            eta  = _eta_str(p.started_at, p.total_time)
            self._run_tbl.setItem(r, 0, cell(p.id))
            self._run_tbl.setItem(r, 1, cell(line.name if line else p.line_id))
            self._run_tbl.setItem(r, 2, cell(p.sample_name))
            self._run_tbl.setItem(r, 3, cell(p.order_id))
            self._run_tbl.setItem(r, 4, cell_c(f"{p.shortage} 개"))
            self._run_tbl.setItem(r, 5, cell_c(f"{p.actual_quantity} 개"))
            self._run_tbl.setItem(r, 6, cell_c(_fmt_time(p.total_time)))
            self._run_tbl.setCellWidget(r, 7, status_widget("⚠ 초과" if "초과" in eta else eta))
            self._run_tbl.setRowHeight(r, 40)

        # ── WAITING 테이블 (FIFO) ──────────────────────────────────
        self._wait_tbl.setRowCount(len(waiting))
        for r, p in enumerate(waiting):
            rank_item = cell_c(f"#{r+1}")
            if r == 0:
                rank_item.setForeground(QColor("#a6e3a1"))
            self._wait_tbl.setItem(r, 0, rank_item)
            self._wait_tbl.setItem(r, 1, cell(p.id))
            self._wait_tbl.setItem(r, 2, cell(p.order_id))
            self._wait_tbl.setItem(r, 3, cell(p.sample_name))
            self._wait_tbl.setItem(r, 4, cell_c(f"{p.shortage} 개"))
            self._wait_tbl.setItem(r, 5, cell_c(f"{p.actual_quantity} 개"))
            self._wait_tbl.setItem(r, 6, cell_c(_fmt_time(p.total_time)))
            self._wait_tbl.setRowHeight(r, 36)

    def _complete(self):
        if self._tabs.currentIndex() != 0:
            QMessageBox.information(self, "알림", "'생산 중' 탭에서 완료할 항목을 선택하세요.")
            return
        row = self._run_tbl.currentRow()
        if row < 0:
            QMessageBox.information(self, "알림", "완료 처리할 생산 항목을 선택하세요.")
            return
        prod_id = self._run_tbl.item(row, 0).text()
        result  = self._pc.complete(prod_id)
        if not result:
            QMessageBox.warning(self, "오류", "완료 처리에 실패했습니다.")
            return
        order = self._oc.get_by_id(result.order_id)
        msg = (f"생산 완료!\n\n"
               f"시료: {result.sample_name}\n"
               f"부족분 {result.shortage}개 생산 완료\n"
               f"주문 상태: PRODUCING → {order.status.value if order else 'CONFIRMED'}")
        QMessageBox.information(self, "생산 완료", msg)
        self._refresh()
