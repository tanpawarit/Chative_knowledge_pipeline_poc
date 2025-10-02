from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from src.embedding.config import MilvusSettings
from src.load.milvus_store import MilvusStore


def main_upsert(
    rows: Iterable[Dict[str, Any]],
    *,
    settings: Optional[MilvusSettings] = None,
) -> None:
    """Upsert already-embedded rows into Milvus.

    Expects each row to have: id, text, metadata, dense_vector.
    """
    rows = list(rows)
    if not rows:
        return

    milvus = MilvusStore((settings or MilvusSettings()).ensure_ready())
    milvus.upsert(rows)

