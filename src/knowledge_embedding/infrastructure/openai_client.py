"""OpenAI embedding client used by the knowledge_embedding context."""

from __future__ import annotations

from typing import List

import numpy as np
from langchain_core.embeddings import Embeddings
from openai import OpenAI

from src.cost_management.infrastructure.openai_cost_tracker import (
    EmbeddingPricing,
    openai_cost_tracker,
)
from src.shared.config import EmbeddingSettings


class OpenAIEmbedder:
    def __init__(self, settings: EmbeddingSettings):
        self._client = OpenAI(api_key=settings.ensure_api_key())
        self.model = settings.model
        self.batch_size = max(1, settings.batch_size)
        self.cost_tracker = openai_cost_tracker

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
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            for item in batch:
                response = self._client.embeddings.create(
                    model=self.model,
                    input=item,
                )
                embedding = response.data[0].embedding
                out.append(np.array(embedding, dtype=np.float32))

                usage = getattr(response, "usage", None)
                token_count = None
                if usage is not None:
                    if isinstance(usage, dict):
                        token_count = (
                            usage.get("total_tokens")
                            or usage.get("prompt_tokens")
                            or usage.get("input_tokens")
                        )
                    else:
                        token_count = (
                            getattr(usage, "total_tokens", None)
                            or getattr(usage, "prompt_tokens", None)
                            or getattr(usage, "input_tokens", None)
                        )

                self.cost_tracker.record_embedding(
                    self.model,
                    response_usage=usage,
                    token_count=token_count,
                    text=item,
                )
        return out


class OpenAIEmbeddings(Embeddings):
    """LangChain-compatible embedding wrapper around `OpenAIEmbedder`."""

    def __init__(self, embedder: OpenAIEmbedder):
        self._embedder = embedder

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        vectors = self._embedder.embed_batch(texts)
        return [vec.tolist() for vec in vectors]

    def embed_query(self, text: str) -> List[float]:
        doc_vecs = self.embed_documents([text])
        return doc_vecs[0] if doc_vecs else []


__all__ = ["OpenAIEmbedder", "OpenAIEmbeddings"]
