"""Infrastructure adapters for knowledge_embedding."""

from .gemini_client import GeminiEmbedder, GeminiEmbeddings
from .openai_client import OpenAIEmbedder, OpenAIEmbeddings

__all__ = [
    "GeminiEmbedder",
    "GeminiEmbeddings",
    "OpenAIEmbedder",
    "OpenAIEmbeddings",
]
