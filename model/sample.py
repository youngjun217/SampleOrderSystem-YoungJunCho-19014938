from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Sample:
    id: str               # 사용자 정의 시료 ID (고유값, ex: GaN-001)
    name: str             # 시료 이름
    avg_production_time: float   # 평균 생산시간 (시간 단위)
    yield_rate: float     # 수율 (0.0 ~ 1.0, ex: 0.9 = 90%)
    stock_quantity: int = 0
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "avg_production_time": self.avg_production_time,
            "yield_rate": self.yield_rate,
            "stock_quantity": self.stock_quantity,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Sample":
        return cls(
            id=data["id"],
            name=data["name"],
            avg_production_time=float(data.get("avg_production_time", 0.0)),
            yield_rate=float(data.get("yield_rate", 1.0)),
            stock_quantity=data.get("stock_quantity", 0),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )
