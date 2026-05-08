import os
from typing import List

from controller.order_controller import OrderController
from model.order import Order, OrderStatus
from view.utils import ljust, rjust
from view.theme import (
    TABLE as W, section_line, menu_num,
    bold, muted, warn, success, danger, info, status_c,
)

_W_ID    =  8
_W_CUST  = 20
_W_SNAME = 20
_W_QTY   =  5
_W_DATE  = 10
_SEP     = _W_ID + 1 + _W_CUST + 1 + _W_SNAME + 1 + _W_QTY + 1 + _W_DATE


class ReleaseView:
    def __init__(self, order_ctrl: OrderController):
        self._order_ctrl = order_ctrl

    def _clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def _header(self, label: str) -> None:
        print()
        print("  " + section_line(label))
        print()

    def run(self) -> None:
        while True:
            self._clear()
            confirmed = self._order_ctrl.get_by_status(OrderStatus.CONFIRMED)
            print()
            print("  " + section_line("출고 처리"))
            print()
            print(f"  출고 대기  {status_c('CONFIRMED')} : {bold(str(len(confirmed)) + '건')}")
            print()
            print(f"  {menu_num('1')}  출고 대기 목록 조회")
            print(f"  {menu_num('2')}  출고 실행  "
                  f"{muted('CONFIRMED')}  →  {status_c('RELEASE')}")
            print(f"  {menu_num('0')}  메인으로")
            print()

            choice = input(f"  {bold('선택')} {muted('▶')} ").strip()

            if choice == "1":
                self._list_confirmed()
            elif choice == "2":
                self._do_release()
            elif choice == "0":
                break
            else:
                input(f"  {warn('잘못된 선택입니다.')}  Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _list_confirmed(self) -> None:
        self._clear()
        self._header("출고 대기 목록  (CONFIRMED)")
        orders = self._order_ctrl.get_by_status(OrderStatus.CONFIRMED)
        if not orders:
            print(f"  {muted('출고 대기 주문이 없습니다.')}")
        else:
            self._print_table(sorted(orders, key=lambda o: o.created_at))
        input(f"\n  {muted('Enter 를 누르세요.')}")

    # ------------------------------------------------------------------
    def _do_release(self) -> None:
        self._clear()
        self._header("출고 실행")

        orders = sorted(
            self._order_ctrl.get_by_status(OrderStatus.CONFIRMED),
            key=lambda o: o.created_at,
        )
        if not orders:
            print(f"  {muted('출고 대기 주문이 없습니다.')}")
            input(f"\n  {muted('Enter 를 누르세요.')}")
            return

        self._print_table(orders)
        print()

        order_id = input(f"  {info('출고할 주문 ID')} : ").strip()
        if not order_id:
            input(f"  {warn('주문 ID를 입력해야 합니다.')}  Enter 로 돌아갑니다.")
            return

        result = self._order_ctrl.release(order_id)
        print()
        if not result:
            print(f"  {danger('CONFIRMED 상태의 주문을 찾을 수 없습니다.')}")
        else:
            print(f"  {success('[ 출고 완료 ]')}")
            print(f"  주문 ID  : {bold(result.id)}")
            print(f"  고객명   : {result.customer_name}")
            print(f"  시료     : {result.sample_name}")
            print(f"  수량     : {result.quantity}개")
            print(f"  상태     : {status_c('CONFIRMED')}  →  {status_c('RELEASE')}")

        input(f"\n  {muted('Enter 를 누르세요.')}")

    # ------------------------------------------------------------------
    def _print_table(self, orders: List[Order]) -> None:
        header = (
            "  "
            + ljust(bold("주문ID"),  _W_ID)    + " "
            + ljust(bold("고객명"),  _W_CUST)  + " "
            + ljust(bold("시료명"),  _W_SNAME) + " "
            + rjust(bold("수량"),    _W_QTY)   + " "
            + ljust(bold("접수일"),  _W_DATE)
        )
        print(header)
        print("  " + muted("─" * _SEP))
        for o in orders:
            print(
                "  "
                + ljust(info(o.id),            _W_ID)    + " "
                + ljust(o.customer_name,        _W_CUST)  + " "
                + ljust(o.sample_name,          _W_SNAME) + " "
                + rjust(f"{o.quantity}개",      _W_QTY)   + " "
                + ljust(muted(o.created_at[:10]), _W_DATE)
            )
