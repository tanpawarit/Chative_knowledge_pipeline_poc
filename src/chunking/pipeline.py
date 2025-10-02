from typing import Any, Dict, List

from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker

from src.chunking.config import ChunkingSettings
from src.chunking.splitter import split_by_markdown
from src.chunking.utils import make_chunk_id
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
    include_dense_vectors: bool = True,
) -> List[Dict[str, Any]]:
    base_chunks = split_by_markdown(md_text)
    if not base_chunks:
        return []

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

    dense_vectors: List[List[float]] = []
    if include_dense_vectors:
        raw_vectors = gemini_embedder.embed_batch(
            [doc.page_content for doc in semantic_docs]
        )
        if len(raw_vectors) != len(semantic_docs):
            raise RuntimeError("Gemini embedding count mismatch with semantic chunks")
        dense_vectors = [vec.tolist() for vec in raw_vectors]

    results: List[Dict[str, Any]] = []
    for index, doc in enumerate(semantic_docs):
        chunk_entry: Dict[str, Any] = {
            "id": make_chunk_id(doc.page_content),
            "text": doc.page_content,
            "meta": doc.metadata,
        }
        if include_dense_vectors:
            chunk_entry["dense_vector"] = dense_vectors[index]
        results.append(chunk_entry)

    return results
