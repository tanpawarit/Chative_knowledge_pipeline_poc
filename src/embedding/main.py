import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from src.embedding.config import EmbeddingSettings
from src.embedding.gemini import GeminiEmbedder


def embed_chunks(
    chunks: Iterable[Dict[str, Any]],
    *,
    settings: Optional[EmbeddingSettings] = None,
    output_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Attach Gemini embeddings to each chunk."""
    chunk_list = [dict(chunk) for chunk in chunks]
    if not chunk_list:
        return []

    settings = settings or EmbeddingSettings()
    embedder = GeminiEmbedder(settings)

    texts = [chunk.get("text", "") for chunk in chunk_list]
    vectors = embedder.embed_batch(texts)
    if len(vectors) != len(chunk_list):
        raise RuntimeError("Gemini embedding count mismatch with chunks")

    for chunk, vec in zip(chunk_list, vectors):
        chunk["vector"] = vec.tolist()

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as fp:
            for chunk in chunk_list:
                fp.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    return chunk_list


def main_embedding(
    chunks: Iterable[Dict[str, Any]],
    *,
    settings: Optional[EmbeddingSettings] = None,
) -> List[Dict[str, Any]]:
    """Convenience wrapper for embedding chunks without file I/O."""
    return embed_chunks(chunks, settings=settings, output_path=None)


# def _load_chunks(path: Path) -> List[Dict[str, Any]]:
#     with path.open("r", encoding="utf-8") as fp:
#         return [json.loads(line) for line in fp]


# def main(
#     input_path: str = "chunks.jsonl",
#     *,
#     output_path: str = "chunks_embedded.jsonl",
# ) -> None:
#     chunks = _load_chunks(Path(input_path))
#     enriched = embed_chunks(
#         chunks,
#         settings=EmbeddingSettings(),
#         output_path=Path(output_path),
#     )
#     print(f"Embedded {len(enriched)} chunks → {output_path}")


# if __name__ == "__main__":
#     main()
