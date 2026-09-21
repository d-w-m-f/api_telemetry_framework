import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import register_routers
from persistence.factory.db_driver import create_product_repository


def build_app() -> FastAPI:
    """Builds the `fastapi_async` variant -- async route handlers, dependencies resolved from
    `app.state`. See fastapi.md §2 for the multi-variant factory pattern this follows; a future
    `fastapi_sync` variant would get its own builder here, sharing `app.py`/`business/`/`persistence/`."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        dsn = os.environ["DATABASE_URL"]
        app.state.product_repository = await create_product_repository(dsn)
        try:
            yield
        finally:
            await app.state.product_repository.close()

    app = FastAPI(lifespan=lifespan)
    register_routers(app)
    return app
