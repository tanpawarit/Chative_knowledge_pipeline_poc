import json
import sys
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.chunking.config import Settings
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

source = "output/Cryptography.md"
out = "chunks.jsonl"
settings = Settings()
md_text = read_input(source)
chunks = run_pipeline(md_text, source=source, settings=settings)

out = Path(out)
with out.open("w", encoding="utf-8") as f:
    for ch in chunks:
        f.write(json.dumps(ch, ensure_ascii=False) + "\n")

print(f"Wrote {len(chunks)} chunks → {out}")
