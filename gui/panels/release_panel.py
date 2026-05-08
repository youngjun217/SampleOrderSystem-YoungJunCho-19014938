from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from gui.widgets import section_header, make_table, cell, cell_c, h_line, status_widget
from controller.order_controller import OrderController
from model.order import OrderStatus


class ReleasePanel(QWidget):
    def __init__(self, order_ctrl: OrderController):
        super().__init__()
        self._oc = order_ctrl
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 20, 28, 20)
        lay.setSpacing(16)

        # 헤더
        hdr = QHBoxLayout()
        hdr.addWidget(section_header("출고 처리"))
        hdr.addStretch()
        btn_refresh = QPushButton("새로고침")
        btn_refresh.setObjectName("btn_secondary")
        btn_refresh.setFixedWidth(100)
        btn_refresh.clicked.connect(self._load)
        hdr.addWidget(btn_refresh)
        lay.addLayout(hdr)
        lay.addWidget(h_line())

        # 안내
        hint = QLabel("CONFIRMED 상태의 주문을 선택하고 출고를 실행합니다.")
        hint.setObjectName("label_hint")
        lay.addWidget(hint)

        # 테이블
        self._tbl = make_table(["주문 ID", "고객명", "시료명", "수량", "상태", "접수일"])
        lay.addWidget(self._tbl)

        # 하단 버튼
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn_release = QPushButton("🚚  출고 실행  (CONFIRMED → RELEASE)")
        self._btn_release.setObjectName("btn_success")
        self._btn_release.clicked.connect(self._release)
        btn_row.addWidget(self._btn_release)
        lay.addLayout(btn_row)

        self._load()

    def _load(self):
        orders = self._oc.get_by_status(OrderStatus.CONFIRMED)
        orders.sort(key=lambda o: o.created_at)   # 오래된 순 (선입선출)

        self._tbl.setRowCount(len(orders))
        for r, o in enumerate(orders):
            self._tbl.setItem(r, 0, cell(o.id))
            self._tbl.setItem(r, 1, cell(o.customer_name))
            self._tbl.setItem(r, 2, cell(o.sample_name))
            self._tbl.setItem(r, 3, cell_c(f"{o.quantity} 개"))
            self._tbl.setCellWidget(r, 4, status_widget(o.status.value))
            self._tbl.setItem(r, 5, cell(o.created_at[:10]))
            self._tbl.setRowHeight(r, 40)

        # 버튼 활성화 여부
        self._btn_release.setEnabled(len(orders) > 0)
        if len(orders) == 0:
            self._btn_release.setText("출고 대기 주문 없음")
        else:
            self._btn_release.setText(f"🚚  출고 실행  (CONFIRMED → RELEASE)  —  {len(orders)}건 대기")

    def _release(self):
        row = self._tbl.currentRow()
        if row < 0:
            # 선택 없으면 가장 오래된 주문 자동 선택
            if self._tbl.rowCount() == 0:
                QMessageBox.information(self, "알림", "출고 대기 주문이 없습니다.")
                return
            order_id = self._tbl.item(0, 0).text()
            auto = True
        else:
            order_id = self._tbl.item(row, 0).text()
            auto = False

        order = self._oc.get_by_id(order_id)
        if not order or order.status != OrderStatus.CONFIRMED:
            QMessageBox.warning(self, "오류", "CONFIRMED 상태의 주문이 아닙니다.")
            return

        reply = QMessageBox.question(
            self, "출고 확인",
            f"주문 {order_id} 를 출고 처리하시겠습니까?\n\n"
            f"고객명  : {order.customer_name}\n"
            f"시료    : {order.sample_name}\n"
            f"수량    : {order.quantity}개\n\n"
            f"확인 시 상태가 RELEASE 로 변경됩니다.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        result = self._oc.release(order_id)
        if result:
            QMessageBox.information(
                self, "출고 완료",
                f"출고 처리 완료!\n\n"
                f"주문 ID  : {result.id}\n"
                f"고객명   : {result.customer_name}\n"
                f"시료     : {result.sample_name}\n"
                f"수량     : {result.quantity}개\n"
                f"상태     : CONFIRMED → RELEASE",
            )
            self._load()
        else:
            QMessageBox.warning(self, "오류", "출고 처리에 실패했습니다.")
