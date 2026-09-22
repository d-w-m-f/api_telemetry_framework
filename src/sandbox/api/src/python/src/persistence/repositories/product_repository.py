from abc import ABC, abstractmethod
from datetime import datetime

from persistence.models.product import Product


class ProductRepository(ABC):
    """Read access to the `products` table.

    This is a comparison knob distinct from APP_VARIANT (see fastapi.md §2): which DB-access library backs
    the sandbox API's persistence layer. One concrete implementation per library under comparison lives
    alongside this file (only `asyncpg` for now); business/ and presentation/ only ever depend on this ABC.
    """

    @abstractmethod
    async def list_products(
        self,
        limit: int,
        after_created_at: datetime | None,
        after_id: int | None,
    ) -> list[Product]:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError
