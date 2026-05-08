from typing import Dict, List

from model.order import Order, OrderStatus
from repository.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db_path: str):
        super().__init__(db_path, Order.from_dict)

    def find_by_status(self, status: OrderStatus) -> List[Order]:
        return [o for o in self.find_all() if o.status == status]

    def count_by_status(self) -> Dict[str, int]:
        counts = {s.value: 0 for s in OrderStatus}
        for o in self.find_all():
            counts[o.status.value] += 1
        return counts
