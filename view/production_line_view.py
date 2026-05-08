import os

from controller.order_controller import OrderController
from controller.production_controller import ProductionController
from model.production import ProductionStatus
from model.production_line import LineStatus
from view.utils import ljust, rjust

LINE = "=" * 66


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

            if choice == "1":
                self._line_status()
            elif choice == "2":
                self._waiting_queue()
            elif choice == "3":
                input("   준비 중입니다. Enter 를 누르세요.")
            elif choice == "0":
                break
            else:
                input("   잘못된 선택입니다. Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _line_status(self) -> None:
        self._clear()
        print(LINE)
        print("   생산 라인 현황")
        print(LINE)

        lines = self._prod_ctrl.get_lines()
        running = self._prod_ctrl.get_running()
        order_map = {o.id: o for o in self._order_ctrl.get_all()}

        idle_count    = sum(1 for l in lines if l.status == LineStatus.IDLE)
        running_count = sum(1 for l in lines if l.status == LineStatus.RUNNING)

        print(f"   총 라인: {len(lines)}개  |  가동 중: {running_count}개  |  유휴: {idle_count}개")
        print()

        # 라인별 상태
        prod_by_order = {p.order_id: p for p in running}

        print("   " + ljust("라인명",    14) + " " +
              ljust("상태",     6)  + " " +
              ljust("담당 주문ID", 12) + " " +
              ljust("시료명",    20) + " " +
              rjust("수량",      5))
        print("   " + "-" * 62)

        for line in lines:
            if line.status == LineStatus.IDLE:
                status_label = "유휴"
                order_id_str = "-"
                sample_str   = "-"
                qty_str      = "-"
            else:
                status_label = "가동 중"
                order_id_str = line.current_order_id
                prod = prod_by_order.get(line.current_order_id)
                if prod:
                    sample_str = prod.sample_name
                    qty_str    = f"{prod.quantity}개"
                else:
                    sample_str = "-"
                    qty_str    = "-"

            print("   " +
                  ljust(line.name,     14) + " " +
                  ljust(status_label,   6) + " " +
                  ljust(order_id_str,  12) + " " +
                  ljust(sample_str,    20) + " " +
                  rjust(qty_str,        5))

        input("\n   Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _waiting_queue(self) -> None:
        self._clear()
        print(LINE)
        print("   생산 대기 큐  (WAITING)")
        print(LINE)

        waiting = self._prod_ctrl.get_waiting()
        if not waiting:
            print("   대기 중인 생산이 없습니다.")
            input("\n   Enter 를 누르세요.")
            return

        print("   " + ljust("생산ID",  10) + " " +
              ljust("주문ID",  10)  + " " +
              ljust("시료명",  20)  + " " +
              rjust("수량",     5))
        print("   " + "-" * 50)

        for p in waiting:
            print("   " +
                  ljust(p.id,          10) + " " +
                  ljust(p.order_id,    10) + " " +
                  ljust(p.sample_name, 20) + " " +
                  rjust(f"{p.quantity}개", 5))

        input("\n   Enter 를 누르세요.")
