import os
from typing import List, Dict, Any

from dotenv import load_dotenv
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    MarkdownTextSplitter,
)

# Ensure .env is loaded when this module is imported standalone
load_dotenv()


HEADERS = [("#", "H1"), ("##", "H2"), ("###", "H3")]


def split_by_markdown(md_text: str) -> List[Dict[str, Any]]:
    """General-purpose Markdown splitter.

    Strategy:
    - First split by headers (H1/H2/H3) to preserve document structure.
    - If a section is very long or there are no headers at all, sub-split that
      content using MarkdownTextSplitter to respect Markdown blocks (lists/code/paras).

    Chunk sizing is controlled via dedicated environment variables:
      - PRESPLIT_MIN_CHARS
      - PRESPLIT_OVERLAP_CHARS
    """

    # Sizing knobs (char-based); enforced via environment variables
    chunk_size = int(os.environ["PRESPLIT_MIN_CHARS"])  # must be set in .env
    chunk_overlap = int(os.environ["PRESPLIT_OVERLAP_CHARS"])  # must be set in .env
    chunk_size = max(1, chunk_size)
    chunk_overlap = max(0, chunk_overlap)

    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS)
    header_docs = header_splitter.split_text(md_text)

    # Determine if headers are effectively absent across the document
    any_header = any(
        (d.metadata.get("H1") or d.metadata.get("H2") or d.metadata.get("H3"))
        for d in header_docs
    )

    md_splitter = MarkdownTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    out: List[Dict[str, Any]] = []

    if not header_docs or not any_header:
        # No meaningful headers; split the whole document by Markdown blocks
        for piece in md_splitter.split_text(md_text):
            text = piece.strip()
            if not text:
                continue
            out.append({"text": text, "meta": {"h1": "", "h2": "", "h3": ""}})
        return out

    # Otherwise, preserve header structure, with adaptive sub-splitting for long sections
    threshold = max(chunk_size * 2, chunk_size + chunk_overlap)

    for d in header_docs:
        meta = d.metadata
        section_text = d.page_content or ""
        section_text = section_text.strip()

        base_meta = {
            "h1": meta.get("H1", ""),
            "h2": meta.get("H2", ""),
            "h3": meta.get("H3", ""),
        }

        if not section_text:
            continue

        # Sub-split only if section is substantially larger than the desired chunk
        if len(section_text) >= threshold:
            parts = md_splitter.split_text(section_text)
            for p in parts:
                text = p.strip()
                if not text:
                    continue
                out.append({"text": text, "meta": dict(base_meta)})
        else:
            out.append({"text": section_text, "meta": dict(base_meta)})

    return out
