"""Application service for embedding document chunks."""

from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Mapping

from src.document_chunking.domain.models import DocumentChunk
from src.knowledge_embedding.domain.models import ChunkEmbeddingRecord
from src.knowledge_embedding.domain.services import (
    finalize_embeddings,
    prepare_embedding_inputs,
)
from src.cost_management.infrastructure.openai_cost_tracker import (
    openai_cost_tracker,
)
from src.knowledge_embedding.infrastructure.openai_client import OpenAIEmbedder
from src.shared.config import EmbeddingSettings


def _coerce_chunk(chunk: Any) -> DocumentChunk:
    if isinstance(chunk, DocumentChunk):
        return chunk

    if isinstance(chunk, Mapping):
        text = chunk.get("text", "")
        metadata = dict(chunk.get("meta") or chunk.get("metadata") or {})
        doc_name = chunk.get("doc_name") or metadata.get("doc_name")
        doc_hash = chunk.get("doc_hash") or metadata.get("doc_hash")
        chunk_index = metadata.get("chunk_index")
        total_chunks = metadata.get("chunk_total") or chunk.get("total_chunks")
        if chunk_index is None:
            chunk_index = chunk.get("chunk_index", 0)
        if total_chunks is None:
            total_chunks = chunk.get("total_chunks", 0)
        return DocumentChunk(
            text=str(text),
            metadata={**metadata, "doc_name": doc_name, "doc_hash": doc_hash},
            chunk_index=int(chunk_index or 0),
            total_chunks=int(total_chunks or 0),
        )

    raise TypeError(f"Unsupported chunk type: {type(chunk).__name__}")


def embed_chunks(
    chunks: Iterable[Any],
    *,
    settings: EmbeddingSettings,
) -> List[Dict[str, Any]]:
    """Attach embeddings to document chunks and return persistence-ready rows."""

    chunk_list = [_coerce_chunk(chunk) for chunk in chunks]
    if not chunk_list:
        return []

    openai_cost_tracker.reset()
    openai_cost_tracker.configure_from_environment()

    inputs = prepare_embedding_inputs(chunk_list)
    texts = [item.text for item in inputs]

    embedder = OpenAIEmbedder(settings)
    dense_vectors = [vec.tolist() for vec in embedder.embed_batch(texts)]
    now_ms = int(time.time() * 1000)
    records: List[ChunkEmbeddingRecord] = finalize_embeddings(
        inputs,
        dense_vectors,
        updated_at=now_ms,
    )

    print(openai_cost_tracker.format_report())
    return [record.to_dict() for record in records]


__all__ = ["embed_chunks"]
