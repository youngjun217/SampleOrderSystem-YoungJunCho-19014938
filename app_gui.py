import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from repository.sample_repository       import SampleRepository
from repository.order_repository        import OrderRepository
from repository.production_line_repository import ProductionLineRepository
from repository.production_repository   import ProductionRepository
from controller.sample_controller       import SampleController
from controller.order_controller        import OrderController
from controller.production_controller   import ProductionController
from gui.main_window import MainWindow
from gui.style import DARK


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK)
    font = QFont("Malgun Gothic", 10)
    app.setFont(font)

    data = os.path.join(BASE_DIR, "data")
    sc = SampleController(SampleRepository(os.path.join(data, "samples.json")))
    oc = OrderController(
        OrderRepository(os.path.join(data, "orders.json")),
        SampleRepository(os.path.join(data, "samples.json")),
    )
    pc = ProductionController(
        ProductionRepository(os.path.join(data, "productions.json")),
        ProductionLineRepository(os.path.join(data, "production_lines.json")),
        OrderRepository(os.path.join(data, "orders.json")),
        SampleRepository(os.path.join(data, "samples.json")),
    )

    win = MainWindow(sc, oc, pc)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
