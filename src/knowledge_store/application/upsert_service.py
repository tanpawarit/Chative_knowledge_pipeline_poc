from __future__ import annotations

from typing import Any, Dict, Iterable

from src.knowledge_store.infrastructure.milvus_store import MilvusStore
from src.shared.config import MilvusSettings


def main_upsert(
    rows: Iterable[Dict[str, Any]],
    *,
    settings: MilvusSettings,
) -> None:
    """Upsert already-embedded rows into Milvus.

    Expects each row to have: id, text, metadata, dense_vector.
    """
    rows = list(rows)
    if not rows:
        return

    milvus = MilvusStore(settings.ensure_ready())
    milvus.upsert(rows)
