from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class Product:
    id: int
    sku: str
    name: str
    price_cents: int
    stock: int
    category_id: int
    attrs: dict[str, Any]
    created_at: datetime
