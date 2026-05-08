from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class OrderStatus(Enum):
    RESERVED  = "RESERVED"   # 주문접수
    REJECTED  = "REJECTED"   # 주문거절
    PRODUCING = "PRODUCING"  # 승인 + 재고 부족 → 생산 중
    CONFIRMED = "CONFIRMED"  # 승인 + 재고 확보 → 출고 대기
    RELEASE   = "RELEASE"    # 출고완료


@dataclass
class Order:
    id: str
    customer_name: str
    sample_id: str
    sample_name: str
    quantity: int
    due_date: str
    status: OrderStatus = OrderStatus.RESERVED
    reject_reason: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "sample_id": self.sample_id,
            "sample_name": self.sample_name,
            "quantity": self.quantity,
            "due_date": self.due_date,
            "status": self.status.value,
            "reject_reason": self.reject_reason,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        return cls(
            id=data["id"],
            customer_name=data["customer_name"],
            sample_id=data["sample_id"],
            sample_name=data.get("sample_name", ""),
            quantity=data["quantity"],
            due_date=data["due_date"],
            status=OrderStatus(data.get("status", "RESERVED")),
            reject_reason=data.get("reject_reason", ""),
            created_at=data.get("created_at", datetime.now().isoformat()),
        )
