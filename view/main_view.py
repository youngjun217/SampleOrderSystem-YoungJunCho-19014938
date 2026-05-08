import os

from controller.order_controller import OrderController
from controller.production_controller import ProductionController
from controller.sample_controller import SampleController
from view.sample_view import SampleView
from view.order_view import OrderView
from view.monitor_view import MonitorView
from view.release_view import ReleaseView
from view.production_line_view import ProductionLineView
from view.theme import (
    box_top, box_mid, box_bot, box_line, menu_num,
    title, sub, bold, muted, success, warn, danger, info, status_c,
    c, BWHITE, GRAY, BOLD,
)


class MainView:
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

    def _build_summary(self):
        return self._sample_ctrl.summary(), self._order_ctrl.count_by_status()

    def _display(self) -> None:
        self._clear()
        smry, cnt = self._build_summary()

        print(box_top())
        print(box_line(title("  S Semi  반도체 시료 생산주문관리 시스템")))
        print(box_mid())

        # ── 시료 현황 ──────────────────────────────────────────
        line = (bold("[ 시료 현황 ]") + "   " +
                "등록  " + success(f"{smry['total_types']}종") +
                "   |   총 재고  " + success(f"{smry['total_stock']}개"))
        print(box_line(line))
        print(box_mid())

        # ── 주문 현황 ──────────────────────────────────────────
        print(box_line(bold("[ 주문 현황 ]")))
        print(box_line())

        def _order_row(s1, s2):
            c1 = cnt.get(s1, 0)
            c2 = cnt.get(s2, 0) if s2 else None
            left  = f"  {status_c(s1):<0}  {bold(str(c1) + '건')}"
            right = (f"    {status_c(s2):<0}  {bold(str(c2) + '건')}"
                     if s2 is not None else "")
            return box_line(left + right)

        print(_order_row("RESERVED",  "PRODUCING"))
        print(_order_row("CONFIRMED", "RELEASE"))
        r_cnt = cnt.get("REJECTED", 0)
        print(box_line(f"  {status_c('REJECTED')}  {bold(str(r_cnt) + '건')}"))
        print(box_mid())

        # ── 메뉴 ───────────────────────────────────────────────
        print(box_line())
        print(box_line(
            f"  {menu_num('1')}  시료 관리      "
            f"{menu_num('2')}  주문           "
            f"{menu_num('3')}  모니터링"
        ))
        print(box_line(
            f"  {menu_num('4')}  출고 처리      "
            f"{menu_num('5')}  생산 라인      "
            f"{menu_num('0')}  종료"
        ))
        print(box_line())
        print(box_bot())

    def run(self) -> None:
        while True:
            self._display()
            choice = input(f"\n  {c('선택', BOLD)} {c('▶', GRAY)} ").strip()

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
                print(f"\n  {muted('시스템을 종료합니다.')}\n")
                break
            else:
                input(f"  {warn('잘못된 선택입니다.')}  Enter 를 누르세요.")
