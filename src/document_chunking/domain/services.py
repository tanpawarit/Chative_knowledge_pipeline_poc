"""Domain services for building document chunks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

from .models import DocumentChunk, DocumentMetadata


@dataclass
class SectionSemanticChunks:
    """Semantic chunk candidates produced for a markdown section."""

    header_index: int
    section_metadata: Dict[str, Any]
    semantic_chunks: List[Dict[str, Any]]  # each element: {"text": str, "metadata": Dict}


def _merge_small_chunks(
    semantic_chunks: Iterable[Dict[str, Any]],
    *,
    min_chunk_chars: int,
) -> List[Dict[str, Any]]:
    filtered: List[Dict[str, Any]] = []
    carryover_text = ""

    for chunk in semantic_chunks:
        text = (chunk.get("text") or "").strip()
        if not text:
            continue

        if carryover_text:
            text = f"{carryover_text}\n{text}".strip()
            carryover_text = ""

        if min_chunk_chars and len(text) < min_chunk_chars:
            carryover_text = text
            continue

        filtered.append({"text": text, "metadata": dict(chunk.get("metadata") or {})})

    if carryover_text and filtered:
        last = filtered[-1]
        last["text"] = f"{last['text']}\n{carryover_text}".strip()

    return filtered


def build_document_chunks(
    sections: Iterable[SectionSemanticChunks],
    *,
    document: DocumentMetadata,
    min_chunk_chars: int,
) -> List[DocumentChunk]:
    """Normalize semantic chunks and attach document-level metadata."""

    prepared: List[DocumentChunk] = []

    for section in sections:
        filtered = _merge_small_chunks(
            section.semantic_chunks,
            min_chunk_chars=max(0, min_chunk_chars),
        )
        if not filtered:
            continue

        total_section_chunks = len(filtered)
        base_meta = {
            **section.section_metadata,
            **document.as_dict(),
            "header_index": section.header_index,
            "section_parent_type": "markdown_header",
        }

        for semantic_index, chunk in enumerate(filtered):
            metadata = {**base_meta, **chunk.get("metadata", {})}
            metadata.update(
                {
                    "parent_type": "semantic_chunk",
                    "semantic_chunk_index": semantic_index,
                    "semantic_chunk_total": total_section_chunks,
                }
            )
            prepared.append(
                DocumentChunk(
                    text=chunk["text"],
                    metadata=metadata,
                    chunk_index=0,
                    total_chunks=0,
                )
            )

    total_chunks = len(prepared)
    for index, chunk in enumerate(prepared):
        chunk.chunk_index = index
        chunk.total_chunks = total_chunks
        chunk.metadata.setdefault("doc_name", document.doc_name)
        chunk.metadata.setdefault("doc_hash", document.doc_hash)
        chunk.metadata.setdefault("chunk_index", index)
        chunk.metadata.setdefault("chunk_total", total_chunks)
        chunk.metadata.setdefault("source", document.source)

    return prepared


__all__ = [
    "SectionSemanticChunks",
    "build_document_chunks",
]
