import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.chunking.config import ChunkingSettings
from src.chunking.pipeline import run_pipeline


def read_input(src: str) -> str:
    p = src.strip()
    if p.startswith("http://") or p.startswith("https://"):
        if requests is None:
            raise RuntimeError("requests not available. `uv add requests` or use local file.")
        r = requests.get(p, timeout=30)
        r.raise_for_status()
        return r.text
    return Path(p).read_text(encoding="utf-8")


def run_chunking(
    source: str,
    *,
    settings: Optional[ChunkingSettings] = None,
    include_vectors: bool = False,
    output_path: Optional[Path] = None,
    markdown_text: Optional[str] = None,
) -> List[Dict[str, Any]]:
    settings = settings or ChunkingSettings()
    md_text = markdown_text if markdown_text is not None else read_input(source)
    chunks = run_pipeline(
        md_text,
        source=source,
        settings=settings,
        include_vectors=include_vectors,
    )

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            for ch in chunks:
                f.write(json.dumps(ch, ensure_ascii=False) + "\n")

    return chunks


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


# def main(
#     source: Optional[str] = None,
#     *,
#     output_path: str = "chunks.jsonl",
#     include_vectors: bool = True,
# ) -> None:
#     src = source or "output/Cryptography.md"
#     out_path = Path(output_path)
#     chunks = run_chunking(
#         src,
#         settings=ChunkingSettings(),
#         include_vectors=include_vectors,
#         output_path=out_path,
#     )
#     print(f"Wrote {len(chunks)} chunks → {out_path}")


# if __name__ == "__main__":
#     main()
