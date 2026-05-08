import os
from collections import defaultdict
from typing import List

from controller.order_controller import OrderController
from controller.production_controller import ProductionController
from controller.sample_controller import SampleController
from model.order import Order, OrderStatus
from view.utils import ljust, rjust

LINE = "=" * 66

# 모니터링 대상 상태 (REJECTED 제외)
ACTIVE_STATUSES = [
    OrderStatus.RESERVED,
    OrderStatus.PRODUCING,
    OrderStatus.CONFIRMED,
    OrderStatus.RELEASE,
]

# 주문 목록 열 너비
_W_OID   = 10
_W_CUST  = 20   # 최대: "KAIST 반도체연구소" = 18
_W_SNAME = 20   # 최대: "SiC 쇼트키 다이오드" = 19
_W_QTY   =  5
_W_DATE  = 10
_O_SEP   = _W_OID + 1 + _W_CUST + 1 + _W_SNAME + 1 + _W_QTY + 1 + _W_DATE

# 재고 목록 열 너비
_W_SID     = 12
_W_SNAME2  = 20
_W_STOCK   =  7
_W_DEMAND  =  9   # 대기주문 ("대기주문" = 8 display)
_W_SLABEL  =  4   # 여유/부족/고갈 (각 4 display)
_I_SEP     = _W_SID + 1 + _W_SNAME2 + 1 + _W_STOCK + 1 + _W_DEMAND + 1 + _W_SLABEL


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
            print("   1.  주문량 확인    (상태별 주문 현황, REJECTED 제외)")
            print("   2.  재고량 확인    (시료별 재고 및 여유/부족/고갈 상태)")
            print("   0.  메인으로")
            print(LINE)
            choice = input("   선택 > ").strip()

            if choice == "1":
                self._order_status()
            elif choice == "2":
                self._inventory_status()
            elif choice == "0":
                break
            else:
                input("   잘못된 선택입니다. Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _order_status(self) -> None:
        self._clear()
        print(LINE)
        print("   주문량 확인  (REJECTED 제외)")
        print(LINE)

        all_orders = self._order_ctrl.get_all()
        active = [o for o in all_orders if o.status in ACTIVE_STATUSES]

        # 요약
        counts = {s: 0 for s in ACTIVE_STATUSES}
        for o in active:
            counts[o.status] += 1

        print("   [상태별 요약]")
        for status in ACTIVE_STATUSES:
            print(f"   {ljust(status.value, 12)} : {counts[status]:>3}건")
        print()

        # 상태별 상세 목록
        for status in ACTIVE_STATUSES:
            group = [o for o in active if o.status == status]
            if not group:
                continue
            print(f"   [{status.value}]")
            self._print_order_table(group)
            print()

        input("   Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _inventory_status(self) -> None:
        self._clear()
        print(LINE)
        print("   재고량 확인")
        print(LINE)

        samples = self._sample_ctrl.get_all()
        if not samples:
            print("   등록된 시료가 없습니다.")
            input("\n   Enter 를 누르세요.")
            return

        all_orders = self._order_ctrl.get_all()

        # RESERVED 주문 기준 시료별 대기 수량 합산
        demand: defaultdict = defaultdict(int)
        for o in all_orders:
            if o.status == OrderStatus.RESERVED:
                demand[o.sample_id] += o.quantity

        # 헤더
        header = (
            "   "
            + ljust("시료ID",   _W_SID)    + " "
            + ljust("이름",     _W_SNAME2) + " "
            + rjust("재고",     _W_STOCK)  + " "
            + rjust("대기주문", _W_DEMAND) + " "
            + ljust("상태",     _W_SLABEL)
        )
        print(header)
        print("   " + "-" * _I_SEP)

        for s in samples:
            req = demand.get(s.id, 0)
            if s.stock_quantity == 0:
                label = "고갈"
            elif s.stock_quantity < req:
                label = "부족"
            else:
                label = "여유"

            row = (
                "   "
                + ljust(s.id,   _W_SID)    + " "
                + ljust(s.name, _W_SNAME2) + " "
                + rjust(f"{s.stock_quantity}개", _W_STOCK)  + " "
                + rjust(f"{req}개",              _W_DEMAND) + " "
                + ljust(label,  _W_SLABEL)
            )
            print(row)

        print()
        # 요약 (고갈·부족 건수)
        depleted = sum(1 for s in samples if s.stock_quantity == 0)
        short    = sum(1 for s in samples if 0 < s.stock_quantity < demand.get(s.id, 0))
        print(f"   고갈: {depleted}종  |  부족: {short}종  |  여유: {len(samples) - depleted - short}종")

        input("\n   Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _print_order_table(self, orders: List[Order]) -> None:
        header = (
            "   "
            + ljust("주문ID", _W_OID)   + " "
            + ljust("고객명", _W_CUST)  + " "
            + ljust("시료명", _W_SNAME) + " "
            + rjust("수량",   _W_QTY)   + " "
            + ljust("접수일", _W_DATE)
        )
        print(header)
        print("   " + "-" * _O_SEP)
        for o in sorted(orders, key=lambda x: x.created_at, reverse=True):
            row = (
                "   "
                + ljust(o.id,            _W_OID)   + " "
                + ljust(o.customer_name, _W_CUST)  + " "
                + ljust(o.sample_name,   _W_SNAME) + " "
                + rjust(f"{o.quantity}개", _W_QTY) + " "
                + ljust(o.created_at[:10], _W_DATE)
            )
            print(row)
