"""Structlog configuration helpers."""

from __future__ import annotations

import sys
from typing import Union

import structlog
from structlog.typing import FilteringBoundLogger

from src.shared.config.env import require_env

_configured = False

_LEVEL_MAP = {
    "TRACE": 5,
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
    "FATAL": 50,
    "NOTSET": 0,
}


def configure_logging(level: Union[int, str, None] = None) -> None:
    """Configure structlog once for the application."""

    global _configured
    if _configured:
        return

    if level is None:
        effective: Union[int, str] = require_env("LOG_LEVEL")
    else:
        effective = level

    resolved_level = _resolve_level(effective)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=True),
            structlog.processors.ExceptionPrettyPrinter(),
            structlog.processors.EventRenamer("message"),
            structlog.processors.KeyValueRenderer(
                key_order=["timestamp", "level", "logger", "message"]
            ),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(resolved_level),
        logger_factory=structlog.WriteLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    _configured = True


def get_logger(name: str | None = None) -> FilteringBoundLogger:
    """Return a structlog logger optionally bound with a name."""

    logger: FilteringBoundLogger = structlog.get_logger()
    if name:
        return logger.bind(logger=name)
    return logger


def _resolve_level(level: Union[int, str]) -> int:
    if isinstance(level, int):
        return level
    cleaned = (level or "").strip()
    if not cleaned:
        raise RuntimeError("LOG_LEVEL must be set when logging level is not provided")
    if cleaned.isdigit():
        return int(cleaned)
    upper = cleaned.upper()
    resolved = _LEVEL_MAP.get(upper)
    if resolved is None:
        raise RuntimeError(f"Unsupported LOG_LEVEL '{level}'")
    return resolved


__all__ = ["configure_logging", "get_logger"]
