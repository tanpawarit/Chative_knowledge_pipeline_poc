"""Application service for semantic chunk generation."""

from __future__ import annotations

from typing import List

from langchain_core.embeddings import Embeddings

from src.document_chunking.domain.models import DocumentChunk, DocumentMetadata
from src.document_chunking.domain.services import (
    SectionSemanticChunks,
    build_document_chunks,
)
from src.document_chunking.infrastructure.markdown_splitter import (
    split_markdown_structure,
)
from src.document_chunking.infrastructure.semantic_chunker import (
    SemanticChunkerAdapter,
)
from src.shared.config import ChunkingSettings
from src.shared.embeddings import create_embedding_runtime


def _default_embeddings(settings: ChunkingSettings) -> Embeddings:
    runtime = create_embedding_runtime(settings.embedding)
    return runtime.embeddings


def generate_document_chunks(
    markdown: str,
    *,
    source: str,
    doc_name: str,
    document_id: str,
    settings: ChunkingSettings,
) -> List[DocumentChunk]:
    """Split markdown into semantic chunks with normalized metadata."""

    if not doc_name:
        raise ValueError("doc_name is required to generate document chunks")
    if not document_id:
        raise ValueError("document_id is required to generate document chunks")

    base_sections = split_markdown_structure(
        markdown,
        chunk_size=settings.presplit_min_chars,
        chunk_overlap=settings.presplit_overlap_chars,
    )
    if not base_sections:
        return []

    document = DocumentMetadata(doc_name=doc_name, document_id=document_id, source=source)

    embed_backend = _default_embeddings(settings)
    chunker = SemanticChunkerAdapter(embed_backend, settings)

    section_chunks: List[SectionSemanticChunks] = []
    for header_index, chunk in enumerate(base_sections):
        section_meta = dict(chunk.get("meta") or {})
        semantic_docs = chunker.split(chunk.get("text", ""), section_meta)
        section_chunks.append(
            SectionSemanticChunks(
                header_index=header_index,
                section_metadata=section_meta,
                semantic_chunks=semantic_docs,
            )
        )

    return build_document_chunks(
        section_chunks,
        document=document,
        min_chunk_chars=settings.min_chars_per_subchunk,
    )


__all__ = ["generate_document_chunks"]
