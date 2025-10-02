from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from src.embedding.config import EmbeddingSettings
from src.embedding.dense import embed_chunks


def main_embedding(
    chunks: Iterable[Dict[str, Any]],
    *,
    settings: Optional[EmbeddingSettings] = None,
) -> List[Dict[str, Any]]:
    """Return embedded rows ready to upsert (no I/O)."""
    return embed_chunks(chunks, settings=settings)
