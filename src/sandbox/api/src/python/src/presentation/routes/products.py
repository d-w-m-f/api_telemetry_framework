from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from business.services.product_service import ProductService
from persistence.models.product import Product
from presentation.schemas.product import CursorOut, ProductOut, ProductPageOut

router = APIRouter()


def get_product_service(request: Request) -> ProductService:
    return ProductService(request.app.state.product_repository)


def _to_schema(product: Product) -> ProductOut:
    return ProductOut(
        id=product.id,
        sku=product.sku,
        name=product.name,
        price_cents=product.price_cents,
        stock=product.stock,
        category_id=product.category_id,
        attrs=product.attrs,
        created_at=product.created_at,
    )


@router.get("/products", response_model=ProductPageOut)
async def list_products(
    service: Annotated[ProductService, Depends(get_product_service)],
    limit: int = Query(default=100, ge=1, le=500),
    after_created_at: datetime | None = Query(default=None),
    after_id: int | None = Query(default=None),
) -> ProductPageOut:
    products = await service.list_products(limit, after_created_at, after_id)
    next_cursor = (
        CursorOut(created_at=products[-1].created_at, id=products[-1].id)
        if len(products) == limit
        else None
    )
    return ProductPageOut(items=[_to_schema(p) for p in products], next_cursor=next_cursor)
