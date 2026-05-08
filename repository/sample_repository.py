from typing import List

from model.sample import Sample
from repository.base_repository import BaseRepository


class SampleRepository(BaseRepository[Sample]):
    def __init__(self, db_path: str):
        super().__init__(db_path, Sample.from_dict)

    def exists(self, sample_id: str) -> bool:
        return any(r["id"] == sample_id for r in self._read())

    def find_by_keyword(self, keyword: str) -> List[Sample]:
        kw = keyword.lower()
        return [
            s for s in self.find_all()
            if kw in s.id.lower() or kw in s.name.lower()
        ]

    def total_stock(self) -> int:
        return sum(s.stock_quantity for s in self.find_all())
