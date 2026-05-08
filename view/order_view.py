import os

from controller.order_controller import OrderController
from controller.production_controller import ProductionController
from controller.sample_controller import SampleController

LINE = "=" * 62


class OrderView:
    def __init__(
        self,
        order_ctrl: OrderController,
        sample_ctrl: SampleController,
        prod_ctrl: ProductionController,
    ):
        self._order_ctrl = order_ctrl
        self._sample_ctrl = sample_ctrl
        self._prod_ctrl = prod_ctrl

    def _clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def run(self) -> None:
        while True:
            self._clear()
            print(LINE)
            print("              주문 (접수 / 승인 / 거절)")
            print(LINE)
            print("   1.  주문 접수      (새 주문 등록)")
            print("   2.  주문 승인      (RESERVED → CONFIRMED / PRODUCING)")
            print("   3.  주문 거절      (RESERVED → REJECTED)")
            print("   4.  주문 목록 조회")
            print("   0.  메인으로")
            print(LINE)
            choice = input("   선택 > ").strip()

            if choice == "0":
                break
            else:
                input("   준비 중입니다. Enter 를 누르세요.")
