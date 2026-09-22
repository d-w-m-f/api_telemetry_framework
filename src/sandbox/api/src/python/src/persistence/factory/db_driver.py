import os

from persistence.repositories.asyncpg_product_repository import AsyncpgProductRepository
from persistence.repositories.product_repository import ProductRepository

_BUILDERS = {
    "asyncpg": AsyncpgProductRepository.create,
}


async def create_product_repository(dsn: str) -> ProductRepository:
    """Builds the ProductRepository implementation selected by the DB_DRIVER env var (default: asyncpg).

    Called once at app startup (see presentation/factory/fastapi_async.py) -- the resulting repository, and
    the connection pool it owns, live for the app's lifetime rather than being rebuilt per request.
    """
    driver = os.environ.get("DB_DRIVER", "asyncpg")
    try:
        builder = _BUILDERS[driver]
    except KeyError:
        raise ValueError(f"unknown DB_DRIVER: {driver!r}") from None
    return await builder(dsn)
