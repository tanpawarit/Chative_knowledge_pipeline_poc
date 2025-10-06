"""Domain entities supporting document chunking."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(frozen=True)
class DocumentMetadata:
    """Document-level metadata required for downstream stages."""

    doc_name: str
    doc_hash: str
    source: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "doc_name": self.doc_name,
            "doc_hash": self.doc_hash,
            "source": self.source,
        }


@dataclass
class DocumentChunk:
    """Semantic chunk of a document enriched with normalized metadata."""

    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunk_index: int = 0
    total_chunks: int = 0

    def __post_init__(self) -> None:
        if not self.text:
            raise ValueError("DocumentChunk.text must be non-empty")
        if self.chunk_index < 0:
            raise ValueError("chunk_index must be >= 0")
        if self.total_chunks < 0:
            raise ValueError("total_chunks must be >= 0")

    def to_record(self) -> Dict[str, Any]:
        """Return a dict payload compatible with downstream embedding flows."""
        base = dict(self.metadata)
        base.setdefault("chunk_index", self.chunk_index)
        base.setdefault("chunk_total", self.total_chunks)

        return {
            "text": self.text,
            "meta": base,
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            "doc_name": base.get("doc_name"),
            "doc_hash": base.get("doc_hash"),
        }


__all__ = ["DocumentMetadata", "DocumentChunk"]
