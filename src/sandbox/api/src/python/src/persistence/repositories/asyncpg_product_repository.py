import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Self

import asyncpg

from persistence.models.product import Product
from persistence.repositories.product_repository import ProductRepository

# db/queries/postgres/ lives outside this package (shared across every sandbox API language). The Docker
# image COPYs it to SANDBOX_DB_QUERIES_DIR; the parents[5] fallback is the real repo layout, for local dev
# running straight out of the checkout.
_DEFAULT_QUERIES_DIR = Path(__file__).resolve().parents[5] / "db" / "queries" / "postgres"
_QUERIES_DIR = Path(os.environ.get("SANDBOX_DB_QUERIES_DIR") or _DEFAULT_QUERIES_DIR)

# list_products.sql filters with `WHERE (created_at, id) < ($1, $2)`. These sentinels are greater than any
# real row, so passing them for the first page (no cursor yet) returns the newest rows without a second,
# cursor-less query variant.
_NO_CURSOR_CREATED_AT = datetime.max.replace(tzinfo=timezone.utc)
_NO_CURSOR_ID = 2**63 - 1


async def _init_connection(conn: asyncpg.Connection) -> None:
    await conn.set_type_codec(
        "jsonb",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
        format="text",
    )


class AsyncpgProductRepository(ProductRepository):
    """asyncpg-backed implementation -- runs db/queries/postgres/list_products.sql verbatim."""

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool
        self._query = (_QUERIES_DIR / "list_products.sql").read_text()

    @classmethod
    async def create(cls, dsn: str) -> Self:
        pool = await asyncpg.create_pool(dsn=dsn, init=_init_connection)
        return cls(pool)

    async def list_products(
        self,
        limit: int,
        after_created_at: datetime | None,
        after_id: int | None,
    ) -> list[Product]:
        created_at = after_created_at or _NO_CURSOR_CREATED_AT
        row_id = after_id if after_id is not None else _NO_CURSOR_ID
        rows = await self._pool.fetch(self._query, created_at, row_id, limit)
        return [
            Product(
                id=row["id"],
                sku=row["sku"],
                name=row["name"],
                price_cents=row["price_cents"],
                stock=row["stock"],
                category_id=row["category_id"],
                attrs=row["attrs"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    async def close(self) -> None:
        await self._pool.close()
