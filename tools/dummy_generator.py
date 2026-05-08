import os
import sys
import random
import uuid
import argparse
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository
from repository.production_line_repository import ProductionLineRepository
from repository.production_repository import ProductionRepository
from model.sample import Sample
from model.order import Order, OrderStatus
from model.production import Production, ProductionStatus

DATA_DIR = os.path.join(BASE_DIR, "data")

SAMPLE_SPECS = [
    ("GaN-001", "GaN 기반 전력소자 200mm"),
    ("SiC-010", "SiC 쇼트키 다이오드 150mm"),
    ("Si-CMOS", "표준 Si CMOS 300mm"),
    ("InP-RF",  "InP 기반 RF 소자 100mm"),
    ("GaAs-HBT","GaAs HBT 에피 150mm"),
]

CUSTOMERS = ["KAIST 반도체연구소", "서울대 나노팹", "삼성전기 R&D", "팹리스코어", "SK하이닉스 연구소"]

STATUSES = [
    OrderStatus.RESERVED, OrderStatus.PRODUCING,
    OrderStatus.CONFIRMED, OrderStatus.RELEASE, OrderStatus.REJECTED,
]
STATUS_WEIGHTS = [0.25, 0.20, 0.20, 0.25, 0.10]


def _rand_date(days_back: int = 30) -> str:
    delta = timedelta(days=random.randint(0, days_back), hours=random.randint(0, 23))
    return (datetime.now() - delta).isoformat()


def _rand_due(days_ahead: int = 60) -> str:
    delta = timedelta(days=random.randint(7, days_ahead))
    return (datetime.now() + delta).strftime("%Y-%m-%d")


def generate(
    sample_count: int = 5,
    order_count: int = 15,
    reset: bool = False,
) -> None:
    sample_repo = SampleRepository(os.path.join(DATA_DIR, "samples.json"))
    order_repo  = OrderRepository(os.path.join(DATA_DIR, "orders.json"))
    line_repo   = ProductionLineRepository(os.path.join(DATA_DIR, "production_lines.json"))
    prod_repo   = ProductionRepository(os.path.join(DATA_DIR, "productions.json"))

    if reset:
        for path in [
            os.path.join(DATA_DIR, "samples.json"),
            os.path.join(DATA_DIR, "orders.json"),
            os.path.join(DATA_DIR, "productions.json"),
        ]:
            import json
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f)
        print("  [초기화] samples / orders / productions 초기화 완료")

    # 시료 생성
    specs = random.sample(SAMPLE_SPECS, min(sample_count, len(SAMPLE_SPECS)))
    samples = []
    for name, spec in specs:
        s = Sample(
            id=str(uuid.uuid4())[:8],
            name=name,
            spec=spec,
            stock_quantity=random.randint(0, 20),
        )
        sample_repo.save(s)
        samples.append(s)
    print(f"  [시료] {len(samples)}종 생성")

    # 주문 생성
    orders = []
    for _ in range(order_count):
        sample = random.choice(samples)
        status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
        o = Order(
            id=str(uuid.uuid4())[:8],
            customer_name=random.choice(CUSTOMERS),
            sample_id=sample.id,
            sample_name=sample.name,
            quantity=random.randint(1, 10),
            due_date=_rand_due(),
            status=status,
            reject_reason="납기 불가" if status == OrderStatus.REJECTED else "",
            created_at=_rand_date(),
        )
        order_repo.save(o)
        orders.append(o)
    print(f"  [주문] {len(orders)}건 생성")

    # PRODUCING 주문에 생산 이력 연결
    lines = line_repo.find_all()
    line_idx = 0
    for o in orders:
        if o.status == OrderStatus.PRODUCING:
            sample = next((s for s in samples if s.id == o.sample_id), None)
            assigned_line = lines[line_idx % len(lines)] if lines else None
            p = Production(
                id=str(uuid.uuid4())[:8],
                line_id=assigned_line.id if assigned_line else "",
                order_id=o.id,
                sample_id=o.sample_id,
                sample_name=o.sample_name,
                quantity=o.quantity,
                status=ProductionStatus.RUNNING,
                started_at=_rand_date(7),
            )
            prod_repo.save(p)
            if assigned_line:
                from model.production_line import LineStatus
                assigned_line.status = LineStatus.RUNNING
                assigned_line.current_order_id = o.id
                line_repo.update(assigned_line)
            line_idx += 1
    producing_count = sum(1 for o in orders if o.status == OrderStatus.PRODUCING)
    print(f"  [생산] {producing_count}건 생산 이력 연결")
    print("\n  더미 데이터 생성 완료.")


if __name__ == "__main__":
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="S Semi 더미 데이터 생성기")
    parser.add_argument("--samples", type=int, default=5, help="생성할 시료 종류 수 (기본: 5)")
    parser.add_argument("--orders",  type=int, default=15, help="생성할 주문 수 (기본: 15)")
    parser.add_argument("--reset",   action="store_true",  help="생성 전 데이터 초기화")
    args = parser.parse_args()

    print("=" * 50)
    print("  S Semi 더미 데이터 생성기")
    print("=" * 50)
    generate(sample_count=args.samples, order_count=args.orders, reset=args.reset)
