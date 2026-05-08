import os
from datetime import datetime, timedelta
from typing import List, Optional

from controller.order_controller import OrderController
from controller.production_controller import ProductionController
from model.production import Production, ProductionStatus
from model.production_line import LineStatus
from view.utils import ljust, rjust
from view.theme import (
    TABLE as W, section_line, menu_num,
    bold, muted, warn, success, danger, info,
    status_c, c, BOLD,
)


def _fmt_time(hours: float) -> str:
    h = int(hours)
    m = int((hours - h) * 60)
    return f"{h}h {m:02d}m"


def _eta(started_at: str, total_time: float) -> str:
    if not started_at:
        return "-"
    try:
        started = datetime.fromisoformat(started_at)
        eta     = started + timedelta(hours=total_time)
        now     = datetime.now()
        if eta < now:
            return success("완료 예정 초과")
        diff = eta - now
        h, rem = divmod(int(diff.total_seconds()), 3600)
        m = rem // 60
        return info(f"약 {h}h {m:02d}m 후")
    except Exception:
        return "-"


class ProductionLineView:
    def __init__(self, prod_ctrl: ProductionController, order_ctrl: OrderController):
        self._prod_ctrl  = prod_ctrl
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
            # 라인 요약
            lines   = self._prod_ctrl.get_lines()
            running = self._prod_ctrl.get_running()
            waiting = self._prod_ctrl.get_waiting()
            idle    = sum(1 for l in lines if l.status == LineStatus.IDLE)

            print()
            print("  " + section_line("생산 라인"))
            print()
            print(f"  총 라인: {bold(str(len(lines)) + '개')}  "
                  f"가동: {status_c('RUNNING') if running else muted('0')}  {bold(str(len(running)) + '개')}  "
                  f"유휴: {muted(str(idle) + '개')}  "
                  f"대기: {warn(str(len(waiting)) + '건') if waiting else muted('0건')}")
            print()
            print(f"  {menu_num('1')}  생산 현황    {muted('현재 가동 중인 생산 정보')}")
            print(f"  {menu_num('2')}  대기 큐      {muted('FIFO 스케줄링 대기 목록')}")
            print(f"  {menu_num('3')}  생산 완료 처리  {muted('PRODUCING → CONFIRMED')}")
            print(f"  {menu_num('0')}  메인으로")
            print()

            choice = input(f"  {bold('선택')} {muted('▶')} ").strip()

            if choice == "1":
                self._production_status()
            elif choice == "2":
                self._waiting_queue()
            elif choice == "3":
                self._complete_production()
            elif choice == "0":
                break
            else:
                input(f"  {warn('잘못된 선택입니다.')}  Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _production_status(self) -> None:
        self._clear()
        self._header("생산 현황  (RUNNING)")

        running = self._prod_ctrl.get_running()
        if not running:
            print(f"  {muted('현재 가동 중인 생산이 없습니다.')}")
            input(f"\n  {muted('Enter 를 누르세요.')}")
            return

        lines    = {l.id: l for l in self._prod_ctrl.get_lines()}
        orders   = {o.id: o for o in self._order_ctrl.get_all()}

        for prod in running:
            line  = lines.get(prod.line_id)
            order = orders.get(prod.order_id)
            print(f"  {bold('─' * 76)}")
            print(f"  {bold('생산 ID')}  {info(prod.id)}"
                  f"    {bold('라인')}  {info(line.name if line else prod.line_id)}")
            print()

            # 주문 정보
            if order:
                print(f"  {bold('[ 주문 정보 ]')}")
                print(f"    주문 ID    : {info(order.id)}")
                print(f"    고객명     : {order.customer_name}")
                print(f"    시료       : {order.sample_name}  {muted('(' + order.sample_id + ')')}")
                print(f"    주문 수량  : {bold(str(order.quantity) + '개')}")
                print()

            # 생산 정보
            print(f"  {bold('[ 생산 정보 ]')}")
            print(f"    부족분       : {warn(str(prod.shortage) + '개')}")
            print(f"    실 생산량    : {bold(str(prod.actual_quantity) + '개')}"
                  f"  {muted('(수율·오차 반영 = ceil(부족분 / (수율×0.9)))')}")
            print(f"    총 생산시간  : {info(_fmt_time(prod.total_time))}")
            print(f"    착수 시각    : {muted(prod.started_at[:19])}")
            print(f"    완료 예정    : {_eta(prod.started_at, prod.total_time)}")
            print()

        input(f"  {muted('Enter 를 누르세요.')}")

    # ------------------------------------------------------------------
    def _waiting_queue(self) -> None:
        self._clear()
        self._header("대기 큐  (FIFO 스케줄링)")

        waiting = self._prod_ctrl.get_waiting()
        if not waiting:
            print(f"  {muted('대기 중인 생산 작업이 없습니다.')}")
            input(f"\n  {muted('Enter 를 누르세요.')}")
            return

        # 헤더 (합계 73 + 구분자 5 = 78)
        _W_RANK  =  4
        _W_PID   = 10
        _W_OID   = 10
        _W_SNAME = 20
        _W_SHORT =  8
        _W_AQTY  = 10
        _W_TIME  = 10

        print("  " +
              rjust(bold("순위"), _W_RANK)  + " " +
              ljust(bold("생산ID"), _W_PID)  + " " +
              ljust(bold("주문ID"), _W_OID)  + " " +
              ljust(bold("시료명"), _W_SNAME) + " " +
              rjust(bold("부족분"), _W_SHORT) + " " +
              rjust(bold("실생산량"), _W_AQTY) + " " +
              rjust(bold("생산시간"), _W_TIME))
        print("  " + muted("─" * (_W_RANK+1+_W_PID+1+_W_OID+1+_W_SNAME+1+_W_SHORT+1+_W_AQTY+1+_W_TIME)))

        for i, prod in enumerate(waiting, 1):
            rank_c = (success if i == 1 else warn if i == 2 else muted)(f"#{i}")
            print(
                "  " +
                rjust(rank_c,                    _W_RANK)  + " " +
                ljust(info(prod.id),             _W_PID)   + " " +
                ljust(info(prod.order_id),       _W_OID)   + " " +
                ljust(prod.sample_name,          _W_SNAME) + " " +
                rjust(f"{prod.shortage}개",      _W_SHORT) + " " +
                rjust(f"{prod.actual_quantity}개", _W_AQTY) + " " +
                rjust(_fmt_time(prod.total_time), _W_TIME)
            )

        print()
        print(f"  {muted('※ FIFO 순서로 유휴 라인이 생기면 자동 배정됩니다.')}")
        input(f"\n  {muted('Enter 를 누르세요.')}")

    # ------------------------------------------------------------------
    def _complete_production(self) -> None:
        self._clear()
        self._header("생산 완료 처리")

        running = self._prod_ctrl.get_running()
        if not running:
            print(f"  {muted('현재 가동 중인 생산이 없습니다.')}")
            input(f"\n  {muted('Enter 를 누르세요.')}")
            return

        lines = {l.id: l for l in self._prod_ctrl.get_lines()}

        # 목록 표시
        _W_PID   = 10
        _W_LINE  = 14
        _W_SNAME = 22
        _W_SHORT =  8
        _W_AQTY  = 10
        _W_TIME  = 10
        sep = _W_PID+1+_W_LINE+1+_W_SNAME+1+_W_SHORT+1+_W_AQTY+1+_W_TIME

        print("  " +
              ljust(bold("생산ID"), _W_PID)   + " " +
              ljust(bold("라인"),   _W_LINE)  + " " +
              ljust(bold("시료명"), _W_SNAME) + " " +
              rjust(bold("부족분"), _W_SHORT) + " " +
              rjust(bold("실생산량"), _W_AQTY) + " " +
              rjust(bold("생산시간"), _W_TIME))
        print("  " + muted("─" * sep))

        for prod in running:
            line = lines.get(prod.line_id)
            print(
                "  " +
                ljust(info(prod.id),             _W_PID)   + " " +
                ljust(line.name if line else "-", _W_LINE)  + " " +
                ljust(prod.sample_name,           _W_SNAME) + " " +
                rjust(f"{prod.shortage}개",       _W_SHORT) + " " +
                rjust(f"{prod.actual_quantity}개", _W_AQTY) + " " +
                rjust(_fmt_time(prod.total_time), _W_TIME)
            )

        print()
        prod_id = input(f"  {info('완료 처리할 생산 ID')} : ").strip()
        if not prod_id:
            input(f"  {warn('생산 ID를 입력해야 합니다.')}  Enter 로 돌아갑니다.")
            return

        result = self._prod_ctrl.complete(prod_id)
        print()
        if not result:
            print(f"  {danger('RUNNING 상태의 생산을 찾을 수 없습니다.')}")
        else:
            order = self._order_ctrl.get_by_id(result.order_id)
            print(f"  {success('[ 생산 완료 ]')}")
            print(f"  생산 ID   : {bold(result.id)}")
            print(f"  시료      : {result.sample_name}")
            print(f"  부족분    : {result.shortage}개 생산 완료")
            if order:
                print(f"  주문 상태 : {status_c('PRODUCING')}  →  {status_c(order.status.value)}")
            print()

            # 다음 대기 작업 배정 결과
            waiting = self._prod_ctrl.get_waiting()
            if waiting:
                next_p = waiting[0]
                print(f"  {info('[ 다음 배정 ]')}  {muted(next_p.id)}  ({next_p.sample_name})")
            else:
                print(f"  {muted('대기 큐가 비어있습니다.')}")

        input(f"\n  {muted('Enter 를 누르세요.')}")
