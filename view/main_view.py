import os

from controller.order_controller import OrderController
from controller.production_controller import ProductionController
from controller.sample_controller import SampleController
from view.sample_view import SampleView
from view.order_view import OrderView
from view.monitor_view import MonitorView
from view.release_view import ReleaseView
from view.production_line_view import ProductionLineView

LINE = "=" * 62


class MainView:
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

    def _build_summary(self) -> tuple:
        s = self._sample_ctrl.summary()
        c = self._order_ctrl.count_by_status()
        return s, c

    def _display(self) -> None:
        self._clear()
        sample_sum, order_counts = self._build_summary()

        print(LINE)
        print("       S Semi 반도체 시료 생산주문관리 시스템")
        print(LINE)
        print()
        print("  [시료 현황]")
        print(f"    등록 시료 : {sample_sum['total_types']:>3}종"
              f"    |    총 재고 : {sample_sum['total_stock']:>5}개")
        print()
        print("  [주문 현황]")
        print(f"    접수      (RESERVED)  : {order_counts.get('RESERVED',  0):>4}건"
              f"    생산중    (PRODUCING) : {order_counts.get('PRODUCING', 0):>4}건")
        print(f"    출고대기  (CONFIRMED) : {order_counts.get('CONFIRMED', 0):>4}건"
              f"    출고완료  (RELEASE)   : {order_counts.get('RELEASE',   0):>4}건")
        print(f"    거절      (REJECTED)  : {order_counts.get('REJECTED',  0):>4}건")
        print()
        print(LINE)
        print("   1.  시료 관리       (등록 / 목록 / 검색)")
        print("   2.  주문            (접수 / 승인 / 거절)")
        print("   3.  모니터링        (주문 상태 · 재고 현황)")
        print("   4.  출고 처리       (CONFIRMED 주문 출고)")
        print("   5.  생산 라인       (생산 현황 · 대기 큐)")
        print("   0.  종료")
        print(LINE)

    def run(self) -> None:
        while True:
            self._display()
            choice = input("   선택 > ").strip()

            if choice == "1":
                SampleView(self._sample_ctrl).run()
            elif choice == "2":
                OrderView(self._order_ctrl, self._sample_ctrl, self._prod_ctrl).run()
            elif choice == "3":
                MonitorView(self._sample_ctrl, self._order_ctrl, self._prod_ctrl).run()
            elif choice == "4":
                ReleaseView(self._order_ctrl).run()
            elif choice == "5":
                ProductionLineView(self._prod_ctrl, self._order_ctrl).run()
            elif choice == "0":
                self._clear()
                print("\n   시스템을 종료합니다.\n")
                break
            else:
                input("   잘못된 선택입니다. Enter 를 누르세요.")
