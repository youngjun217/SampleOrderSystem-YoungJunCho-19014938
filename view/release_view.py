import os

from controller.order_controller import OrderController
from view.theme import section_line, menu_num, bold, muted, warn, success, info, status_c

W = 66


class ReleaseView:
    def __init__(self, order_ctrl: OrderController):
        self._order_ctrl = order_ctrl

    def _clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def run(self) -> None:
        while True:
            self._clear()
            print()
            print("  " + section_line("출고 처리", W))
            print()
            print(f"  {menu_num('1')}  출고 대기 목록 조회  {muted('(' + status_c('CONFIRMED') + ')')}")
            print(f"  {menu_num('2')}  출고 실행            "
                  f"{muted('CONFIRMED')}  →  {status_c('RELEASE')}")
            print(f"  {menu_num('0')}  메인으로")
            print()

            choice = input(f"  {bold('선택')} {muted('▶')} ").strip()

            if choice == "0":
                break
            else:
                input(f"  {warn('준비 중입니다.')}  Enter 를 누르세요.")
