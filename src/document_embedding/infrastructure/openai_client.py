"""Backward-compatible export of OpenAI embedding helpers."""

from __future__ import annotations

from src.shared.embeddings.providers import OpenAIEmbedder, OpenAIEmbeddings

__all__ = ["OpenAIEmbedder", "OpenAIEmbeddings"]
