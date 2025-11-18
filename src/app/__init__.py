"""FastAPI application package exposing the QStash webhook."""

from __future__ import annotations

from fastapi import FastAPI

from src.app.api.routers import qstash
from src.shared.logging.logger import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="QStash Receiver")
    app.include_router(qstash.router)
    return app


__all__ = ["create_app"]
