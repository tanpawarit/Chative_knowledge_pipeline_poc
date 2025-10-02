import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.chunking.config import ChunkingSettings
from src.chunking.pipeline import run_pipeline


def main_chunking(
    markdown: str,
    *,
    source: str = "inline",
    settings: Optional[ChunkingSettings] = None,
) -> List[Dict[str, Any]]:
    """Chunk Markdown into semantic segments without embeddings."""
    use_settings = settings or ChunkingSettings()
    return run_pipeline(
        markdown,
        source=source,
        settings=use_settings,
        include_vectors=False,
    )
