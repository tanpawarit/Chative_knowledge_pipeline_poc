import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    genai_api_key: str = os.getenv("GEMINI_API_KEY", "")
    model_emb: str = os.getenv("GEMINI_EMBED_MODEL", "models/text-embedding-004")

    # token-based sizing via TokenTextSplitter
    max_tokens_per_subchunk: int = int(os.getenv("MAX_TOKENS", 900))
    overlap_tokens: int = int(os.getenv("OVERLAP_TOKENS", 100))
    token_encoding_name: str = os.getenv("TOKEN_ENCODING", "cl100k_base")

    # sentence-level semantic chunking controls
    chunking_mode: str = os.getenv("CHUNKING_MODE", "token")
    semantic_cohesion_drop: float = float(os.getenv("COHESION_DROP", 0.12))
    semantic_min_tokens: int = int(os.getenv("SEMANTIC_MIN_TOKENS", 150))
    semantic_sentence_overlap: int = int(os.getenv("SENTENCE_OVERLAP", 0))

    # batch size for API calls
    batch_size: int = int(os.getenv("BATCH_SIZE", 64))

    # caching
    cache_dir: str = os.getenv("CACHE_DIR", ".chunk_cache")
