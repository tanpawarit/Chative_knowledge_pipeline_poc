from typing import Any, Dict, List

from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker

from src.chunking.config import Settings
from src.chunking.embed_gemini import GeminiEmbedder, GeminiEmbeddings
from src.chunking.splitter import split_by_markdown
from src.chunking.utils import make_chunk_id


def _build_semantic_chunker(settings: Settings, embedder: GeminiEmbedder) -> SemanticChunker:
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


def run_pipeline(md_text: str, source: str, settings: Settings) -> List[Dict[str, Any]]:
    base_chunks = split_by_markdown(md_text)
    if not base_chunks:
        return []

    gemini_embedder = GeminiEmbedder(settings)
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
            semantic_docs.append(Document(page_content=doc.page_content, metadata=metadata))

    if not semantic_docs:
        return []

    vectors = gemini_embedder.embed_batch([doc.page_content for doc in semantic_docs])
    if len(vectors) != len(semantic_docs):
        raise RuntimeError("Gemini embedding count mismatch with semantic chunks")

    results: List[Dict[str, Any]] = []
    for doc, vec in zip(semantic_docs, vectors):
        results.append(
            {
                "id": make_chunk_id(doc.page_content),
                "text": doc.page_content,
                "vector": vec.tolist(),
                "meta": doc.metadata,
            }
        )

    return results
