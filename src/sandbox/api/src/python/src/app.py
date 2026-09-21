from fastapi import FastAPI

from presentation.routes import health, products


def register_routers(app: FastAPI) -> None:
    """Attaches every route module to `app`. Shared by every APP_VARIANT builder in presentation/factory/
    so adding a route only ever needs to happen here, once."""
    app.include_router(health.router)
    app.include_router(products.router)
