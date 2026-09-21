from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ProductOut(BaseModel):
    id: int
    sku: str
    name: str
    price_cents: int
    stock: int
    category_id: int
    attrs: dict[str, Any]
    created_at: datetime


class CursorOut(BaseModel):
    created_at: datetime
    id: int


class ProductPageOut(BaseModel):
    items: list[ProductOut]
    next_cursor: CursorOut | None
