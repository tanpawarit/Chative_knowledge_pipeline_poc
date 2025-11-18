"""Domain services for embedding normalization."""

from __future__ import annotations

import time
import uuid
from typing import Any, Iterable, List, Mapping, Protocol, runtime_checkable

from .models import ChunkEmbeddingInput, ChunkEmbeddingRecord


@runtime_checkable
class SupportsChunkRecord(Protocol):
    def to_record(self) -> Mapping[str, Any]:
        ...


def _chunk_to_record(chunk: Any) -> Mapping[str, Any]:
    if isinstance(chunk, Mapping):
        return chunk
    if isinstance(chunk, SupportsChunkRecord):
        return chunk.to_record()
    raise TypeError(f"Unsupported chunk type: {type(chunk).__name__}")


def prepare_embedding_inputs(chunks: Iterable[Any]) -> List[ChunkEmbeddingInput]:
    """Normalize document chunks into embedding inputs."""

    now_ms = int(time.time() * 1000)
    prepared: List[ChunkEmbeddingInput] = []

    for chunk in chunks:
        record = dict(_chunk_to_record(chunk))
        text = record.get("text", "")
        if not text.strip():
            continue

        metadata = dict(record.get("meta") or record.get("metadata") or {})

        chunk_index_raw = metadata.get("chunk_index") or record.get("chunk_index")
        chunk_total_raw = metadata.get("chunk_total") or record.get("total_chunks")
        document_id = metadata.get("document_id") or record.get("document_id")
        doc_name = metadata.get("doc_name") or record.get("doc_name")

        if document_id is None or not document_id:
            raise ValueError("Document chunk is missing document_id")
        if doc_name is None or not doc_name:
            raise ValueError("Document chunk is missing doc_name")
        if chunk_index_raw is None:
            raise ValueError("Document chunk is missing chunk_index")
        if chunk_total_raw is None:
            raise ValueError("Document chunk is missing chunk_total")

        chunk_index = int(chunk_index_raw)
        chunk_total = int(chunk_total_raw)

        metadata.setdefault("chunk_index", chunk_index)
        metadata.setdefault("chunk_total", chunk_total)
        metadata.setdefault("document_id", document_id)
        metadata.setdefault("doc_name", doc_name)

        chunk_id = record.get("id") or str(uuid.uuid4())
        created_at = int(record.get("created_at") or now_ms)

        prepared.append(
            ChunkEmbeddingInput(
                id=str(chunk_id),
                text=text,
                metadata=metadata,
                chunk_index=chunk_index,
                total_chunks=chunk_total,
                document_id=str(document_id),
                doc_name=str(doc_name),
                created_at=created_at,
            )
        )

    return prepared


def finalize_embeddings(
    inputs: List[ChunkEmbeddingInput],
    dense_vectors: List[List[float]],
    *,
    updated_at: int,
) -> List[ChunkEmbeddingRecord]:
    if len(inputs) != len(dense_vectors):
        raise RuntimeError("Embedding count mismatch with chunk inputs")

    records: List[ChunkEmbeddingRecord] = []
    for chunk_input, dense_vec in zip(inputs, dense_vectors):
        records.append(
            ChunkEmbeddingRecord(
                id=chunk_input.id,
                text=chunk_input.text,
                metadata=dict(chunk_input.metadata),
                dense_vector=list(dense_vec),
                chunk_index=chunk_input.chunk_index,
                total_chunks=chunk_input.total_chunks,
                document_id=chunk_input.document_id,
                doc_name=chunk_input.doc_name,
                created_at=chunk_input.created_at,
                updated_at=updated_at,
            )
        )
    return records


__all__ = ["prepare_embedding_inputs", "finalize_embeddings"]
