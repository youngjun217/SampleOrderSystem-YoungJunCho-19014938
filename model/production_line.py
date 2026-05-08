from dataclasses import dataclass
from enum import Enum


class LineStatus(Enum):
    IDLE    = "IDLE"     # 유휴
    RUNNING = "RUNNING"  # 가동 중


@dataclass
class ProductionLine:
    id: str
    name: str
    status: LineStatus = LineStatus.IDLE
    current_order_id: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "current_order_id": self.current_order_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProductionLine":
        return cls(
            id=data["id"],
            name=data["name"],
            status=LineStatus(data.get("status", "IDLE")),
            current_order_id=data.get("current_order_id", ""),
        )
