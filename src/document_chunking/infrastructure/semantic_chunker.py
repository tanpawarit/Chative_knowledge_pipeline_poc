"""Semantic chunking adapter backed by LangChain's SemanticChunker."""

from __future__ import annotations

from typing import Any, Dict, List

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_experimental.text_splitter import SemanticChunker

from src.shared.config import ChunkingSettings


class SemanticChunkerAdapter:
    """Wrapper around LangChain's semantic chunker producing plain dicts."""

    def __init__(self, embeddings: Embeddings, settings: ChunkingSettings) -> None:
        chunker_kwargs: Dict[str, Any] = {
            "buffer_size": max(1, settings.semantic_buffer_size),
            "breakpoint_threshold_type": settings.semantic_breakpoint_type,
        }
        if settings.semantic_breakpoint_amount is not None:
            chunker_kwargs["breakpoint_threshold_amount"] = settings.semantic_breakpoint_amount

        min_size = settings.min_chars_per_subchunk
        if min_size > 0:
            chunker_kwargs["min_chunk_size"] = min_size

        self._chunker = SemanticChunker(embeddings, **chunker_kwargs)

    def split(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        base_doc = Document(page_content=text, metadata=dict(metadata))
        docs = self._chunker.split_documents([base_doc])
        return [
            {"text": doc.page_content, "metadata": dict(doc.metadata)}
            for doc in docs
            if doc.page_content.strip()
        ]


__all__ = ["SemanticChunkerAdapter"]
