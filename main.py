from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.document_chunking.application.chunking_service import (
    generate_document_chunks,
)
from src.document_extraction.application.extraction_service import extract_markdown
from src.knowledge_embedding.application.embed_pipeline import embed_chunks
from src.knowledge_store.application.upsert_service import main_upsert
from src.knowledge_store.infrastructure.milvus_store import MilvusStore
from src.shared.config import ChunkingSettings, EmbeddingSettings, MilvusSettings


logger = logging.getLogger(__name__)


def run_pipeline(
    source: str,
    *,
    doc_name: str,
    doc_hash: str,
    milvus_settings: MilvusSettings,
    chunking_settings: ChunkingSettings,
    embedding_settings: EmbeddingSettings,
) -> List[Dict[str, Any]]:
    """Run extraction → chunking → embedding and optionally upsert.

    Callers must supply document identifiers plus concrete settings objects for
    Milvus, chunking, and embedding so configuration is explicit at the entry
    point. When `skip_if_unchanged` is true and Milvus already stores a row with
    the same identifiers, the pipeline short-circuits and returns an empty list.
    """
    if not source:
        raise ValueError("`source` is required to run the pipeline.")
    if not doc_name:
        raise ValueError("`doc_name` must be supplied by the caller.")
    if not doc_hash:
        raise ValueError("`doc_hash` must be supplied by the caller.")

    milvus_ready: Optional[MilvusSettings] = None
    if milvus_settings.is_configured():
        milvus_ready = milvus_settings.ensure_ready()

    if milvus_ready is not None:
        try:
            store = MilvusStore(milvus_ready)
            workspace_id = milvus_ready.partition_key_value or None
            if store.document_exists(
                doc_name=doc_name,
                doc_hash=doc_hash,
                workspace_id=workspace_id,
            ):
                logger.info(
                    "Document '%s' already ingested with matching hash; skipping pipeline.",
                    doc_name,
                )
                return []
        except Exception as exc:  # pragma: no cover - defensive: continue when Milvus check fails
            logger.warning("Milvus preflight check failed; continuing pipeline: %s", exc)

    markdown = extract_markdown(source)

    chunks = generate_document_chunks(
        markdown,
        source=source,
        doc_name=doc_name,
        doc_hash=doc_hash,
        settings=chunking_settings,
    )
    embedded_chunks = embed_chunks(chunks, settings=embedding_settings)

    if milvus_ready is not None:
        main_upsert(embedded_chunks, settings=milvus_ready)

    return embedded_chunks


def main(source: str = "data/Screenshot 2568-07-18 at 12.10.26.png") -> None:
    source_path = Path(source)
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    doc_name = source_path.name or "unknown"
    try:
        doc_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    except OSError as exc:
        raise RuntimeError(f"Unable to read source file for hashing: {source}") from exc

    milvus_settings = MilvusSettings()
    chunking_settings = ChunkingSettings()
    embedding_settings = EmbeddingSettings()

    embedded = run_pipeline(
        source,
        doc_name=doc_name,
        doc_hash=doc_hash,
        milvus_settings=milvus_settings,
        chunking_settings=chunking_settings,
        embedding_settings=embedding_settings,
    )
    print(f"Pipeline complete. Embedded {len(embedded)} chunks.") 

if __name__ == "__main__":
    main()
