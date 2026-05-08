import uuid
from datetime import datetime
from typing import List, Optional

from model.order import OrderStatus
from model.production import Production, ProductionStatus
from model.production_line import ProductionLine, LineStatus
from repository.order_repository import OrderRepository
from repository.production_repository import ProductionRepository
from repository.production_line_repository import ProductionLineRepository
from repository.sample_repository import SampleRepository


class ProductionController:
    def __init__(
        self,
        prod_repo: ProductionRepository,
        line_repo: ProductionLineRepository,
        order_repo: OrderRepository,
        sample_repo: SampleRepository,
    ):
        self._prod_repo = prod_repo
        self._line_repo = line_repo
        self._order_repo = order_repo
        self._sample_repo = sample_repo

    def get_lines(self) -> List[ProductionLine]:
        return self._line_repo.find_all()

    def get_running(self) -> List[Production]:
        return self._prod_repo.find_by_status(ProductionStatus.RUNNING)

    def get_waiting(self) -> List[Production]:
        return self._prod_repo.find_by_status(ProductionStatus.WAITING)

    def assign_line(self, order_id: str) -> Optional[Production]:
        order = self._order_repo.find_by_id(order_id)
        if not order:
            return None
        idle_line = self._line_repo.find_idle()
        if idle_line:
            status = ProductionStatus.RUNNING
            started_at = datetime.now().isoformat()
            idle_line.status = LineStatus.RUNNING
            idle_line.current_order_id = order_id
            self._line_repo.update(idle_line)
        else:
            status = ProductionStatus.WAITING
            started_at = ""
        production = Production(
            id=str(uuid.uuid4())[:8],
            line_id=idle_line.id if idle_line else "",
            order_id=order_id,
            sample_id=order.sample_id,
            sample_name=order.sample_name,
            quantity=order.quantity,
            status=status,
            started_at=started_at,
        )
        return self._prod_repo.save(production)

    def complete(self, production_id: str) -> Optional[Production]:
        prod = self._prod_repo.find_by_id(production_id)
        if not prod or prod.status == ProductionStatus.DONE:
            return None
        prod.status = ProductionStatus.DONE
        prod.completed_at = datetime.now().isoformat()
        self._prod_repo.update(prod)

        sample = self._sample_repo.find_by_id(prod.sample_id)
        if sample:
            sample.stock_quantity += prod.quantity
            self._sample_repo.update(sample)

        order = self._order_repo.find_by_id(prod.order_id)
        if order:
            order.status = OrderStatus.CONFIRMED
            self._order_repo.update(order)

        if prod.line_id:
            line = self._line_repo.find_by_id(prod.line_id)
            if line:
                waiting = self._prod_repo.find_by_status(ProductionStatus.WAITING)
                if waiting:
                    next_prod = waiting[0]
                    next_prod.line_id = line.id
                    next_prod.status = ProductionStatus.RUNNING
                    next_prod.started_at = datetime.now().isoformat()
                    self._prod_repo.update(next_prod)
                    line.status = LineStatus.RUNNING
                    line.current_order_id = next_prod.order_id
                else:
                    line.status = LineStatus.IDLE
                    line.current_order_id = ""
                self._line_repo.update(line)
        return prod
