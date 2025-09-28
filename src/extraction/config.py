from __future__ import annotations

import logging
import os

_log = logging.getLogger(__name__)


def _get_env(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def _get_float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return float(value)
    except ValueError:  # pragma: no cover - defensive parsing
        _log.warning("Invalid float for %s: %s", name, value)
        return default


OCR_MODEL = _get_env("MISTRAL_OCR_MODEL", "mistral-ocr-latest")
PICTURE_MODEL = _get_env("MISTRAL_PICTURE_MODEL", "pixtral-12b")
PICTURE_PROMPT = _get_env(
    "MISTRAL_PICTURE_PROMPT",
    "Summarize the picture in 2-3 sentences, capturing layout, text, and key visuals.",
)

OCR_COST_PER_PAGE = _get_float_env("MISTRAL_OCR_COST_PER_PAGE", 0.005)
PICTURE_INPUT_COST_PER_MILLION = _get_float_env(
    "MISTRAL_PICTURE_INPUT_COST_PER_MILLION", 1.8
)
PICTURE_OUTPUT_COST_PER_MILLION = _get_float_env(
    "MISTRAL_PICTURE_OUTPUT_COST_PER_MILLION", 5.4
)


__all__ = [
    "OCR_MODEL",
    "PICTURE_MODEL",
    "PICTURE_PROMPT",
    "OCR_COST_PER_PAGE",
    "PICTURE_INPUT_COST_PER_MILLION",
    "PICTURE_OUTPUT_COST_PER_MILLION",
]
