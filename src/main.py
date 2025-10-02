from __future__ import annotations

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
    do_upsert: bool = True,
    milvus_settings: Optional[MilvusSettings] = None,
) -> List[Dict[str, Any]]:
    """Run extraction → chunking → embedding and optionally upsert."""
    if not source:
        raise ValueError("`source` is required to run the pipeline.")

    markdown = main_extraction(source)
    chunks = main_chunking(markdown, source=source)
    embedded_chunks = main_embedding(chunks)

    if do_upsert:
        settings = milvus_settings or MilvusSettings()
        if settings.is_configured():
            main_upsert(embedded_chunks, settings=settings)

    return embedded_chunks


def main(source: str = "data/Develop Process_QuantLab.pptx") -> None:
    embedded = run_pipeline(source)
    print(f"Pipeline complete. Embedded {len(embedded)} chunks.")
    print(embedded[0] if embedded else "No chunks embedded.")


if __name__ == "__main__":
    main()
