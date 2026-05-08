import uuid
from datetime import datetime
from typing import List, Optional

from model.sample import Sample
from repository.sample_repository import SampleRepository


class SampleController:
    def __init__(self, repo: SampleRepository):
        self._repo = repo

    def register(self, name: str, spec: str, stock_quantity: int = 0) -> Sample:
        sample = Sample(
            id=str(uuid.uuid4())[:8],
            name=name,
            spec=spec,
            stock_quantity=stock_quantity,
        )
        return self._repo.save(sample)

    def get_all(self) -> List[Sample]:
        return self._repo.find_all()

    def get_by_id(self, sample_id: str) -> Optional[Sample]:
        return self._repo.find_by_id(sample_id)

    def search_by_name(self, keyword: str) -> List[Sample]:
        return self._repo.find_by_name(keyword)

    def adjust_stock(self, sample_id: str, delta: int) -> Optional[Sample]:
        sample = self._repo.find_by_id(sample_id)
        if not sample:
            return None
        sample.stock_quantity += delta
        sample.updated_at = datetime.now().isoformat()
        return self._repo.update(sample)

    def summary(self) -> dict:
        samples = self._repo.find_all()
        return {
            "total_types": len(samples),
            "total_stock": sum(s.stock_quantity for s in samples),
        }
