from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.chunking.main import main_chunking
from src.embedding.main import main_embedding
from src.extraction.main import main_extraction
 

def run_pipeline(source: Optional[str] = None) -> List[Dict[str, Any]]:
    """Run extraction → chunking → embedding and return embedded chunks."""
    src = source 

    markdown = main_extraction(src)
    chunks = main_chunking(markdown, source=src)
    embedded_chunks = main_embedding(chunks)

    return embedded_chunks


def main(source: Optional[str] = None) -> None:
    embedded = run_pipeline(source)
    print(f"Pipeline complete. Embedded {len(embedded)} chunks.")
    print(embedded[0] if embedded else "No chunks embedded.")


if __name__ == "__main__":
    main(source="data/Develop Process_QuantLab.pptx")
