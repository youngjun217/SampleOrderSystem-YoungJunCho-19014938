import os

from controller.order_controller import OrderController
from controller.production_controller import ProductionController
from controller.sample_controller import SampleController

LINE = "=" * 62


class MonitorView:
    def __init__(
        self,
        sample_ctrl: SampleController,
        order_ctrl: OrderController,
        prod_ctrl: ProductionController,
    ):
        self._sample_ctrl = sample_ctrl
        self._order_ctrl = order_ctrl
        self._prod_ctrl = prod_ctrl

    def _clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def run(self) -> None:
        while True:
            self._clear()
            print(LINE)
            print("                   모니터링")
            print(LINE)
            print("   1.  주문 상태별 현황")
            print("   2.  시료별 재고 현황")
            print("   0.  메인으로")
            print(LINE)
            choice = input("   선택 > ").strip()

            if choice == "0":
                break
            else:
                input("   준비 중입니다. Enter 를 누르세요.")
