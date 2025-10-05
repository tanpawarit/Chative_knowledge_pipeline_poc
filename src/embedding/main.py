from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from src.embedding.config import EmbeddingSettings
from src.embedding.dense import embed_chunks
from cost_tracker.gemini_cost_tracker import gemini_cost_tracker


def main_embedding(
    chunks: Iterable[Dict[str, Any]],
    *,
    settings: Optional[EmbeddingSettings] = None,
) -> List[Dict[str, Any]]:
    """Return embedded rows ready to upsert (no I/O)."""
    gemini_cost_tracker.reset()
    gemini_cost_tracker.configure_from_environment()
    embedded_rows = embed_chunks(chunks, settings=settings)
    print(gemini_cost_tracker.format_report())
    return embedded_rows
