"""Knowledge embedding bounded context."""

from .application.embed_pipeline import embed_chunks
from .domain.models import ChunkEmbeddingInput, ChunkEmbeddingRecord

__all__ = [
    "ChunkEmbeddingInput",
    "ChunkEmbeddingRecord",
    "embed_chunks",
]
