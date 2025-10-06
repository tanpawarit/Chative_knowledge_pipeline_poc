"""Application layer for document chunking."""

from .chunking_service import generate_document_chunks, to_records

__all__ = [
    "generate_document_chunks",
    "to_records",
]
