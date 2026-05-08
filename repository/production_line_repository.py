from typing import List, Optional

from model.production_line import ProductionLine, LineStatus
from repository.base_repository import BaseRepository


class ProductionLineRepository(BaseRepository[ProductionLine]):
    def __init__(self, db_path: str):
        super().__init__(db_path, ProductionLine.from_dict)

    def find_idle(self) -> Optional[ProductionLine]:
        return next((l for l in self.find_all() if l.status == LineStatus.IDLE), None)

    def find_running(self) -> List[ProductionLine]:
        return [l for l in self.find_all() if l.status == LineStatus.RUNNING]
