import os

from controller.order_controller import OrderController
from controller.production_controller import ProductionController
from model.production_line import LineStatus
from view.utils import ljust, rjust
from view.theme import (
    section_line, menu_num, bold, muted, warn, success, danger,
    info, status_c, c, BOLD,
)

W = 66


class ProductionLineView:
    def __init__(self, prod_ctrl: ProductionController, order_ctrl: OrderController):
        self._prod_ctrl  = prod_ctrl
        self._order_ctrl = order_ctrl

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
            print("  " + section_line("생산 라인", W))
            print()
            print(f"  {menu_num('1')}  생산 라인 현황    {muted('유휴 / 가동 중')}")
            print(f"  {menu_num('2')}  생산 대기 큐      {muted('WAITING 목록')}")
            print(f"  {menu_num('3')}  생산 완료 처리")
            print(f"  {menu_num('0')}  메인으로")
            print()

            choice = input(f"  {bold('선택')} {muted('▶')} ").strip()

            if choice == "1":
                self._line_status()
            elif choice == "2":
                self._waiting_queue()
            elif choice == "3":
                input(f"  {warn('준비 중입니다.')}  Enter 를 누르세요.")
            elif choice == "0":
                break
            else:
                input(f"  {warn('잘못된 선택입니다.')}  Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _line_status(self) -> None:
        self._clear()
        self._header("생산 라인 현황")

        lines   = self._prod_ctrl.get_lines()
        running = self._prod_ctrl.get_running()

        idle_cnt    = sum(1 for l in lines if l.status == LineStatus.IDLE)
        running_cnt = sum(1 for l in lines if l.status == LineStatus.RUNNING)

        print(f"  총 라인: {bold(str(len(lines)) + '개')}   "
              f"가동 중: {status_c('RUNNING') if running_cnt else muted('0')}  {bold(str(running_cnt) + '개')}   "
              f"유휴: {muted(str(idle_cnt) + '개')}")
        print()

        prod_by_order = {p.order_id: p for p in running}

        _W_LINE   = 14
        _W_STATUS =  8
        _W_OID    = 12
        _W_SNAME  = 20
        _W_QTY    =  5

        header = (
            "  " +
            ljust(bold("라인명"),    _W_LINE)   + " " +
            ljust(bold("상태"),      _W_STATUS) + " " +
            ljust(bold("담당 주문"), _W_OID)    + " " +
            ljust(bold("시료명"),    _W_SNAME)  + " " +
            rjust(bold("수량"),      _W_QTY)
        )
        print(header)
        print("  " + muted("─" * (_W_LINE + 1 + _W_STATUS + 1 + _W_OID + 1 + _W_SNAME + 1 + _W_QTY)))

        for line in lines:
            if line.status == LineStatus.IDLE:
                status_disp = muted("유휴")
                oid_disp    = muted("-")
                sname_disp  = muted("-")
                qty_disp    = muted("-")
            else:
                status_disp = status_c("RUNNING")
                oid_disp    = info(line.current_order_id)
                prod        = prod_by_order.get(line.current_order_id)
                sname_disp  = prod.sample_name if prod else muted("-")
                qty_disp    = (f"{prod.quantity}개" if prod else muted("-"))

            print(
                "  " +
                ljust(bold(line.name), _W_LINE)   + " " +
                ljust(status_disp,     _W_STATUS) + " " +
                ljust(oid_disp,        _W_OID)    + " " +
                ljust(sname_disp,      _W_SNAME)  + " " +
                rjust(qty_disp,        _W_QTY)
            )

        input(f"\n  {muted('Enter 를 누르세요.')}")

    # ------------------------------------------------------------------
    def _waiting_queue(self) -> None:
        self._clear()
        self._header("생산 대기 큐  (WAITING)")

        waiting = self._prod_ctrl.get_waiting()
        if not waiting:
            print(f"  {muted('대기 중인 생산이 없습니다.')}")
            input(f"\n  {muted('Enter 를 누르세요.')}")
            return

        _W_PID   = 10
        _W_OID   = 10
        _W_SNAME = 20
        _W_QTY   =  5

        print("  " +
              ljust(bold("생산ID"), _W_PID)  + " " +
              ljust(bold("주문ID"), _W_OID)  + " " +
              ljust(bold("시료명"), _W_SNAME) + " " +
              rjust(bold("수량"),   _W_QTY))
        print("  " + muted("─" * (_W_PID + 1 + _W_OID + 1 + _W_SNAME + 1 + _W_QTY)))

        for p in waiting:
            print("  " +
                  ljust(muted(p.id),      _W_PID)  + " " +
                  ljust(info(p.order_id), _W_OID)  + " " +
                  ljust(p.sample_name,    _W_SNAME) + " " +
                  rjust(f"{p.quantity}개", _W_QTY))

        input(f"\n  {muted('Enter 를 누르세요.')}")
