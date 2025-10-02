"""Dense embedding helpers for Gemini outputs."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from src.chunking.utils import make_chunk_id
from src.embedding.config import EmbeddingSettings
from src.embedding.gemini import GeminiEmbedder


def embed_chunks(
    chunks: Iterable[Dict[str, Any]],
    *,
    settings: Optional[EmbeddingSettings] = None,
) -> List[Dict[str, Any]]:
    """Attach Gemini embeddings and return rows ready for upsert.

    Output rows have the shape: {"id", "text", "metadata", "dense_vector"}. 
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

    for chunk, dense_vec in zip(chunk_list, dense_vectors):
        chunk_id = chunk.get("id") or make_chunk_id(chunk.get("text", ""))
        dense_list = dense_vec.tolist()
        entries_for_upsert.append(
            {
                "id": chunk_id,
                "text": chunk.get("text", ""),
                "metadata": dict(chunk.get("meta") or {}),
                "dense_vector": dense_list,
            }
        )

    return entries_for_upsert
