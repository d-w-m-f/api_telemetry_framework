from datetime import datetime

from persistence.models.product import Product
from persistence.repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    async def list_products(
        self,
        limit: int,
        after_created_at: datetime | None,
        after_id: int | None,
    ) -> list[Product]:
        return await self._repository.list_products(limit, after_created_at, after_id)
