from __future__ import annotations

import hashlib
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.chunking.main import main_chunking
from src.embedding.config import MilvusSettings
from src.embedding.main import main_embedding
from src.extraction.main import main_extraction
from src.load.main import main_upsert
from src.load.milvus_store import MilvusStore


logger = logging.getLogger(__name__)


def run_pipeline(
    source: str,
    *,
    doc_name: str,
    doc_hash: str,
    do_upsert: bool = True,
    milvus_settings: Optional[MilvusSettings] = None,
    skip_if_unchanged: bool = True,
) -> List[Dict[str, Any]]:
    """Run extraction → chunking → embedding and optionally upsert.

    Requires callers to supply `doc_name` and `doc_hash` (e.g., sourced from
    upstream storage metadata) so downstream stages can enforce deduplication.
    When `skip_if_unchanged` is true and Milvus already stores a row with the
    same identifiers, the pipeline short-circuits and returns an empty list.
    """
    if not source:
        raise ValueError("`source` is required to run the pipeline.")
    if not doc_name:
        raise ValueError("`doc_name` must be supplied by the caller.")
    if not doc_hash:
        raise ValueError("`doc_hash` must be supplied by the caller.")

    resolved_settings = milvus_settings or MilvusSettings()
    milvus_ready: Optional[MilvusSettings] = None
    if resolved_settings.is_configured():
        milvus_ready = resolved_settings.ensure_ready()

    if skip_if_unchanged and do_upsert and milvus_ready is not None:
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

    markdown = main_extraction(source)

    chunks = main_chunking(
        markdown,
        source=source,
        doc_name=doc_name,
        doc_hash=doc_hash,
    )
    embedded_chunks = main_embedding(chunks)

    if do_upsert and milvus_ready is not None:
        main_upsert(embedded_chunks, settings=milvus_ready)

    return embedded_chunks


def main(source: str = "data/2509.04343v1.pdf") -> None:
    source_path = Path(source)
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    doc_name = source_path.name or "unknown"
    try:
        doc_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    except OSError as exc:
        raise RuntimeError(f"Unable to read source file for hashing: {source}") from exc

    embedded = run_pipeline(source, doc_name=doc_name, doc_hash=doc_hash)
    print(f"Pipeline complete. Embedded {len(embedded)} chunks.")
    print(embedded[0] if embedded else "No chunks embedded.")


if __name__ == "__main__":
    main()
