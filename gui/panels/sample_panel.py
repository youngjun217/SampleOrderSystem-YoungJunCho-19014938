from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QDoubleSpinBox, QSpinBox, QDialog, QFormLayout,
    QMessageBox, QFrame,
)
from PyQt6.QtCore import Qt
from gui.widgets import section_header, make_table, cell, cell_c, h_line
from controller.sample_controller import SampleController


class SamplePanel(QWidget):
    def __init__(self, ctrl: SampleController):
        super().__init__()
        self._ctrl = ctrl
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 20, 28, 20)
        lay.setSpacing(16)

        # 헤더
        hdr = QHBoxLayout()
        hdr.addWidget(section_header("시료 관리"))
        hdr.addStretch()
        btn_add = QPushButton("+ 시료 등록")
        btn_add.setFixedWidth(120)
        btn_add.clicked.connect(self._open_register)
        hdr.addWidget(btn_add)
        lay.addLayout(hdr)
        lay.addWidget(h_line())

        # 검색
        search_row = QHBoxLayout()
        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText("시료 ID 또는 이름으로 검색…")
        self._search_box.textChanged.connect(self._load)
        search_row.addWidget(self._search_box)
        lay.addLayout(search_row)

        # 테이블
        self._tbl = make_table(["시료 ID", "이름", "평균 생산시간", "수율", "재고"])
        lay.addWidget(self._tbl)

        self._load()

    def _load(self):
        kw = self._search_box.text().strip()
        samples = self._ctrl.search(kw) if kw else self._ctrl.get_all()
        self._tbl.setRowCount(len(samples))
        for r, s in enumerate(samples):
            self._tbl.setItem(r, 0, cell(s.id))
            self._tbl.setItem(r, 1, cell(s.name))
            self._tbl.setItem(r, 2, cell_c(f"{s.avg_production_time:.1f} h"))
            self._tbl.setItem(r, 3, cell_c(f"{s.yield_rate * 100:.1f} %"))
            stock_item = cell_c(f"{s.stock_quantity} 개")
            if s.stock_quantity == 0:
                from PyQt6.QtGui import QColor
                stock_item.setForeground(QColor("#f38ba8"))
            elif s.stock_quantity < 5:
                from PyQt6.QtGui import QColor
                stock_item.setForeground(QColor("#f9e2af"))
            else:
                from PyQt6.QtGui import QColor
                stock_item.setForeground(QColor("#a6e3a1"))
            self._tbl.setItem(r, 4, stock_item)

    def _open_register(self):
        dlg = RegisterSampleDialog(self._ctrl, self)
        if dlg.exec():
            self._load()


class RegisterSampleDialog(QDialog):
    def __init__(self, ctrl: SampleController, parent=None):
        super().__init__(parent)
        self._ctrl = ctrl
        self.setWindowTitle("시료 등록")
        self.setFixedSize(420, 320)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)

        title = QLabel("새 시료 등록")
        title.setObjectName("page_title")
        lay.addWidget(title)
        lay.addWidget(h_line())

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._id_edit   = QLineEdit(); self._id_edit.setPlaceholderText("예: GaN-001")
        self._name_edit = QLineEdit(); self._name_edit.setPlaceholderText("예: 질화갈륨 전력소자")
        self._time_spin = QDoubleSpinBox(); self._time_spin.setRange(0.1, 9999); self._time_spin.setSuffix(" h"); self._time_spin.setValue(24.0)
        self._yield_spin = QDoubleSpinBox(); self._yield_spin.setRange(0.01, 1.0); self._yield_spin.setSingleStep(0.01); self._yield_spin.setValue(0.90); self._yield_spin.setDecimals(2)
        self._stock_spin = QSpinBox(); self._stock_spin.setRange(0, 9999); self._stock_spin.setSuffix(" 개")

        form.addRow("시료 ID",       self._id_edit)
        form.addRow("이름",          self._name_edit)
        form.addRow("평균 생산시간", self._time_spin)
        form.addRow("수율",          self._yield_spin)
        form.addRow("초기 재고",     self._stock_spin)
        lay.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        cancel = QPushButton("취소"); cancel.setObjectName("btn_secondary"); cancel.clicked.connect(self.reject)
        ok = QPushButton("등록"); ok.clicked.connect(self._submit)
        btns.addWidget(cancel); btns.addWidget(ok)
        lay.addLayout(btns)

    def _submit(self):
        sample, err = self._ctrl.register(
            self._id_edit.text().strip(),
            self._name_edit.text().strip(),
            self._time_spin.value(),
            self._yield_spin.value(),
            self._stock_spin.value(),
        )
        if err:
            QMessageBox.warning(self, "등록 실패", err)
        else:
            self.accept()
