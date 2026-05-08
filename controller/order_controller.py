import uuid
from typing import Dict, List, Optional, Tuple

from model.order import Order, OrderStatus
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository


class OrderController:
    def __init__(self, order_repo: OrderRepository, sample_repo: SampleRepository):
        self._order_repo = order_repo
        self._sample_repo = sample_repo

    def create(
        self,
        customer_name: str,
        sample_id: str,
        quantity: int,
    ) -> Tuple[Optional[Order], str]:
        if not customer_name:
            return None, "고객명을 입력해야 합니다."
        if quantity <= 0:
            return None, "주문 수량은 1 이상이어야 합니다."
        sample = self._sample_repo.find_by_id(sample_id)
        if not sample:
            return None, f"등록되지 않은 시료 ID입니다: {sample_id}"
        order = Order(
            id=str(uuid.uuid4())[:8],
            customer_name=customer_name,
            sample_id=sample_id,
            sample_name=sample.name,
            quantity=quantity,
            due_date="",
        )
        return self._order_repo.save(order), ""

    def get_all(self) -> List[Order]:
        return self._order_repo.find_all()

    def get_by_id(self, order_id: str) -> Optional[Order]:
        return self._order_repo.find_by_id(order_id)

    def get_by_status(self, status: OrderStatus) -> List[Order]:
        return self._order_repo.find_by_status(status)

    def count_by_status(self) -> Dict[str, int]:
        return self._order_repo.count_by_status()

    def approve(self, order_id: str) -> Optional[Order]:
        order = self._order_repo.find_by_id(order_id)
        if not order or order.status != OrderStatus.RESERVED:
            return None
        sample = self._sample_repo.find_by_id(order.sample_id)
        if sample and sample.stock_quantity >= order.quantity:
            order.status = OrderStatus.CONFIRMED
            sample.stock_quantity -= order.quantity
            self._sample_repo.update(sample)
        else:
            order.status = OrderStatus.PRODUCING
        return self._order_repo.update(order)

    def reject(self, order_id: str, reason: str) -> Optional[Order]:
        order = self._order_repo.find_by_id(order_id)
        if not order or order.status != OrderStatus.RESERVED:
            return None
        order.status = OrderStatus.REJECTED
        order.reject_reason = reason
        return self._order_repo.update(order)

    def release(self, order_id: str) -> Optional[Order]:
        order = self._order_repo.find_by_id(order_id)
        if not order or order.status != OrderStatus.CONFIRMED:
            return None
        order.status = OrderStatus.RELEASE
        return self._order_repo.update(order)
