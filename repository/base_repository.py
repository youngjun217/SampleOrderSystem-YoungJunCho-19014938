import json
import os
from typing import Callable, Generic, List, Optional, TypeVar

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, db_path: str, from_dict: Callable[[dict], T]):
        self._db_path = db_path
        self._from_dict = from_dict
        self._ensure_db()

    def _ensure_db(self) -> None:
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        if not os.path.exists(self._db_path):
            self._write([])

    def _read(self) -> List[dict]:
        with open(self._db_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def _write(self, data: List[dict]) -> None:
        with open(self._db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def find_all(self) -> List[T]:
        return [self._from_dict(r) for r in self._read()]

    def find_by_id(self, entity_id: str) -> Optional[T]:
        record = next((r for r in self._read() if r["id"] == entity_id), None)
        return self._from_dict(record) if record else None

    def save(self, entity: T) -> T:
        records = self._read()
        records.append(entity.to_dict())
        self._write(records)
        return entity

    def update(self, entity: T) -> Optional[T]:
        records = self._read()
        for i, r in enumerate(records):
            if r["id"] == entity.id:
                records[i] = entity.to_dict()
                self._write(records)
                return entity
        return None

    def delete(self, entity_id: str) -> bool:
        records = self._read()
        filtered = [r for r in records if r["id"] != entity_id]
        if len(filtered) == len(records):
            return False
        self._write(filtered)
        return True

    def count(self) -> int:
        return len(self._read())
