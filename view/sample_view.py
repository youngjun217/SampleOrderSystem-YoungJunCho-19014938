import os
from typing import List

from controller.sample_controller import SampleController
from model.sample import Sample
from view.utils import ljust as _ljust, rjust as _rjust


# 열 표시 너비 (display width 기준)
_W_ID    = 12
_W_NAME  = 22
_W_TIME  =  9   # right
_W_YIELD =  7   # right
_W_STOCK =  6   # right
_SEP_LEN = _W_ID + 1 + _W_NAME + 1 + _W_TIME + 1 + _W_YIELD + 1 + _W_STOCK  # 60


class SampleView:
    def __init__(self, ctrl: SampleController):
        self._ctrl = ctrl

    def _clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def run(self) -> None:
        while True:
            self._clear()
            print(LINE)
            print("                     시료 관리")
            print(LINE)
            print("   1.  시료 등록")
            print("   2.  시료 조회  (전체 목록 + 재고)")
            print("   3.  시료 검색  (ID / 이름)")
            print("   0.  메인으로")
            print(LINE)
            choice = input("   선택 > ").strip()

            if choice == "1":
                self._register()
            elif choice == "2":
                self._list_all()
            elif choice == "3":
                self._search()
            elif choice == "0":
                break
            else:
                input("   잘못된 선택입니다. Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _register(self) -> None:
        self._clear()
        print(LINE)
        print("   시료 등록")
        print(LINE)

        sample_id = input("   시료 ID         : ").strip()
        if not sample_id:
            input("   시료 ID는 필수입니다. Enter 로 돌아갑니다.")
            return

        name = input("   이름             : ").strip()
        if not name:
            input("   이름은 필수입니다. Enter 로 돌아갑니다.")
            return

        try:
            avg_time = float(input("   평균 생산시간 (h) : ").strip())
        except ValueError:
            input("   숫자를 입력해야 합니다. Enter 로 돌아갑니다.")
            return

        try:
            yield_rate = float(input("   수율 (0.0~1.0)   : ").strip())
        except ValueError:
            input("   숫자를 입력해야 합니다. Enter 로 돌아갑니다.")
            return

        stock_str = input("   초기 재고 (개)   : ").strip()
        stock = int(stock_str) if stock_str.isdigit() else 0

        sample, err = self._ctrl.register(sample_id, name, avg_time, yield_rate, stock)
        print()
        if err:
            print(f"   [오류] {err}")
        else:
            print(f"   [등록 완료]")
            print(f"   시료 ID  : {sample.id}")
            print(f"   이름     : {sample.name}")
            print(f"   생산시간 : {sample.avg_production_time}h")
            print(f"   수율     : {sample.yield_rate * 100:.1f}%")
            print(f"   재고     : {sample.stock_quantity}개")
        input("\n   Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _list_all(self) -> None:
        self._clear()
        print(LINE)
        print("   시료 조회  (전체 목록)")
        print(LINE)
        self._print_table(self._ctrl.get_all())
        input("\n   Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _search(self) -> None:
        self._clear()
        print(LINE)
        print("   시료 검색")
        print(LINE)
        keyword = input("   검색어 (ID 또는 이름) : ").strip()
        if not keyword:
            input("   검색어를 입력해야 합니다. Enter 로 돌아갑니다.")
            return
        results = self._ctrl.search(keyword)
        print()
        self._print_table(results)
        input("\n   Enter 를 누르세요.")

    # ------------------------------------------------------------------
    def _print_table(self, samples: List[Sample]) -> None:
        if not samples:
            print("   검색 결과가 없습니다.")
            return

        header = (
            "   "
            + _ljust("시료ID",   _W_ID)   + " "
            + _ljust("이름",     _W_NAME)  + " "
            + _rjust("생산시간", _W_TIME)  + " "
            + _rjust("수율",     _W_YIELD) + " "
            + _rjust("재고",     _W_STOCK)
        )
        print(header)
        print("   " + "-" * _SEP_LEN)

        for s in samples:
            time_str  = f"{s.avg_production_time:.1f}h"
            yield_str = f"{s.yield_rate * 100:.1f}%"
            stock_str = f"{s.stock_quantity}개"
            row = (
                "   "
                + _ljust(s.id,   _W_ID)   + " "
                + _ljust(s.name, _W_NAME)  + " "
                + _rjust(time_str,  _W_TIME)  + " "
                + _rjust(yield_str, _W_YIELD) + " "
                + _rjust(stock_str, _W_STOCK)
            )
            print(row)
