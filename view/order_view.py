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
            elif choice == "2":
                self._approve()
            elif choice == "3":
                self._reject()
            elif choice == "4":
                self._list_orders()
            elif choice == "0":
                break
            else:
                input("   잘못된 선택입니다. Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _reserve(self) -> None:
        self._clear()
        print(LINE)
        print("   주문 접수")
        print(LINE)

        samples = self._sample_ctrl.get_all()
        if not samples:
            print("   등록된 시료가 없습니다. 시료를 먼저 등록해 주세요.")
            input("\n   Enter 를 누르세요.")
            return

        print("   [등록 시료 목록]")
        print("   " + ljust("시료ID", 12) + " " + ljust("이름", 20) + " " + rjust("재고", 5))
        print("   " + "-" * 40)
        for s in samples:
            print("   " + ljust(s.id, 12) + " " + ljust(s.name, 20) + " " + rjust(f"{s.stock_quantity}개", 5))
        print()

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
    def _approve(self) -> None:
        self._clear()
        print(LINE)
        print("   주문 승인")
        print(LINE)

        reserved = self._order_ctrl.get_by_status(OrderStatus.RESERVED)
        if not reserved:
            print("   승인 대기 주문(RESERVED)이 없습니다.")
            input("\n   Enter 를 누르세요.")
            return

        self._print_table(reserved)
        print()

        order_id = input("   승인할 주문 ID : ").strip()
        if not order_id:
            input("   주문 ID를 입력해야 합니다. Enter 로 돌아갑니다.")
            return

        order = self._order_ctrl.get_by_id(order_id)
        if not order or order.status != OrderStatus.RESERVED:
            print("\n   RESERVED 상태의 주문을 찾을 수 없습니다.")
            input("   Enter 를 누르세요.")
            return

        # 재고 상황 미리 표시
        sample = self._sample_ctrl.get_by_id(order.sample_id)
        stock = sample.stock_quantity if sample else 0
        shortage = stock < order.quantity
        print()
        print(f"   [재고 확인]  {order.sample_name}")
        print(f"   현재 재고: {stock}개  |  주문 수량: {order.quantity}개  "
              f"→  {'재고 부족 → 생산라인 배정 예정' if shortage else '재고 충분 → 즉시 CONFIRMED'}")

        confirm = input("\n   이 주문을 승인하시겠습니까? (y/n) : ").strip().lower()
        if confirm != "y":
            print("   취소되었습니다.")
            input("   Enter 를 누르세요.")
            return

        result = self._order_ctrl.approve(order_id)
        print()
        if not result:
            print("   처리에 실패했습니다.")
            input("\n   Enter 를 누르세요.")
            return

        if result.status == OrderStatus.CONFIRMED:
            print(f"   [승인 완료]  재고 차감 → CONFIRMED")
            print(f"   주문 ID : {result.id}")
            print(f"   상태    : {result.status.value}")
            print(f"   차감 후 재고 : {stock - order.quantity}개")
        else:
            production = self._prod_ctrl.assign_line(order_id)
            print(f"   [승인 완료]  생산라인 배정 → PRODUCING")
            print(f"   주문 ID : {result.id}")
            print(f"   상태    : {result.status.value}")
            if production and production.line_id:
                lines = self._prod_ctrl.get_lines()
                line = next((l for l in lines if l.id == production.line_id), None)
                print(f"   배정 라인 : {line.name if line else production.line_id}")
                print(f"   생산 ID   : {production.id}")
            else:
                print(f"   유휴 생산라인 없음 → 대기 큐에 등록")

        input("\n   Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _reject(self) -> None:
        self._clear()
        print(LINE)
        print("   주문 거절")
        print(LINE)

        reserved = self._order_ctrl.get_by_status(OrderStatus.RESERVED)
        if not reserved:
            print("   거절 대기 주문(RESERVED)이 없습니다.")
            input("\n   Enter 를 누르세요.")
            return

        self._print_table(reserved)
        print()

        order_id = input("   거절할 주문 ID : ").strip()
        if not order_id:
            input("   주문 ID를 입력해야 합니다. Enter 로 돌아갑니다.")
            return

        reason = input("   거절 사유      : ").strip()
        if not reason:
            input("   거절 사유를 입력해야 합니다. Enter 로 돌아갑니다.")
            return

        result = self._order_ctrl.reject(order_id, reason)
        print()
        if not result:
            print("   RESERVED 상태의 주문을 찾을 수 없습니다.")
        else:
            print(f"   [거절 완료]")
            print(f"   주문 ID : {result.id}")
            print(f"   상태    : {result.status.value}")
            print(f"   사유    : {result.reject_reason}")

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
            + ljust("상태",    _W_STATUS) + " "
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
                + ljust(o.status.value,   _W_STATUS) + " "
                + ljust(o.created_at[:10], _W_DATE)
            )
            print(row)
