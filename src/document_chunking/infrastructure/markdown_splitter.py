"""Adapters for splitting markdown documents using LangChain text splitters."""

from __future__ import annotations

from typing import Any, Dict, List

from langchain_text_splitters import MarkdownHeaderTextSplitter, MarkdownTextSplitter


HEADERS = [("#", "H1"), ("##", "H2"), ("###", "H3")]


def split_markdown_structure(
    md_text: str,
    *,
    chunk_size: int,
    chunk_overlap: int,
) -> List[Dict[str, Any]]:
    """Split Markdown into structural sections with optional sub-splitting."""

    chunk_size = max(1, chunk_size)
    chunk_overlap = max(0, chunk_overlap)

    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS)
    header_docs = header_splitter.split_text(md_text)

    any_header = any(
        (doc.metadata.get("H1") or doc.metadata.get("H2") or doc.metadata.get("H3"))
        for doc in header_docs
    )

    md_splitter = MarkdownTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    out: List[Dict[str, Any]] = []

    if not header_docs or not any_header:
        for piece in md_splitter.split_text(md_text):
            text = piece.strip()
            if not text:
                continue
            out.append({"text": text, "meta": {"h1": "", "h2": "", "h3": ""}})
        return out

    threshold = max(chunk_size * 2, chunk_size + chunk_overlap)

    for doc in header_docs:
        meta = doc.metadata
        section_text = (doc.page_content or "").strip()
        if not section_text:
            continue

        base_meta = {
            "h1": meta.get("H1", ""),
            "h2": meta.get("H2", ""),
            "h3": meta.get("H3", ""),
        }

        if len(section_text) >= threshold:
            for part in md_splitter.split_text(section_text):
                text = part.strip()
                if text:
                    out.append({"text": text, "meta": dict(base_meta)})
            continue

        out.append({"text": section_text, "meta": dict(base_meta)})

    return out


__all__ = ["split_markdown_structure"]
