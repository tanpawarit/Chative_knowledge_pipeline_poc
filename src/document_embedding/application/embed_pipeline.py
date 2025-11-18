"""Application service for embedding document chunks."""

from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Sequence

import numpy as np

from src.document_embedding.domain.models import ChunkEmbeddingRecord
from src.document_embedding.domain.services import (
    finalize_embeddings,
    prepare_embedding_inputs,
)
from src.shared.config import EmbeddingSettings
from src.shared.embeddings import create_embedding_runtime
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


def _to_float_list(vector: Sequence[float | int]) -> List[float]:
    return [float(value) for value in vector]


def embed_chunks(
    chunks: Iterable[Any],
    *,
    settings: EmbeddingSettings,
) -> List[Dict[str, Any]]:
    """Attach embeddings to document chunks and return persistence-ready rows."""

    runtime = create_embedding_runtime(settings)
    runtime.reset_usage()

    inputs = prepare_embedding_inputs(chunks)
    if not inputs:
        return []
    texts = [item.text for item in inputs]

    raw_vectors = runtime.client.embed_batch(texts)
    dense_vectors: List[List[float]] = []
    for vec in raw_vectors:
        if isinstance(vec, np.ndarray):
            dense_vectors.append(vec.astype(float).tolist())
        else:
            dense_vectors.append(_to_float_list(vec))

    now_ms = int(time.time() * 1000)
    records: List[ChunkEmbeddingRecord] = finalize_embeddings(
        inputs,
        dense_vectors,
        updated_at=now_ms,
    )

    usage_report = runtime.usage_report()
    if usage_report:
        logger.info("Embedding usage report", report=usage_report)

    return [record.to_dict() for record in records]


__all__ = ["embed_chunks"]
