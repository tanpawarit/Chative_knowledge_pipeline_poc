"""Infrastructure adapters for document_embedding."""

from .openai_client import OpenAIEmbedder, OpenAIEmbeddings

__all__ = [
    "OpenAIEmbedder",
    "OpenAIEmbeddings",
]
