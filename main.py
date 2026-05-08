import os
import sys

# 실행 위치와 무관하게 항상 스크립트 디렉터리 기준으로 경로를 잡는다
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository
from repository.production_line_repository import ProductionLineRepository
from repository.production_repository import ProductionRepository
from controller.sample_controller import SampleController
from controller.order_controller import OrderController
from controller.production_controller import ProductionController
from view.main_view import MainView


def main() -> None:
    data = os.path.join(BASE_DIR, "data")

    sample_repo = SampleRepository(os.path.join(data, "samples.json"))
    order_repo  = OrderRepository(os.path.join(data, "orders.json"))
    line_repo   = ProductionLineRepository(os.path.join(data, "production_lines.json"))
    prod_repo   = ProductionRepository(os.path.join(data, "productions.json"))

    sample_ctrl = SampleController(sample_repo)
    order_ctrl  = OrderController(order_repo, sample_repo)
    prod_ctrl   = ProductionController(prod_repo, line_repo, order_repo, sample_repo)

    MainView(sample_ctrl, order_ctrl, prod_ctrl).run()


if __name__ == "__main__":
    main()
