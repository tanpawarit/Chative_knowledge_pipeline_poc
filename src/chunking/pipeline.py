from typing import Any, Dict, List

from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker

from src.chunking.config import ChunkingSettings
from src.chunking.splitter import split_by_markdown
from src.embedding.gemini import GeminiEmbedder, GeminiEmbeddings


def _build_semantic_chunker(settings: ChunkingSettings, embedder: GeminiEmbedder) -> SemanticChunker:
    chunker_kwargs: Dict[str, Any] = {
        "buffer_size": max(1, settings.semantic_buffer_size),
        "breakpoint_threshold_type": settings.semantic_breakpoint_type,
    }
    if settings.semantic_breakpoint_amount is not None:
        chunker_kwargs["breakpoint_threshold_amount"] = settings.semantic_breakpoint_amount

    min_size = settings.min_chars_per_subchunk
    if min_size > 0:
        chunker_kwargs["min_chunk_size"] = min_size

    return SemanticChunker(GeminiEmbeddings(embedder), **chunker_kwargs)


def run_pipeline(
    md_text: str,
    source: str,
    settings: ChunkingSettings,
    *,
    doc_name: str,
    doc_hash: str,
) -> List[Dict[str, Any]]:
    """Split Markdown into semantic chunks with normalized metadata.

    Purpose
    - Convert a Markdown document into a list of semantically coherent chunks
      using LangChain's `SemanticChunker` backed by Gemini embeddings.
    - Normalize and attach document-level and ordering metadata required by
      later embedding and storage stages.

    Inputs
    - `md_text`: str — Full Markdown text to split.
    - `source`: str — Original source path/URI for contextual metadata.
    - `settings`: ChunkingSettings — Controls semantic split behavior:
      - `semantic_buffer_size`: int
      - `semantic_breakpoint_type`: str
      - `semantic_breakpoint_amount`: Optional[float]
      - `min_chars_per_subchunk`: int — minimum chars for a final chunk; short
        segments are carried over and merged forward.
    - Keyword-only metadata inputs (must be provided by caller):
      - `doc_name`: str — Human-readable document name (usually filename).
      - `doc_hash`: str — Stable hash for deduplication (e.g., SHA256 of source content).

    Processing
    - First split by Markdown structure (`split_by_markdown`).
    - Then, for each section, use `SemanticChunker` to produce semantic sub-chunks.
    - Enforce `min_chars_per_subchunk` by carrying short fragments forward and
      merging them into the next chunk.

    Output
    - List[dict], one entry per final semantic chunk, each with:
      - `text`: str — chunk text content.
      - `meta`: dict — base metadata including (and not limited to):
        - `source`: str — original `source` value.
        - `doc_name`: str — supplied `doc_name` value.
        - `doc_hash`: str — supplied `doc_hash` value.
        - `chunk_index`: int — 0-based index across all emitted chunks.
        - `chunk_total`: int — total number of chunks emitted for this document.
        - `header_index`: int — index of the parent markdown header section.
        - `section_parent_type`: str — e.g., "markdown_header".
        - `parent_type`: str — e.g., "semantic_chunk".
        - `semantic_chunk_index`: int — index within the parent section.
        - `semantic_chunk_total`: int — total sub-chunks in the section.
      - `chunk_index`: int — same as in `meta` for convenience.
      - `total_chunks`: int — same as `chunk_total` in `meta`.
      - `doc_name`: str — duplicated for convenience.
      - `doc_hash`: str — duplicated for convenience.

    Notes
    - Returns an empty list if no chunks are produced.
    - The embedding stage expects `doc_hash`, `doc_name`, `chunk_index`, and
      `total_chunks` to be present (either at top level or in `meta`).
    """
    base_chunks = split_by_markdown(
        md_text,
        chunk_size=settings.presplit_min_chars,
        chunk_overlap=settings.presplit_overlap_chars,
    )
    if not base_chunks:
        return []

    if not doc_name:
        raise ValueError("`doc_name` is required; supply it before calling run_pipeline().")
    if not doc_hash:
        raise ValueError("`doc_hash` is required; supply it before calling run_pipeline().")

    gemini_embedder = GeminiEmbedder(settings.embedding)
    semantic_chunker = _build_semantic_chunker(settings, gemini_embedder)

    semantic_docs: List[Document] = []
    min_chunk_chars = max(0, settings.min_chars_per_subchunk)

    for header_index, chunk in enumerate(base_chunks):
        base_metadata = dict(chunk["meta"])
        base_metadata.update(
            {
                "source": source,
                "header_index": header_index,
                "section_parent_type": "markdown_header",
            }
        )

        base_doc = Document(page_content=chunk["text"], metadata=base_metadata)
        split_docs = semantic_chunker.split_documents([base_doc])

        filtered_docs: List[Document] = []
        carryover_text = ""
        for doc in split_docs:
            chunk_text = doc.page_content.strip()
            if not chunk_text:
                continue

            if carryover_text:
                chunk_text = f"{carryover_text}\n{chunk_text}".strip()
                carryover_text = ""

            if min_chunk_chars and len(chunk_text) < min_chunk_chars:
                carryover_text = chunk_text
                continue

            filtered_docs.append(
                Document(page_content=chunk_text, metadata=dict(doc.metadata))
            )

        if carryover_text and filtered_docs:
            last_doc = filtered_docs[-1]
            merged_text = f"{last_doc.page_content}\n{carryover_text}".strip()
            filtered_docs[-1] = Document(
                page_content=merged_text,
                metadata=dict(last_doc.metadata),
            )

        if carryover_text and not filtered_docs:
            # No valid chunks were produced; skip the leftover short text entirely.
            carryover_text = ""

        total = len(filtered_docs)
        for semantic_index, doc in enumerate(filtered_docs):
            metadata = dict(doc.metadata)
            metadata.update(
                {
                    "parent_type": "semantic_chunk",
                    "semantic_chunk_index": semantic_index,
                    "semantic_chunk_total": total,
                }
            )
            semantic_docs.append(
                Document(page_content=doc.page_content, metadata=metadata)
            )

    if not semantic_docs:
        return []

    results: List[Dict[str, Any]] = []
    total_chunks = len(semantic_docs)
    for chunk_index, doc in enumerate(semantic_docs):
        metadata = dict(doc.metadata)
        metadata.setdefault("doc_name", doc_name)
        metadata.setdefault("doc_hash", doc_hash)
        metadata.setdefault("chunk_index", chunk_index)
        metadata.setdefault("chunk_total", total_chunks)
        metadata.setdefault("source", source)

        chunk_entry: Dict[str, Any] = {
            "text": doc.page_content,
            "meta": metadata,
            "chunk_index": chunk_index,
            "total_chunks": total_chunks,
            "doc_name": doc_name,
            "doc_hash": doc_hash,
        }
        results.append(chunk_entry)

    return results
