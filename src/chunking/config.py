import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


load_dotenv()


def _optional_float(env_key: str) -> Optional[float]:
    raw = os.getenv(env_key)
    if raw is None:
        return None
    value = raw.strip()
    if not value or value.lower() == "auto":
        return None
    return float(value)


@dataclass
class Settings:
    genai_api_key: str = os.getenv("GEMINI_API_KEY", "")
    model_emb: str = os.getenv("GEMINI_EMBED_MODEL", "models/text-embedding-004")
 
    min_chars_per_subchunk: int = int(os.getenv("MIN_CHARS", 700))
    overlap_chars: int = int(os.getenv("OVERLAP_CHARS", 300))
    cohesion_drop: float = float(os.getenv("COHESION_DROP", 0.12))

    # token-based sizing via TokenTextSplitter
    max_tokens_per_subchunk: int = int(os.getenv("MAX_TOKENS", 750))
    overlap_tokens: int = int(os.getenv("OVERLAP_TOKENS", 150))
    token_encoding_name: str = os.getenv("TOKEN_ENCODING", "cl100k_base")

    # batch size for API calls
    batch_size: int = int(os.getenv("BATCH_SIZE", 128))

    # caching
    cache_dir: str = os.getenv("CACHE_DIR", ".chunk_cache")

    # SemanticChunker tuning
    semantic_buffer_size: int = int(os.getenv("SEMANTIC_BUFFER_SIZE", 1))
    semantic_breakpoint_type: str = os.getenv("SEMANTIC_BREAKPOINT_TYPE", "percentile")
    semantic_breakpoint_amount: Optional[float] = _optional_float("SEMANTIC_BREAKPOINT_AMOUNT")
