import os
from typing import List

from controller.sample_controller import SampleController
from model.sample import Sample
from view.utils import ljust as _ljust, rjust as _rjust
from view.theme import (
    section_line, menu_num, bold, muted, success, warn, danger,
    info, c, BWHITE, BOLD, GRAY, pad_r, pad_l, dw,
)

from view.theme import TABLE as W   # section-line width (= TABLE = 78)


class SampleView:
    def __init__(self, ctrl: SampleController):
        self._ctrl = ctrl

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
            print("  " + section_line("시료 관리", W))
            print()
            print(f"  {menu_num('1')}  시료 등록")
            print(f"  {menu_num('2')}  시료 조회  (전체 목록 + 재고)")
            print(f"  {menu_num('3')}  시료 검색  (ID / 이름)")
            print(f"  {menu_num('0')}  메인으로")
            print()

            choice = input(f"  {bold('선택')} {muted('▶')} ").strip()

            if choice == "1":
                self._register()
            elif choice == "2":
                self._list_all()
            elif choice == "3":
                self._search()
            elif choice == "0":
                break
            else:
                input(f"  {warn('잘못된 선택입니다.')}  Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _register(self) -> None:
        self._clear()
        self._header("시료 등록")

        sample_id = input(f"  {info('시료 ID')}         : ").strip()
        if not sample_id:
            input(f"  {warn('시료 ID를 입력해야 합니다.')}  Enter 로 돌아갑니다.")
            return

        name = input(f"  {info('이름')}             : ").strip()
        if not name:
            input(f"  {warn('이름은 필수입니다.')}  Enter 로 돌아갑니다.")
            return

        try:
            avg_time = float(input(f"  {info('평균 생산시간 (h)')} : ").strip())
        except ValueError:
            input(f"  {warn('숫자를 입력해야 합니다.')}  Enter 로 돌아갑니다.")
            return

        try:
            yield_rate = float(input(f"  {info('수율 (0.0~1.0)')}   : ").strip())
        except ValueError:
            input(f"  {warn('숫자를 입력해야 합니다.')}  Enter 로 돌아갑니다.")
            return

        stock_str = input(f"  {info('초기 재고 (개)')}   : ").strip()
        stock = int(stock_str) if stock_str.isdigit() else 0

        sample, err = self._ctrl.register(sample_id, name, avg_time, yield_rate, stock)
        print()
        if err:
            print(f"  {danger('[ 오류 ]')}  {err}")
        else:
            print(f"  {success('[ 등록 완료 ]')}")
            print(f"  시료 ID  : {bold(sample.id)}")
            print(f"  이름     : {sample.name}")
            print(f"  생산시간 : {sample.avg_production_time}h")
            print(f"  수율     : {sample.yield_rate * 100:.1f}%")
            print(f"  재고     : {sample.stock_quantity}개")
        input(f"\n  {muted('Enter 를 누르세요.')}")

    # ------------------------------------------------------------------
    def _list_all(self) -> None:
        self._clear()
        self._header("시료 조회  (전체 목록)")
        self._print_table(self._ctrl.get_all())
        input(f"\n  {muted('Enter 를 누르세요.')}")

    # ------------------------------------------------------------------
    def _search(self) -> None:
        self._clear()
        self._header("시료 검색")
        keyword = input(f"  {info('검색어')} (ID 또는 이름) : ").strip()
        if not keyword:
            input(f"  {warn('검색어를 입력해야 합니다.')}  Enter 로 돌아갑니다.")
            return
        print()
        self._print_table(self._ctrl.search(keyword))
        input(f"\n  {muted('Enter 를 누르세요.')}")

    # ------------------------------------------------------------------
    # 컬럼 합계 74 + 구분자 4 = 78 (TABLE 기준)
    _W_ID    = 12
    _W_NAME  = 28
    _W_TIME  = 12
    _W_YIELD = 10
    _W_STOCK = 12

    def _print_table(self, samples: List[Sample]) -> None:
        if not samples:
            print(f"  {muted('검색 결과가 없습니다.')}")
            return

        W_ID, W_NAME, W_TIME, W_YIELD, W_STOCK = (
            self._W_ID, self._W_NAME, self._W_TIME, self._W_YIELD, self._W_STOCK
        )
        sep = W_ID + 1 + W_NAME + 1 + W_TIME + 1 + W_YIELD + 1 + W_STOCK  # = 78

        header = (
            "  " +
            _ljust(bold("시료ID"),   W_ID)   + " " +
            _ljust(bold("이름"),     W_NAME)  + " " +
            _rjust(bold("생산시간"), W_TIME)  + " " +
            _rjust(bold("수율"),     W_YIELD) + " " +
            _rjust(bold("재고"),     W_STOCK)
        )
        print(header)
        print("  " + muted("─" * sep))

        for s in samples:
            stock_col = (success if s.stock_quantity > 0 else danger)(f"{s.stock_quantity}개")
            print(
                "  " +
                _ljust(info(s.id),   W_ID)   + " " +
                _ljust(s.name,       W_NAME)  + " " +
                _rjust(f"{s.avg_production_time:.1f}h", W_TIME) + " " +
                _rjust(f"{s.yield_rate * 100:.1f}%",   W_YIELD) + " " +
                _rjust(stock_col,    W_STOCK)
            )
