import os

from fastapi import FastAPI


def _build_app() -> FastAPI:
    variant = os.environ.get("APP_VARIANT", "fastapi_async")
    if variant == "fastapi_async":
        from presentation.factory.fastapi_async import build_app

        return build_app()
    raise ValueError(f"unknown APP_VARIANT: {variant!r}")


app = _build_app()
