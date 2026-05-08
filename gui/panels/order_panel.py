from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QComboBox, QDialog, QFormLayout,
    QMessageBox, QTabWidget, QTableWidget,
)
from PyQt6.QtCore import Qt
from gui.widgets import section_header, make_table, cell, cell_c, h_line, status_widget
from controller.order_controller import OrderController
from controller.production_controller import ProductionController
from controller.sample_controller import SampleController
from model.order import OrderStatus


class OrderPanel(QWidget):
    def __init__(self, order_ctrl: OrderController, sample_ctrl: SampleController,
                 prod_ctrl: ProductionController):
        super().__init__()
        self._oc = order_ctrl
        self._sc = sample_ctrl
        self._pc = prod_ctrl
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 20, 28, 20)
        lay.setSpacing(16)

        hdr = QHBoxLayout()
        hdr.addWidget(section_header("주문 관리"))
        hdr.addStretch()
        btn_new = QPushButton("+ 주문 접수")
        btn_new.setFixedWidth(120)
        btn_new.clicked.connect(self._open_reserve)
        hdr.addWidget(btn_new)
        lay.addLayout(hdr)
        lay.addWidget(h_line())

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #313244; border-radius: 8px; top: -1px; }
            QTabBar::tab { background:#313244; color:#a6adc8; padding:8px 20px;
                           border-top-left-radius:6px; border-top-right-radius:6px; margin-right:2px; }
            QTabBar::tab:selected { background:#1e1e2e; color:#89b4fa; font-weight:bold; }
        """)

        self._all_tbl      = self._make_order_table()
        self._reserved_tbl = self._make_order_table()
        self._prod_tbl     = self._make_order_table()

        tabs.addTab(self._all_tbl,      "전체")
        tabs.addTab(self._reserved_tbl, "접수(RESERVED)")
        tabs.addTab(self._prod_tbl,     "생산중(PRODUCING)")
        tabs.currentChanged.connect(self._load)
        lay.addWidget(tabs)
        self._tabs = tabs

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_approve = QPushButton("✔  승인"); btn_approve.setObjectName("btn_success")
        btn_reject  = QPushButton("✘  거절"); btn_reject.setObjectName("btn_danger")
        btn_refresh = QPushButton("새로고침"); btn_refresh.setObjectName("btn_secondary")
        btn_approve.clicked.connect(self._approve)
        btn_reject.clicked.connect(self._reject)
        btn_refresh.clicked.connect(self._load)
        btn_row.addWidget(btn_approve)
        btn_row.addWidget(btn_reject)
        btn_row.addWidget(btn_refresh)
        lay.addLayout(btn_row)

        self._load()

    def _make_order_table(self):
        tbl = make_table(["주문 ID", "고객명", "시료명", "수량", "상태", "접수일"])
        tbl.setColumnWidth(4, 130)   # 상태 컬럼 — CONFIRMED/PRODUCING 기준
        return tbl

    def _load(self, _=None):
        all_orders      = self._oc.get_all()
        reserved_orders = self._oc.get_by_status(OrderStatus.RESERVED)
        prod_orders     = self._oc.get_by_status(OrderStatus.PRODUCING)

        self._fill_table(self._all_tbl, sorted(all_orders, key=lambda o: o.created_at, reverse=True))
        self._fill_table(self._reserved_tbl, sorted(reserved_orders, key=lambda o: o.created_at, reverse=True))
        self._fill_table(self._prod_tbl, sorted(prod_orders, key=lambda o: o.created_at, reverse=True))

    def _fill_table(self, tbl: QTableWidget, orders):
        tbl.setRowCount(len(orders))
        for r, o in enumerate(orders):
            tbl.setItem(r, 0, cell(o.id))
            tbl.setItem(r, 1, cell(o.customer_name))
            tbl.setItem(r, 2, cell(o.sample_name))
            tbl.setItem(r, 3, cell_c(f"{o.quantity} 개"))
            tbl.setCellWidget(r, 4, status_widget(o.status.value))
            tbl.setItem(r, 5, cell(o.created_at[:10]))
            tbl.setRowHeight(r, 40)

    def _get_selected_order_id(self):
        tbl = self._tabs.currentWidget()
        row = tbl.currentRow()
        if row < 0:
            return None
        return tbl.item(row, 0).text()

    def _approve(self):
        oid = self._get_selected_order_id()
        if not oid:
            QMessageBox.information(self, "알림", "승인할 주문을 선택하세요.")
            return
        order = self._oc.get_by_id(oid)
        if not order or order.status != OrderStatus.RESERVED:
            QMessageBox.warning(self, "오류", "RESERVED 상태의 주문만 승인할 수 있습니다.")
            return
        result = self._oc.approve(oid)
        if result.status == OrderStatus.PRODUCING:
            self._pc.assign_line(oid)
            msg = f"주문 {oid}\n→  재고 부족 → 생산라인 배정 완료\n상태: PRODUCING"
        else:
            msg = f"주문 {oid}\n→  재고 충분 → 즉시 출고 대기\n상태: CONFIRMED"
        QMessageBox.information(self, "승인 완료", msg)
        self._load()

    def _reject(self):
        oid = self._get_selected_order_id()
        if not oid:
            QMessageBox.information(self, "알림", "거절할 주문을 선택하세요.")
            return
        order = self._oc.get_by_id(oid)
        if not order or order.status != OrderStatus.RESERVED:
            QMessageBox.warning(self, "오류", "RESERVED 상태의 주문만 거절할 수 있습니다.")
            return
        dlg = RejectDialog(self)
        if dlg.exec():
            self._oc.reject(oid, dlg.reason())
            self._load()

    def _open_reserve(self):
        dlg = ReserveDialog(self._sc, self._oc, self)
        if dlg.exec():
            self._load()


class RejectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("주문 거절")
        self.setFixedSize(420, 200)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setSpacing(16)
        lay.addWidget(QLabel("거절 사유를 입력하세요."))
        self._edit = QLineEdit()
        self._edit.setPlaceholderText("예: 납기 불가, 시료 미등록 등")
        self._edit.setMinimumHeight(38)
        lay.addWidget(self._edit)
        btns = QHBoxLayout(); btns.addStretch()
        cancel = QPushButton("취소"); cancel.setObjectName("btn_secondary")
        cancel.setMinimumWidth(90); cancel.clicked.connect(self.reject)
        ok = QPushButton("거절 확정"); ok.setObjectName("btn_danger")
        ok.setMinimumWidth(110); ok.clicked.connect(self._confirm)
        btns.addWidget(cancel); btns.addWidget(ok); lay.addLayout(btns)

    def _confirm(self):
        if not self._edit.text().strip():
            QMessageBox.warning(self, "오류", "사유를 입력해야 합니다.")
            return
        self.accept()

    def reason(self): return self._edit.text().strip()


class ReserveDialog(QDialog):
    def __init__(self, sc: SampleController, oc: OrderController, parent=None):
        super().__init__(parent)
        self._sc = sc; self._oc = oc
        self.setWindowTitle("주문 접수")
        self.setFixedSize(520, 340)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(18)

        title = QLabel("새 주문 접수")
        title.setObjectName("page_title")
        lay.addWidget(title)
        lay.addWidget(h_line())

        form = QFormLayout()
        form.setSpacing(16)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self._cust = QLineEdit()
        self._cust.setPlaceholderText("예: KAIST 반도체연구소")
        self._cust.setMinimumHeight(38)

        self._combo = QComboBox()
        self._combo.setMinimumHeight(38)
        samples = self._sc.get_all()
        for s in samples:
            self._combo.addItem(f"{s.id}  —  {s.name}  (재고: {s.stock_quantity}개)", s.id)

        self._qty = QSpinBox()
        self._qty.setRange(1, 9999)
        self._qty.setValue(1)
        self._qty.setSuffix(" 개")
        self._qty.setMinimumHeight(38)

        form.addRow("고객명",    self._cust)
        form.addRow("시료 선택", self._combo)
        form.addRow("주문 수량", self._qty)
        lay.addLayout(form)

        lay.addStretch()
        btns = QHBoxLayout(); btns.addStretch()
        cancel = QPushButton("취소"); cancel.setObjectName("btn_secondary")
        cancel.setMinimumWidth(90); cancel.clicked.connect(self.reject)
        ok = QPushButton("접수"); ok.setMinimumWidth(90); ok.clicked.connect(self._submit)
        btns.addWidget(cancel); btns.addWidget(ok); lay.addLayout(btns)

    def _submit(self):
        cust = self._cust.text().strip()
        sid  = self._combo.currentData()
        qty  = self._qty.value()
        if not cust:
            QMessageBox.warning(self, "오류", "고객명을 입력하세요.")
            return
        order, err = self._oc.create(cust, sid, qty)
        if err:
            QMessageBox.warning(self, "오류", err)
        else:
            self.accept()
