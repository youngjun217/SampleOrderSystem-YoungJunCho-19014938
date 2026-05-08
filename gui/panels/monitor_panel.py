import math
from collections import defaultdict
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt6.QtCore import Qt, QTimer
from gui.widgets import section_header, summary_card, make_table, cell, cell_c, colored_cell, h_line
from controller.order_controller import OrderController
from controller.sample_controller import SampleController
from controller.production_controller import ProductionController
from model.order import OrderStatus


class MonitorPanel(QWidget):
    def __init__(self, sc: SampleController, oc: OrderController, pc: ProductionController):
        super().__init__()
        self._sc = sc; self._oc = oc; self._pc = pc
        self._build()
        # 10초마다 자동 갱신
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(10_000)

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 20, 28, 20)
        lay.setSpacing(16)

        hdr = QHBoxLayout()
        hdr.addWidget(section_header("모니터링"))
        hdr.addStretch()
        btn = QPushButton("새로고침"); btn.setObjectName("btn_secondary")
        btn.setFixedWidth(100); btn.clicked.connect(self._refresh)
        hdr.addWidget(btn)
        lay.addLayout(hdr)
        lay.addWidget(h_line())

        # 요약 카드 행
        self._card_row = QHBoxLayout()
        self._card_row.setSpacing(12)
        lay.addLayout(self._card_row)

        # 주문 테이블
        lbl_order = QLabel("주문 현황  (REJECTED 제외)")
        lbl_order.setObjectName("label_hint")
        lay.addWidget(lbl_order)
        self._order_tbl = make_table(["주문 ID", "고객명", "시료명", "수량", "상태", "접수일"])
        lay.addWidget(self._order_tbl)

        # 재고 테이블
        lbl_inv = QLabel("시료별 재고 현황")
        lbl_inv.setObjectName("label_hint")
        lay.addWidget(lbl_inv)
        self._inv_tbl = make_table(["시료 ID", "이름", "수율", "재고", "대기주문", "상태"])
        lay.addWidget(self._inv_tbl)

        self._refresh()

    def _refresh(self):
        # 카드 갱신
        while self._card_row.count():
            item = self._card_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        smry   = self._sc.summary()
        counts = self._oc.count_by_status()

        cards = [
            ("등록 시료",  f"{smry['total_types']} 종", "#89b4fa"),
            ("총 재고",    f"{smry['total_stock']} 개", "#a6e3a1"),
            ("접수(RESERVED)", f"{counts.get('RESERVED', 0)} 건", "#f9e2af"),
            ("생산중(PRODUCING)", f"{counts.get('PRODUCING', 0)} 건", "#89b4fa"),
            ("출고대기(CONFIRMED)", f"{counts.get('CONFIRMED', 0)} 건", "#a6e3a1"),
            ("출고완료(RELEASE)", f"{counts.get('RELEASE', 0)} 건", "#94e2d5"),
        ]
        for t, v, c in cards:
            self._card_row.addWidget(summary_card(t, v, c))

        # 주문 테이블
        ACTIVE = [OrderStatus.RESERVED, OrderStatus.PRODUCING,
                  OrderStatus.CONFIRMED, OrderStatus.RELEASE]
        orders = [o for o in self._oc.get_all() if o.status in ACTIVE]
        orders.sort(key=lambda o: o.created_at, reverse=True)
        self._order_tbl.setRowCount(len(orders))
        for r, o in enumerate(orders):
            self._order_tbl.setItem(r, 0, cell(o.id))
            self._order_tbl.setItem(r, 1, cell(o.customer_name))
            self._order_tbl.setItem(r, 2, cell(o.sample_name))
            self._order_tbl.setItem(r, 3, cell_c(f"{o.quantity} 개"))
            self._order_tbl.setItem(r, 4, colored_cell(o.status.value))
            self._order_tbl.setItem(r, 5, cell(o.created_at[:10]))
            self._order_tbl.setRowHeight(r, 34)

        # 재고 테이블
        samples   = self._sc.get_all()
        all_orders = self._oc.get_all()
        demand    = defaultdict(int)
        for o in all_orders:
            if o.status == OrderStatus.RESERVED:
                demand[o.sample_id] += o.quantity

        self._inv_tbl.setRowCount(len(samples))
        for r, s in enumerate(samples):
            req = demand.get(s.id, 0)
            label = "고갈" if s.stock_quantity == 0 else ("부족" if s.stock_quantity < req else "여유")
            self._inv_tbl.setItem(r, 0, cell(s.id))
            self._inv_tbl.setItem(r, 1, cell(s.name))
            self._inv_tbl.setItem(r, 2, cell_c(f"{s.yield_rate*100:.1f} %"))
            self._inv_tbl.setItem(r, 3, cell_c(f"{s.stock_quantity} 개"))
            self._inv_tbl.setItem(r, 4, cell_c(f"{req} 개"))
            self._inv_tbl.setItem(r, 5, colored_cell(label))
            self._inv_tbl.setRowHeight(r, 34)
