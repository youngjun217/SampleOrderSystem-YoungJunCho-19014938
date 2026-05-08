import math
from dataclasses import dataclass, field
from datetime import datetime
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
    quantity: int           # 주문 수량
    shortage: int           # 부족분 (= 실제 생산 목표)
    actual_quantity: int    # 실 생산량 = ceil(shortage / (yield * 0.9))
    total_time: float       # 총 생산시간 (h) = avg_time * actual_quantity
    status: ProductionStatus = ProductionStatus.WAITING
    queued_at: str = field(default_factory=lambda: datetime.now().isoformat())
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
            "shortage": self.shortage,
            "actual_quantity": self.actual_quantity,
            "total_time": self.total_time,
            "status": self.status.value,
            "queued_at": self.queued_at,
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
            shortage=data.get("shortage", data["quantity"]),
            actual_quantity=data.get("actual_quantity", data["quantity"]),
            total_time=float(data.get("total_time", 0.0)),
            status=ProductionStatus(data.get("status", "WAITING")),
            queued_at=data.get("queued_at", datetime.now().isoformat()),
            started_at=data.get("started_at", ""),
            completed_at=data.get("completed_at", ""),
        )
