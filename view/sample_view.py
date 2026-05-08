import os
from typing import List

from controller.sample_controller import SampleController
from model.sample import Sample

LINE = "=" * 62


class SampleView:
    def __init__(self, ctrl: SampleController):
        self._ctrl = ctrl

    def _clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def run(self) -> None:
        while True:
            self._clear()
            print(LINE)
            print("                   시료 관리")
            print(LINE)
            print("   1.  시료 등록")
            print("   2.  시료 목록")
            print("   3.  이름 검색")
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

    def _register(self) -> None:
        self._clear()
        print(LINE)
        print("   시료 등록")
        print(LINE)
        name = input("   시료명     : ").strip()
        if not name:
            input("   시료명을 입력해야 합니다. Enter 로 돌아갑니다.")
            return
        spec = input("   규격/설명  : ").strip()
        stock_str = input("   초기 재고  : ").strip()
        stock = int(stock_str) if stock_str.isdigit() else 0
        sample = self._ctrl.register(name, spec, stock)
        print()
        print(f"   [완료] [{sample.id}] {sample.name}  재고: {sample.stock_quantity}개")
        input("   Enter 를 누르세요.")

    def _list_all(self) -> None:
        self._clear()
        print(LINE)
        print("   시료 목록")
        print(LINE)
        self._print_table(self._ctrl.get_all())
        input("\n   Enter 를 누르세요.")

    def _search(self) -> None:
        self._clear()
        print(LINE)
        print("   이름 검색")
        print(LINE)
        keyword = input("   검색어 : ").strip()
        results = self._ctrl.search_by_name(keyword)
        print()
        self._print_table(results)
        input("\n   Enter 를 누르세요.")

    def _print_table(self, samples: List[Sample]) -> None:
        if not samples:
            print("   등록된 시료가 없습니다.")
            return
        print(f"   {'ID':<10} {'시료명':<20} {'규격':<18} {'재고':>6}")
        print("   " + "-" * 58)
        for s in samples:
            print(f"   {s.id:<10} {s.name:<20} {s.spec:<18} {s.stock_quantity:>6}개")
