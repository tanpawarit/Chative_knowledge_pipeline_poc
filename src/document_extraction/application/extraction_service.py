"""Application service orchestrating document extraction."""

from __future__ import annotations

from src.document_extraction.infrastructure.docling_extractor import run_extraction


def extract_markdown(document_bytes: bytes, *, filename: str) -> str:
    """Return the Markdown representation of the provided in-memory document."""
    return run_extraction(document_bytes, filename=filename)


__all__ = ["extract_markdown"]
