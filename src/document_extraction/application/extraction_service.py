"""Application service orchestrating document extraction."""

from __future__ import annotations

from src.document_extraction.infrastructure.docling_extractor import run_extraction


def extract_markdown(source: str) -> str:
    """Return the Markdown representation of the provided document source."""
    return run_extraction(source)


__all__ = ["extract_markdown"]
