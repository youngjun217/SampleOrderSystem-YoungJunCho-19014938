import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository
from repository.production_line_repository import ProductionLineRepository
from controller.sample_controller import SampleController
from controller.order_controller import OrderController

sample_repo = SampleRepository("data/samples.json")
order_repo  = OrderRepository("data/orders.json")
line_repo   = ProductionLineRepository("data/production_lines.json")

sample_ctrl = SampleController(sample_repo)
order_ctrl  = OrderController(order_repo, sample_repo)

sample_ctrl.register("GaN-001", "질화갈륨 전력소자",  24.0, 0.92, 5)
sample_ctrl.register("SiC-010", "SiC 쇼트키 다이오드", 36.0, 0.88, 0)
sample_ctrl.register("Si-CMOS", "표준 Si CMOS",        12.0, 0.95, 12)

smry   = sample_ctrl.summary()
counts = order_ctrl.count_by_status()

print("=" * 60)
print("  [시료 현황]")
print(f"    등록 시료 : {smry['total_types']}종  |  총 재고 : {smry['total_stock']}개")
print()
print("  [주문 현황]")
for k, v in counts.items():
    print(f"    {k:<12}: {v}건")
print()
print("  [시료 목록]")
print(f"  {'시료ID':<12} {'이름':<20} {'생산시간':>8} {'수율':>7} {'재고':>5}")
print("  " + "-" * 56)
for s in sample_ctrl.get_all():
    print(f"  {s.id:<12} {s.name:<20} {s.avg_production_time:>7.1f}h {s.yield_rate*100:>6.1f}% {s.stock_quantity:>4}개")
print()
print("  [검색: 'SiC']")
for s in sample_ctrl.search("SiC"):
    print(f"  -> [{s.id}] {s.name}")
print()
print("  [생산라인]")
for line in line_repo.find_all():
    print(f"  {line.name}: {line.status.value}")
print("=" * 60)
print("검증 완료")
