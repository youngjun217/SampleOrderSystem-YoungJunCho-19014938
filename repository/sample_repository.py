from typing import List

from model.sample import Sample
from repository.base_repository import BaseRepository


class SampleRepository(BaseRepository[Sample]):
    def __init__(self, db_path: str):
        super().__init__(db_path, Sample.from_dict)

    def find_by_name(self, keyword: str) -> List[Sample]:
        return [s for s in self.find_all() if keyword.lower() in s.name.lower()]

    def total_stock(self) -> int:
        return sum(s.stock_quantity for s in self.find_all())
