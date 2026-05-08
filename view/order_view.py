import os
from typing import List

from controller.order_controller import OrderController
from controller.production_controller import ProductionController
from controller.sample_controller import SampleController
from model.order import Order, OrderStatus
from view.utils import ljust, rjust
from view.theme import (
    section_line, menu_num, bold, muted, success, warn, danger,
    info, status_c, c, BOLD, GRAY,
)

from view.theme import TABLE as W   # section-line width (= TABLE = 78)

# 주문 목록 열 너비 — SID 제거, 합계 73 + 구분자 5 = 78 (TABLE 기준)
_W_ID     =  8
_W_CUST   = 20
_W_SNAME  = 20
_W_QTY    =  5
_W_STATUS = 10
_W_DATE   = 10
_SEP_LEN  = _W_ID + 1 + _W_CUST + 1 + _W_SNAME + 1 + _W_QTY + 1 + _W_STATUS + 1 + _W_DATE  # = 78


class OrderView:
    def __init__(
        self,
        order_ctrl: OrderController,
        sample_ctrl: SampleController,
        prod_ctrl: ProductionController,
    ):
        self._order_ctrl  = order_ctrl
        self._sample_ctrl = sample_ctrl
        self._prod_ctrl   = prod_ctrl

    def _clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def _header(self, label: str) -> None:
        print()
        print("  " + section_line(label, W))
        print()

    def run(self) -> None:
        while True:
            self._clear()
            print()
            print("  " + section_line("주문  (접수 / 승인 / 거절)", W))
            print()
            print(f"  {menu_num('1')}  주문 접수      "
                  f"{muted('새 주문 등록')}  →  {status_c('RESERVED')}")
            print(f"  {menu_num('2')}  주문 승인      "
                  f"{muted('RESERVED')}  →  {status_c('CONFIRMED')} / {status_c('PRODUCING')}")
            print(f"  {menu_num('3')}  주문 거절      "
                  f"{muted('RESERVED')}  →  {status_c('REJECTED')}")
            print(f"  {menu_num('4')}  주문 목록 조회")
            print(f"  {menu_num('0')}  메인으로")
            print()

            choice = input(f"  {bold('선택')} {muted('▶')} ").strip()

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
                input(f"  {warn('잘못된 선택입니다.')}  Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _reserve(self) -> None:
        self._clear()
        self._header("주문 접수")

        samples = self._sample_ctrl.get_all()
        if not samples:
            print(f"  {warn('등록된 시료가 없습니다. 시료를 먼저 등록해 주세요.')}")
            input(f"\n  {muted('Enter 를 누르세요.')}")
            return

        print(f"  {bold('[ 등록 시료 목록 ]')}")
        print("  " + ljust(bold("시료ID"), 12) + " " +
              ljust(bold("이름"), 20) + " " + rjust(bold("재고"), 5))
        print("  " + muted("─" * 40))
        for s in samples:
            stock_col = (success if s.stock_quantity > 0 else danger)(f"{s.stock_quantity}개")
            print("  " + ljust(info(s.id), 12) + " " +
                  ljust(s.name, 20) + " " + rjust(stock_col, 5))
        print()

        sample_id = input(f"  {info('시료 ID')}   : ").strip()
        if not sample_id:
            input(f"  {warn('시료 ID를 입력해야 합니다.')}  Enter 로 돌아갑니다.")
            return

        customer_name = input(f"  {info('고객명')}    : ").strip()
        if not customer_name:
            input(f"  {warn('고객명을 입력해야 합니다.')}  Enter 로 돌아갑니다.")
            return

        qty_str = input(f"  {info('주문 수량')} : ").strip()
        if not qty_str.isdigit() or int(qty_str) <= 0:
            input(f"  {warn('수량은 1 이상의 숫자여야 합니다.')}  Enter 로 돌아갑니다.")
            return
        quantity = int(qty_str)

        order, err = self._order_ctrl.create(customer_name, sample_id, quantity)
        print()
        if err:
            print(f"  {danger('[ 오류 ]')}  {err}")
        else:
            print(f"  {success('[ 접수 완료 ]')}")
            print(f"  주문 ID  : {bold(order.id)}")
            print(f"  고객명   : {order.customer_name}")
            print(f"  시료     : {order.sample_name}  {muted('(' + order.sample_id + ')')}")
            print(f"  수량     : {order.quantity}개")
            print(f"  상태     : {status_c(order.status.value)}")
            print(f"  접수일   : {muted(order.created_at[:19])}")
        input(f"\n  {muted('Enter 를 누르세요.')}")

    # ------------------------------------------------------------------
    def _approve(self) -> None:
        self._clear()
        self._header("주문 승인")

        reserved = self._order_ctrl.get_by_status(OrderStatus.RESERVED)
        if not reserved:
            print(f"  {muted('승인 대기 주문(RESERVED)이 없습니다.')}")
            input(f"\n  {muted('Enter 를 누르세요.')}")
            return

        self._print_table(reserved)
        print()

        order_id = input(f"  {info('승인할 주문 ID')} : ").strip()
        if not order_id:
            input(f"  {warn('주문 ID를 입력해야 합니다.')}  Enter 로 돌아갑니다.")
            return

        order = self._order_ctrl.get_by_id(order_id)
        if not order or order.status != OrderStatus.RESERVED:
            print(f"\n  {danger('RESERVED 상태의 주문을 찾을 수 없습니다.')}")
            input(f"  {muted('Enter 를 누르세요.')}")
            return

        sample = self._sample_ctrl.get_by_id(order.sample_id)
        stock = sample.stock_quantity if sample else 0
        shortage = stock < order.quantity

        print()
        print(f"  {bold('[ 재고 확인 ]')}  {order.sample_name}")
        stock_str = (danger if stock == 0 else warn if shortage else success)(f"{stock}개")
        verdict   = warn("재고 부족 → 생산라인 배정") if shortage else success("재고 충분 → 즉시 CONFIRMED")
        print(f"  현재 재고: {stock_str}   주문 수량: {bold(str(order.quantity) + '개')}   {verdict}")

        confirm = input(f"\n  {bold('승인하시겠습니까?')}  {muted('(y/n)')} : ").strip().lower()
        if confirm != "y":
            print(f"  {muted('취소되었습니다.')}")
            input(f"  {muted('Enter 를 누르세요.')}")
            return

        result = self._order_ctrl.approve(order_id)
        print()
        if not result:
            print(f"  {danger('처리에 실패했습니다.')}")
        elif result.status == OrderStatus.CONFIRMED:
            print(f"  {success('[ 승인 완료 ]')}  재고 차감 → {status_c('CONFIRMED')}")
            print(f"  주문 ID  : {bold(result.id)}")
            print(f"  차감 후 재고 : {success(str(stock - order.quantity) + '개')}")
        else:
            production = self._prod_ctrl.assign_line(order_id)
            print(f"  {success('[ 승인 완료 ]')}  생산라인 배정 → {status_c('PRODUCING')}")
            print(f"  주문 ID  : {bold(result.id)}")
            if production and production.line_id:
                lines = self._prod_ctrl.get_lines()
                line  = next((l for l in lines if l.id == production.line_id), None)
                print(f"  배정 라인 : {info(line.name if line else production.line_id)}")
                print(f"  생산 ID   : {muted(production.id)}")
            else:
                print(f"  {warn('유휴 생산라인 없음 → 대기 큐에 등록')}")

        input(f"\n  {muted('Enter 를 누르세요.')}")

    # ------------------------------------------------------------------
    def _reject(self) -> None:
        self._clear()
        self._header("주문 거절")

        reserved = self._order_ctrl.get_by_status(OrderStatus.RESERVED)
        if not reserved:
            print(f"  {muted('거절 대기 주문(RESERVED)이 없습니다.')}")
            input(f"\n  {muted('Enter 를 누르세요.')}")
            return

        self._print_table(reserved)
        print()

        order_id = input(f"  {info('거절할 주문 ID')} : ").strip()
        if not order_id:
            input(f"  {warn('주문 ID를 입력해야 합니다.')}  Enter 로 돌아갑니다.")
            return

        reason = input(f"  {info('거절 사유')}      : ").strip()
        if not reason:
            input(f"  {warn('거절 사유를 입력해야 합니다.')}  Enter 로 돌아갑니다.")
            return

        result = self._order_ctrl.reject(order_id, reason)
        print()
        if not result:
            print(f"  {danger('RESERVED 상태의 주문을 찾을 수 없습니다.')}")
        else:
            print(f"  {success('[ 거절 완료 ]')}")
            print(f"  주문 ID : {bold(result.id)}")
            print(f"  상태    : {status_c(result.status.value)}")
            print(f"  사유    : {warn(result.reject_reason)}")

        input(f"\n  {muted('Enter 를 누르세요.')}")

    # ------------------------------------------------------------------
    def _list_orders(self) -> None:
        self._clear()
        self._header("주문 목록")
        orders = self._order_ctrl.get_all()
        self._print_table(orders)
        input(f"\n  {muted('Enter 를 누르세요.')}")

    # ------------------------------------------------------------------
    def _print_table(self, orders: List[Order]) -> None:
        if not orders:
            print(f"  {muted('주문 내역이 없습니다.')}")
            return

        header = (
            "  " +
            ljust(bold("주문ID"),  _W_ID)    + " " +
            ljust(bold("고객명"),  _W_CUST)  + " " +
            ljust(bold("시료명"),  _W_SNAME) + " " +
            rjust(bold("수량"),    _W_QTY)   + " " +
            ljust(bold("상태"),    _W_STATUS) + " " +
            ljust(bold("접수일"),  _W_DATE)
        )
        print(header)
        print("  " + muted("─" * _SEP_LEN))

        for o in sorted(orders, key=lambda x: x.created_at, reverse=True):
            row = (
                "  " +
                ljust(info(o.id),               _W_ID)    + " " +
                ljust(o.customer_name,           _W_CUST)  + " " +
                ljust(o.sample_name,             _W_SNAME) + " " +
                rjust(f"{o.quantity}개",         _W_QTY)   + " " +
                ljust(status_c(o.status.value),  _W_STATUS) + " " +
                ljust(muted(o.created_at[:10]),  _W_DATE)
            )
            print(row)
