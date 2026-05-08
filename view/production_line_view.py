import os

from controller.order_controller import OrderController
from controller.production_controller import ProductionController

LINE = "=" * 62


class ProductionLineView:
    def __init__(self, prod_ctrl: ProductionController, order_ctrl: OrderController):
        self._prod_ctrl = prod_ctrl
        self._order_ctrl = order_ctrl

    def _clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def run(self) -> None:
        while True:
            self._clear()
            print(LINE)
            print("                   생산 라인")
            print(LINE)
            print("   1.  생산 라인 현황    (유휴 / 가동 중)")
            print("   2.  생산 대기 큐      (WAITING 목록)")
            print("   3.  생산 완료 처리")
            print("   0.  메인으로")
            print(LINE)
            choice = input("   선택 > ").strip()

            if choice == "0":
                break
            else:
                input("   준비 중입니다. Enter 를 누르세요.")
