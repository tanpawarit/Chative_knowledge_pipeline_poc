import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    genai_api_key: str = os.getenv("GEMINI_API_KEY", "")
    model_emb: str = os.getenv("GEMINI_EMBED_MODEL", "models/text-embedding-004")

    # sizing by characters (model-agnostic & simple); adjust as needed
    max_chars_per_subchunk: int = int(os.getenv("MAX_CHARS", 3000))
    min_chars_per_subchunk: int = int(os.getenv("MIN_CHARS", 700))
    overlap_chars: int = int(os.getenv("OVERLAP_CHARS", 300))
    cohesion_drop: float = float(os.getenv("COHESION_DROP", 0.12))

    # batch size for API calls
    batch_size: int = int(os.getenv("BATCH_SIZE", 128))

    # caching
    cache_dir: str = os.getenv("CACHE_DIR", ".chunk_cache")
