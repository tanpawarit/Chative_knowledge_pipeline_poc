"""Gemini embedding client used by the knowledge_embedding context."""

from __future__ import annotations

import os
from typing import List

import google.generativeai as genai
import numpy as np
from langchain_core.embeddings import Embeddings

from src.cost_management.infrastructure.gemini_cost_tracker import (
    EmbeddingPricing,
    gemini_cost_tracker,
)
from src.shared.config import EmbeddingSettings

# Quiet noisy gRPC warnings about ALTS credentials when running outside GCP.
os.environ.setdefault("GRPC_VERBOSITY", "NONE")
os.environ.setdefault("GRPC_LOG_SEVERITY", "ERROR")
os.environ.setdefault("ABSL_LOGGING_STDERR_THRESHOLD", "3")


class GeminiEmbedder:
    def __init__(self, settings: EmbeddingSettings):
        genai.configure(api_key=settings.ensure_api_key())
        self.model = settings.model
        self.batch_size = settings.batch_size
        self.cost_tracker = gemini_cost_tracker

        override_price = getattr(settings, "embed_price_per_million_tokens", None)
        if override_price:
            self.cost_tracker.configure_pricing(
                self.model,
                EmbeddingPricing(usd_per_million_tokens=float(override_price)),
            )

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        if not texts:
            return []

        out: List[np.ndarray] = []
        batch_size = self.batch_size
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            for item in batch:
                resp = genai.embed_content(model=self.model, content=item)
                embedding = resp["embedding"]
                out.append(np.array(embedding, dtype=np.float32))

                self.cost_tracker.record_embedding(
                    self.model,
                    response_usage=resp,
                    text=item,
                )
        return out


class GeminiEmbeddings(Embeddings):
    """LangChain-compatible embedding wrapper around `GeminiEmbedder`."""

    def __init__(self, embedder: GeminiEmbedder):
        self._embedder = embedder

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        vectors = self._embedder.embed_batch(texts)
        return [vec.tolist() for vec in vectors]

    def embed_query(self, text: str) -> List[float]:
        doc_vecs = self.embed_documents([text])
        return doc_vecs[0] if doc_vecs else []


__all__ = ["GeminiEmbedder", "GeminiEmbeddings"]
