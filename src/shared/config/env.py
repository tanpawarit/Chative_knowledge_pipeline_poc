"""Helper functions for reading required environment variables."""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv


load_dotenv()


class MissingEnvironmentVariable(RuntimeError):
    """Raised when a required environment variable is not configured."""


def require_env(key: str) -> str:
    """Return a non-empty environment variable or raise an error."""

    raw_value = os.getenv(key)
    if raw_value is None:
        raise MissingEnvironmentVariable(f"{key} is required but not set")
    value = raw_value.strip()
    if not value:
        raise MissingEnvironmentVariable(f"{key} is required but blank")
    return value


def optional_env(key: str) -> Optional[str]:
    """Return a trimmed env value or None when unset/blank."""

    raw_value = os.getenv(key)
    if raw_value is None:
        return None
    value = raw_value.strip()
    return value or None


def require_int_env(key: str) -> int:
    """Return an int parsed from an environment variable."""

    value = require_env(key)
    try:
        return int(value)
    except ValueError as exc:
        raise MissingEnvironmentVariable(f"{key} must be an integer") from exc


def require_float_env(key: str) -> float:
    """Return a float parsed from an environment variable."""

    value = require_env(key)
    try:
        return float(value)
    except ValueError as exc:
        raise MissingEnvironmentVariable(f"{key} must be a float") from exc


def optional_float_env(key: str) -> Optional[float]:
    """Return an optional float parsed from an environment variable."""

    value = optional_env(key)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise MissingEnvironmentVariable(f"{key} must be a float") from exc


__all__ = [
    "MissingEnvironmentVariable",
    "optional_env",
    "optional_float_env",
    "require_env",
    "require_float_env",
    "require_int_env",
]
