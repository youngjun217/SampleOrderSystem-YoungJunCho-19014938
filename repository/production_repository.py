from typing import List

from model.production import Production, ProductionStatus
from repository.base_repository import BaseRepository


class ProductionRepository(BaseRepository[Production]):
    def __init__(self, db_path: str):
        super().__init__(db_path, Production.from_dict)

    def find_by_status(self, status: ProductionStatus) -> List[Production]:
        return [p for p in self.find_all() if p.status == status]

    def find_by_order_id(self, order_id: str) -> List[Production]:
        return [p for p in self.find_all() if p.order_id == order_id]
