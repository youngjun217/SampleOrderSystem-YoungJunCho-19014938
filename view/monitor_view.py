import os
from collections import defaultdict
from typing import List

from controller.order_controller import OrderController
from controller.production_controller import ProductionController
from controller.sample_controller import SampleController
from model.order import Order, OrderStatus
from view.utils import ljust, rjust
from view.theme import (
    section_line, menu_num, bold, muted, success, warn, danger,
    info, status_c, c, BOLD,
)

from view.theme import TABLE as W   # section-line width (= TABLE = 78)

ACTIVE_STATUSES = [
    OrderStatus.RESERVED,
    OrderStatus.PRODUCING,
    OrderStatus.CONFIRMED,
    OrderStatus.RELEASE,
]

# 주문 테이블 — 합계 73 + 구분자 5 = 78 (order_view와 동일)
_W_OID   =  8
_W_CUST  = 20
_W_SNAME = 20
_W_QTY   =  5
_W_DATE  = 10
_W_STATUS_O = 10
_O_SEP   = _W_OID + 1 + _W_CUST + 1 + _W_SNAME + 1 + _W_QTY + 1 + _W_STATUS_O + 1 + _W_DATE  # = 78

# 재고 테이블 — 합계 74 + 구분자 4 = 78
_W_SID    = 14
_W_SNAME2 = 26
_W_STOCK  = 10
_W_DEMAND = 12
_W_SLABEL = 12
_I_SEP    = _W_SID + 1 + _W_SNAME2 + 1 + _W_STOCK + 1 + _W_DEMAND + 1 + _W_SLABEL  # = 78

STOCK_LABEL_COLOR = {"여유": success, "부족": warn, "고갈": danger}


class MonitorView:
    def __init__(
        self,
        sample_ctrl: SampleController,
        order_ctrl: OrderController,
        prod_ctrl: ProductionController,
    ):
        self._sample_ctrl = sample_ctrl
        self._order_ctrl  = order_ctrl
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
            print("  " + section_line("모니터링", W))
            print()
            print(f"  {menu_num('1')}  주문량 확인    {muted('상태별 주문 현황, REJECTED 제외')}")
            print(f"  {menu_num('2')}  재고량 확인    {muted('시료별 재고 및 여유 / 부족 / 고갈 상태')}")
            print(f"  {menu_num('0')}  메인으로")
            print()

            choice = input(f"  {bold('선택')} {muted('▶')} ").strip()

            if choice == "1":
                self._order_status()
            elif choice == "2":
                self._inventory_status()
            elif choice == "0":
                break
            else:
                input(f"  {warn('잘못된 선택입니다.')}  Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _order_status(self) -> None:
        self._clear()
        self._header("주문량 확인  (REJECTED 제외)")

        all_orders = self._order_ctrl.get_all()
        active     = [o for o in all_orders if o.status in ACTIVE_STATUSES]
        counts     = {s: 0 for s in ACTIVE_STATUSES}
        for o in active:
            counts[o.status] += 1

        # 요약 카드
        print(f"  {bold('[ 상태별 요약 ]')}")
        for status in ACTIVE_STATUSES:
            bar_len = min(counts[status], 20)
            bar     = "■" * bar_len + muted("□" * (20 - bar_len))
            print(f"  {status_c(status.value):<0}  {bar}  {bold(str(counts[status]) + '건')}")
        print()

        # 상태별 상세 목록
        for status in ACTIVE_STATUSES:
            group = [o for o in active if o.status == status]
            if not group:
                continue
            print(f"  {bold('[ ' + status.value + ' ]')}")
            self._print_order_table(group)
            print()

        input(f"  {muted('Enter 를 누르세요.')}")

    # ------------------------------------------------------------------
    def _inventory_status(self) -> None:
        self._clear()
        self._header("재고량 확인")

        samples = self._sample_ctrl.get_all()
        if not samples:
            print(f"  {muted('등록된 시료가 없습니다.')}")
            input(f"\n  {muted('Enter 를 누르세요.')}")
            return

        all_orders = self._order_ctrl.get_all()
        demand: defaultdict = defaultdict(int)
        for o in all_orders:
            if o.status == OrderStatus.RESERVED:
                demand[o.sample_id] += o.quantity

        header = (
            "  " +
            ljust(bold("시료ID"),   _W_SID)    + " " +
            ljust(bold("이름"),     _W_SNAME2) + " " +
            rjust(bold("재고"),     _W_STOCK)  + " " +
            rjust(bold("대기주문"), _W_DEMAND) + " " +
            ljust(bold("상태"),     _W_SLABEL)
        )
        print(header)
        print("  " + muted("─" * _I_SEP))

        for s in samples:
            req = demand.get(s.id, 0)
            if s.stock_quantity == 0:
                label = "고갈"
            elif s.stock_quantity < req:
                label = "부족"
            else:
                label = "여유"

            color_fn   = STOCK_LABEL_COLOR[label]
            stock_disp = color_fn(f"{s.stock_quantity}개")

            row = (
                "  " +
                ljust(info(s.id),  _W_SID)    + " " +
                ljust(s.name,      _W_SNAME2) + " " +
                rjust(stock_disp,  _W_STOCK)  + " " +
                rjust(f"{req}개",  _W_DEMAND) + " " +
                ljust(color_fn(label), _W_SLABEL)
            )
            print(row)

        print()
        depleted = sum(1 for s in samples if s.stock_quantity == 0)
        short    = sum(1 for s in samples
                       if 0 < s.stock_quantity < demand.get(s.id, 0))
        surplus  = len(samples) - depleted - short
        print(f"  {danger('고갈')}: {depleted}종   "
              f"{warn('부족')}: {short}종   "
              f"{success('여유')}: {surplus}종")

        input(f"\n  {muted('Enter 를 누르세요.')}")

    # ------------------------------------------------------------------
    def _print_order_table(self, orders: List[Order]) -> None:
        header = (
            "  " +
            ljust(bold("주문ID"), _W_OID)      + " " +
            ljust(bold("고객명"), _W_CUST)     + " " +
            ljust(bold("시료명"), _W_SNAME)    + " " +
            rjust(bold("수량"),   _W_QTY)      + " " +
            ljust(bold("상태"),   _W_STATUS_O) + " " +
            ljust(bold("접수일"), _W_DATE)
        )
        print(header)
        print("  " + muted("─" * _O_SEP))
        for o in sorted(orders, key=lambda x: x.created_at, reverse=True):
            print(
                "  " +
                ljust(info(o.id),              _W_OID)      + " " +
                ljust(o.customer_name,          _W_CUST)     + " " +
                ljust(o.sample_name,            _W_SNAME)    + " " +
                rjust(f"{o.quantity}개",        _W_QTY)      + " " +
                ljust(status_c(o.status.value), _W_STATUS_O) + " " +
                ljust(muted(o.created_at[:10]), _W_DATE)
            )
