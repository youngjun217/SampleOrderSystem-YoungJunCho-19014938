from datetime import datetime
from typing import List, Optional

from model.sample import Sample
from repository.sample_repository import SampleRepository


class SampleController:
    def __init__(self, repo: SampleRepository):
        self._repo = repo

    def register(
        self,
        sample_id: str,
        name: str,
        avg_production_time: float,
        yield_rate: float,
        stock_quantity: int = 0,
    ) -> tuple[Optional[Sample], str]:
        if not sample_id or not name:
            return None, "시료 ID와 이름은 필수입니다."
        if self._repo.exists(sample_id):
            return None, f"이미 존재하는 시료 ID입니다: {sample_id}"
        if not (0.0 <= yield_rate <= 1.0):
            return None, "수율은 0.0 ~ 1.0 사이여야 합니다."
        if avg_production_time <= 0:
            return None, "평균 생산시간은 0보다 커야 합니다."
        sample = Sample(
            id=sample_id,
            name=name,
            avg_production_time=avg_production_time,
            yield_rate=yield_rate,
            stock_quantity=stock_quantity,
        )
        return self._repo.save(sample), ""

    def get_all(self) -> List[Sample]:
        return self._repo.find_all()

    def get_by_id(self, sample_id: str) -> Optional[Sample]:
        return self._repo.find_by_id(sample_id)

    def search(self, keyword: str) -> List[Sample]:
        return self._repo.find_by_keyword(keyword)

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
