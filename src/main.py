from __future__ import annotations

import hashlib
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


def run_pipeline(
    source: str,
    *,
    doc_name: str,
    doc_hash: str,
    do_upsert: bool = True,
    milvus_settings: Optional[MilvusSettings] = None,
) -> List[Dict[str, Any]]:
    """Run extraction → chunking → embedding and optionally upsert.

    Requires callers to supply `doc_name` and `doc_hash` (e.g., sourced from
    upstream storage metadata) so downstream stages can enforce deduplication.
    """
    if not source:
        raise ValueError("`source` is required to run the pipeline.")
    if not doc_name:
        raise ValueError("`doc_name` must be supplied by the caller.")
    if not doc_hash:
        raise ValueError("`doc_hash` must be supplied by the caller.")

    markdown = main_extraction(source)

    chunks = main_chunking(
        markdown,
        source=source,
        doc_name=doc_name,
        doc_hash=doc_hash,
    )
    embedded_chunks = main_embedding(chunks)

    if do_upsert:
        settings = milvus_settings or MilvusSettings()
        if settings.is_configured():
            main_upsert(embedded_chunks, settings=settings)

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

    embedded = run_pipeline(source, doc_name=doc_name, doc_hash=doc_hash)
    print(f"Pipeline complete. Embedded {len(embedded)} chunks.")
    print(embedded[0] if embedded else "No chunks embedded.")


if __name__ == "__main__":
    main()
