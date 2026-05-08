import os
from typing import List

from controller.order_controller import OrderController
from controller.production_controller import ProductionController
from controller.sample_controller import SampleController
from model.order import Order, OrderStatus
from view.utils import ljust, rjust

LINE = "=" * 66

# 주문 목록 열 너비 (display width 기준)
_W_ID     = 10
_W_CUST   = 14
_W_SID    = 10
_W_SNAME  = 18
_W_QTY    =  5
_W_STATUS = 12
_W_DATE   = 10
_SEP_LEN  = _W_ID + 1 + _W_CUST + 1 + _W_SID + 1 + _W_SNAME + 1 + _W_QTY + 1 + _W_STATUS + 1 + _W_DATE


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
            print("   1.  주문 접수      (새 주문 등록 → RESERVED)")
            print("   2.  주문 승인      (RESERVED → CONFIRMED / PRODUCING)")
            print("   3.  주문 거절      (RESERVED → REJECTED)")
            print("   4.  주문 목록 조회")
            print("   0.  메인으로")
            print(LINE)
            choice = input("   선택 > ").strip()

            if choice == "1":
                self._reserve()
            elif choice == "4":
                self._list_orders()
            elif choice == "0":
                break
            elif choice in ("2", "3"):
                input("   준비 중입니다. Enter 를 누르세요.")
            else:
                input("   잘못된 선택입니다. Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _reserve(self) -> None:
        self._clear()
        print(LINE)
        print("   주문 접수")
        print(LINE)

        # 등록된 시료 목록 표시
        samples = self._sample_ctrl.get_all()
        if not samples:
            print("   등록된 시료가 없습니다. 시료를 먼저 등록해 주세요.")
            input("\n   Enter 를 누르세요.")
            return

        print("   [등록 시료 목록]")
        print(f"   {'시료ID':<12} {'이름':<20} {'재고':>5}")
        print("   " + "-" * 40)
        for s in samples:
            stock_display = f"{s.stock_quantity}개"
            print("   " + ljust(s.id, 12) + " " + ljust(s.name, 20) + " " + rjust(stock_display, 5))
        print()

        # 입력
        sample_id = input("   시료 ID   : ").strip()
        if not sample_id:
            input("   시료 ID를 입력해야 합니다. Enter 로 돌아갑니다.")
            return

        customer_name = input("   고객명    : ").strip()
        if not customer_name:
            input("   고객명을 입력해야 합니다. Enter 로 돌아갑니다.")
            return

        qty_str = input("   주문 수량 : ").strip()
        if not qty_str.isdigit() or int(qty_str) <= 0:
            input("   수량은 1 이상의 숫자여야 합니다. Enter 로 돌아갑니다.")
            return
        quantity = int(qty_str)

        order, err = self._order_ctrl.create(customer_name, sample_id, quantity)
        print()
        if err:
            print(f"   [오류] {err}")
        else:
            print(f"   [접수 완료] 주문이 등록되었습니다.")
            print(f"   주문 ID  : {order.id}")
            print(f"   고객명   : {order.customer_name}")
            print(f"   시료     : {order.sample_name}  ({order.sample_id})")
            print(f"   수량     : {order.quantity}개")
            print(f"   상태     : {order.status.value}")
            print(f"   접수일   : {order.created_at[:19]}")
        input("\n   Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _list_orders(self) -> None:
        self._clear()
        print(LINE)
        print("   주문 목록")
        print(LINE)
        orders = self._order_ctrl.get_all()
        self._print_table(orders)
        input("\n   Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _print_table(self, orders: List[Order]) -> None:
        if not orders:
            print("   주문 내역이 없습니다.")
            return

        header = (
            "   "
            + ljust("주문ID",  _W_ID)    + " "
            + ljust("고객명",  _W_CUST)  + " "
            + ljust("시료ID",  _W_SID)   + " "
            + ljust("시료명",  _W_SNAME) + " "
            + rjust("수량",    _W_QTY)   + " "
            + ljust("상태",    _W_STATUS)+ " "
            + ljust("접수일",  _W_DATE)
        )
        print(header)
        print("   " + "-" * _SEP_LEN)

        for o in sorted(orders, key=lambda x: x.created_at, reverse=True):
            row = (
                "   "
                + ljust(o.id,             _W_ID)    + " "
                + ljust(o.customer_name,  _W_CUST)  + " "
                + ljust(o.sample_id,      _W_SID)   + " "
                + ljust(o.sample_name,    _W_SNAME) + " "
                + rjust(f"{o.quantity}개", _W_QTY)  + " "
                + ljust(o.status.value,   _W_STATUS)+ " "
                + ljust(o.created_at[:10], _W_DATE)
            )
            print(row)
