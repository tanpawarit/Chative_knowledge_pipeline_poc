"""FastAPI application entry point."""

from __future__ import annotations

from src.app import create_app
from src.shared.config.env import require_int_env
from src.shared.logging.logger import get_logger


app = create_app()
logger = get_logger(__name__)


def _run() -> None:
    import uvicorn

    port = require_int_env("APP_SERVER_PORT")

    logger.info(
        "Starting QStash receiver",
        url=f"http://127.0.0.1:{port}",
        route="/consume/documents/embed",
    )
    uvicorn.run(app, port=port, log_level="warning", access_log=False, log_config=None)


if __name__ == "__main__":
    _run()
