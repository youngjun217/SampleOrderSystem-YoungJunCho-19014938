import os

from controller.order_controller import OrderController

LINE = "=" * 62


class ReleaseView:
    def __init__(self, order_ctrl: OrderController):
        self._order_ctrl = order_ctrl

    def _clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def run(self) -> None:
        while True:
            self._clear()
            print(LINE)
            print("                   출고 처리")
            print(LINE)
            print("   1.  출고 대기 목록 조회  (CONFIRMED)")
            print("   2.  출고 실행            (CONFIRMED → RELEASE)")
            print("   0.  메인으로")
            print(LINE)
            choice = input("   선택 > ").strip()

            if choice == "0":
                break
            else:
                input("   준비 중입니다. Enter 를 누르세요.")
