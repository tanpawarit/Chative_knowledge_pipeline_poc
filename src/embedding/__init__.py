"""Embedding utilities and configuration."""

from .config import EmbeddingSettings
from .dense import embed_chunks
from .gemini import GeminiEmbedder, GeminiEmbeddings
from .main import main_embedding

__all__ = [
    "EmbeddingSettings",
    "GeminiEmbedder",
    "GeminiEmbeddings",
    "embed_chunks",
    "main_embedding",
]
