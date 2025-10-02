"""Embedding utilities and configuration."""

from .config import EmbeddingSettings
from .gemini import GeminiEmbedder, GeminiEmbeddings
from .main import embed_chunks, main_embedding

__all__ = [
    "EmbeddingSettings",
    "GeminiEmbedder",
    "GeminiEmbeddings",
    "embed_chunks",
    "main_embedding",
]
