from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Sample:
    id: str
    name: str
    spec: str
    stock_quantity: int = 0
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "spec": self.spec,
            "stock_quantity": self.stock_quantity,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Sample":
        return cls(
            id=data["id"],
            name=data["name"],
            spec=data["spec"],
            stock_quantity=data.get("stock_quantity", 0),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )
