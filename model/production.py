from dataclasses import dataclass
from enum import Enum


class ProductionStatus(Enum):
    WAITING = "WAITING"  # 생산라인 대기 중
    RUNNING = "RUNNING"  # 생산 중
    DONE    = "DONE"     # 생산 완료


@dataclass
class Production:
    id: str
    line_id: str
    order_id: str
    sample_id: str
    sample_name: str
    quantity: int
    status: ProductionStatus = ProductionStatus.WAITING
    started_at: str = ""
    completed_at: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "line_id": self.line_id,
            "order_id": self.order_id,
            "sample_id": self.sample_id,
            "sample_name": self.sample_name,
            "quantity": self.quantity,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Production":
        return cls(
            id=data["id"],
            line_id=data["line_id"],
            order_id=data["order_id"],
            sample_id=data["sample_id"],
            sample_name=data.get("sample_name", ""),
            quantity=data["quantity"],
            status=ProductionStatus(data.get("status", "WAITING")),
            started_at=data.get("started_at", ""),
            completed_at=data.get("completed_at", ""),
        )
