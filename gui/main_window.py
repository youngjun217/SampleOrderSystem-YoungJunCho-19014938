from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

from controller.sample_controller import SampleController
from controller.order_controller import OrderController
from controller.production_controller import ProductionController

from gui.panels.sample_panel     import SamplePanel
from gui.panels.order_panel      import OrderPanel
from gui.panels.monitor_panel    import MonitorPanel
from gui.panels.production_panel import ProductionPanel
from gui.widgets import summary_card, h_line


class MainWindow(QMainWindow):
    def __init__(self, sc: SampleController, oc: OrderController, pc: ProductionController):
        super().__init__()
        self._sc = sc; self._oc = oc; self._pc = pc

        self.setWindowTitle("S Semi — 반도체 시료 생산주문관리 시스템")
        self.setMinimumSize(1200, 750)
        self.resize(1400, 840)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())
        root.addWidget(self._build_content())

        self._switch(0)

    # ── 사이드바 ────────────────────────────────────────────────────
    def _build_sidebar(self) -> QWidget:
        sb = QWidget(); sb.setObjectName("sidebar")
        lay = QVBoxLayout(sb)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        logo = QLabel("◈  S Semi")
        logo.setObjectName("logo_label")
        lay.addWidget(logo)

        menus = [
            ("대시보드",      "📊"),
            ("시료 관리",     "🔬"),
            ("주문 관리",     "📋"),
            ("모니터링",      "📈"),
            ("생산 라인",     "⚙"),
        ]
        self._nav_btns = []
        for i, (label, icon) in enumerate(menus):
            btn = QPushButton(f"  {icon}  {label}")
            btn.setObjectName("nav_btn")
            btn.setCheckable(True)
            btn.setFixedHeight(44)
            btn.clicked.connect(lambda _, idx=i: self._switch(idx))
            lay.addWidget(btn)
            self._nav_btns.append(btn)

        lay.addStretch()

        ver = QLabel("v1.0  S Semi")
        ver.setObjectName("label_muted")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setContentsMargins(0, 0, 0, 12)
        lay.addWidget(ver)
        return sb

    # ── 콘텐츠 ──────────────────────────────────────────────────────
    def _build_content(self) -> QWidget:
        self._stack = QStackedWidget()
        self._stack.setObjectName("content")

        self._stack.addWidget(self._build_dashboard())
        self._stack.addWidget(SamplePanel(self._sc))
        self._stack.addWidget(OrderPanel(self._oc, self._sc, self._pc))
        self._stack.addWidget(MonitorPanel(self._sc, self._oc, self._pc))
        self._stack.addWidget(ProductionPanel(self._pc, self._oc))
        return self._stack

    def _switch(self, idx: int):
        self._stack.setCurrentIndex(idx)
        for i, btn in enumerate(self._nav_btns):
            btn.setChecked(i == idx)
        if idx == 0:
            self._refresh_dashboard()

    # ── 대시보드 ─────────────────────────────────────────────────────
    def _build_dashboard(self) -> QWidget:
        page = QWidget()
        self._dash_lay = QVBoxLayout(page)
        self._dash_lay.setContentsMargins(28, 20, 28, 20)
        self._dash_lay.setSpacing(16)

        from gui.widgets import section_header
        self._dash_lay.addWidget(section_header("대시보드"))
        self._dash_lay.addWidget(h_line())

        self._card_row = QHBoxLayout(); self._card_row.setSpacing(12)
        self._dash_lay.addLayout(self._card_row)

        # 주문 현황 레이블
        lbl = QLabel("주문 현황"); lbl.setObjectName("label_hint")
        self._dash_lay.addWidget(lbl)

        from gui.widgets import make_table
        self._dash_tbl = make_table(["주문 ID", "고객명", "시료명", "수량", "상태", "접수일"])
        self._dash_lay.addWidget(self._dash_tbl)
        self._dash_lay.addStretch()
        return page

    def _refresh_dashboard(self):
        # 카드 초기화
        while self._card_row.count():
            item = self._card_row.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        smry   = self._sc.summary()
        counts = self._oc.count_by_status()

        data = [
            ("등록 시료",         f"{smry['total_types']} 종",        "#89b4fa"),
            ("총 재고",            f"{smry['total_stock']} 개",        "#a6e3a1"),
            ("접수 (RESERVED)",   f"{counts.get('RESERVED',0)} 건",   "#f9e2af"),
            ("생산 중 (PRODUCING)", f"{counts.get('PRODUCING',0)} 건", "#89b4fa"),
            ("출고 대기",          f"{counts.get('CONFIRMED',0)} 건",  "#a6e3a1"),
            ("출고 완료",          f"{counts.get('RELEASE',0)} 건",    "#94e2d5"),
        ]
        for t, v, c in data:
            self._card_row.addWidget(summary_card(t, v, c))

        # 테이블
        from model.order import OrderStatus
        orders = sorted(self._oc.get_all(), key=lambda o: o.created_at, reverse=True)[:20]
        from gui.widgets import cell, cell_c, colored_cell
        self._dash_tbl.setRowCount(len(orders))
        for r, o in enumerate(orders):
            self._dash_tbl.setItem(r, 0, cell(o.id))
            self._dash_tbl.setItem(r, 1, cell(o.customer_name))
            self._dash_tbl.setItem(r, 2, cell(o.sample_name))
            self._dash_tbl.setItem(r, 3, cell_c(f"{o.quantity} 개"))
            self._dash_tbl.setItem(r, 4, colored_cell(o.status.value))
            self._dash_tbl.setItem(r, 5, cell(o.created_at[:10]))
            self._dash_tbl.setRowHeight(r, 34)
