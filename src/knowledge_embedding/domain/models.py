"""Domain entities for the knowledge_embedding bounded context."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ChunkEmbeddingInput:
    """Normalized input required prior to generating embeddings."""

    id: str
    text: str
    metadata: Dict[str, Any]
    chunk_index: int
    total_chunks: int
    doc_hash: str
    doc_name: str
    created_at: int


@dataclass
class ChunkEmbeddingRecord:
    """Embedding output ready for persistence in vector stores."""

    id: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    dense_vector: List[float] = field(default_factory=list)
    chunk_index: int = 0
    total_chunks: int = 0
    doc_hash: str = ""
    doc_name: str = ""
    created_at: int = 0
    updated_at: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "metadata": dict(self.metadata),
            "dense_vector": list(self.dense_vector),
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            "doc_hash": self.doc_hash,
            "doc_name": self.doc_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


__all__ = ["ChunkEmbeddingInput", "ChunkEmbeddingRecord"]
