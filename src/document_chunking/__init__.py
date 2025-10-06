"""Document chunking bounded context."""

from .application.chunking_service import generate_document_chunks, to_records
from .domain.models import DocumentChunk, DocumentMetadata

__all__ = [
    "DocumentChunk",
    "DocumentMetadata",
    "generate_document_chunks",
    "to_records",
]
