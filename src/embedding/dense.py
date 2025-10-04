"""Dense embedding helpers for Gemini outputs."""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Iterable, List, Optional

from src.embedding.config import EmbeddingSettings
from src.embedding.gemini import GeminiEmbedder


def embed_chunks(
    chunks: Iterable[Dict[str, Any]],
    *,
    settings: Optional[EmbeddingSettings] = None,
) -> List[Dict[str, Any]]:
    """Attach Gemini embeddings and return rows ready for Milvus upsert.

    Input
    - `chunks`: iterable of dicts. Each item must include:
      - `text`: str — required.
      - `meta` or `metadata`: dict — optional container; merged into the output.
        Required fields (ValueError if any is missing):
        - `doc_hash`: str — SHA256 of the full document content.
        - `doc_name`: str — original filename or logical document label.
        - `chunk_index`: int — 0-based index of this chunk in the document.
        - `chunk_total`: int — total number of chunks produced for the document.
      - Alternatively, the required fields may be given at the top level; they
        are read with the same names except `chunk_total` which maps to
        `total_chunks`.
      - `id`: str — optional; if absent a UUID4 is generated.
      - `created_at`: int (epoch ms) — optional; if absent it is set to now.

    Output
    - List[dict] with one entry per input chunk. Each entry has:
      - `id`: str — UUID if not provided.
      - `text`: str — the chunk text.
      - `metadata`: dict — original metadata plus normalized fields:
        - `doc_hash`, `doc_name`, `chunk_index`, `chunk_total`.
      - `dense_vector`: List[float] — Gemini embedding.
      - `chunk_index`: int — normalized index for convenience.
      - `total_chunks`: int — normalized total for convenience.
      - `doc_hash`: str — duplicated for direct filtering.
      - `doc_name`: str — duplicated for direct filtering.
      - `created_at`: int (epoch ms) — from input or set to now.
      - `updated_at`: int (epoch ms) — set to now.

    Notes
    - Raises RuntimeError if the number of embeddings does not match the number of chunks.
    - Raises ValueError if `doc_hash`, `doc_name`, `chunk_index`, or
      `chunk_total` is missing for any chunk.
    - Embedding dimension depends on the configured model (e.g., `models/text-embedding-004`).
    """
    chunk_list = [dict(chunk) for chunk in chunks]
    if not chunk_list:
        return []

    settings = settings or EmbeddingSettings()
    embedder = GeminiEmbedder(settings)

    texts = [chunk.get("text", "") for chunk in chunk_list]
    dense_vectors = embedder.embed_batch(texts)
    if len(dense_vectors) != len(chunk_list):
        raise RuntimeError("Gemini embedding count mismatch with chunks")

    entries_for_upsert: List[Dict[str, Any]] = []

    now_ms = int(time.time() * 1000)

    for _, (chunk, dense_vec) in enumerate(zip(chunk_list, dense_vectors)):
        chunk_text = chunk.get("text", "")
        metadata = dict(chunk.get("meta") or {})

        chunk_index_raw = (
            chunk.get("chunk_index")
            if "chunk_index" in chunk
            else metadata.get("chunk_index")
        )
        total_chunks_raw = (
            chunk.get("total_chunks")
            if "total_chunks" in chunk
            else metadata.get("chunk_total")
        )
        doc_hash = chunk.get("doc_hash") or metadata.get("doc_hash")
        doc_name = chunk.get("doc_name") or metadata.get("doc_name")

        if not doc_hash:
            raise ValueError("Chunk is missing 'doc_hash'; ensure the chunking pipeline provides it.")
        if not doc_name:
            raise ValueError("Chunk is missing 'doc_name'; ensure the chunking pipeline provides it.")
        if chunk_index_raw is None:
            raise ValueError("Chunk is missing 'chunk_index'; ensure the chunking pipeline provides it.")
        if total_chunks_raw is None:
            raise ValueError("Chunk is missing 'chunk_total'; ensure the chunking pipeline provides it.")

        chunk_index = int(chunk_index_raw)
        total_chunks = int(total_chunks_raw)

        metadata.setdefault("chunk_index", chunk_index)
        metadata.setdefault("chunk_total", total_chunks)
        metadata.setdefault("doc_hash", doc_hash)
        metadata.setdefault("doc_name", doc_name)

        dense_list = dense_vec.tolist()
        entries_for_upsert.append(
            {
                "id": str(chunk.get("id") or uuid.uuid4()),
                "text": chunk_text,
                "metadata": metadata,
                "dense_vector": dense_list,
                "chunk_index": chunk_index,
                "total_chunks": total_chunks,
                "doc_hash": doc_hash,
                "doc_name": doc_name,
                "created_at": chunk.get("created_at") or now_ms,
                "updated_at": now_ms,
            }
        )

    return entries_for_upsert
