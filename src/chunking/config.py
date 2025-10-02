import os
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv

from src.embedding.config import EmbeddingSettings


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
class ChunkingSettings:
    embedding: EmbeddingSettings = field(default_factory=EmbeddingSettings)

    min_chars_per_subchunk: int = int(os.environ["MIN_CHARS"])
    overlap_chars: int = int(os.environ["OVERLAP_CHARS"])
    cohesion_drop: float = float(os.environ["COHESION_DROP"])

    # token-based sizing via TokenTextSplitter
    max_tokens_per_subchunk: int = int(os.environ["MAX_TOKENS"])
    overlap_tokens: int = int(os.environ["OVERLAP_TOKENS"])
    token_encoding_name: str = os.environ["TOKEN_ENCODING"]
    
    # SemanticChunker tuning
    semantic_buffer_size: int = int(os.environ["SEMANTIC_BUFFER_SIZE"])
    semantic_breakpoint_type: str = os.environ["SEMANTIC_BREAKPOINT_TYPE"]
    semantic_breakpoint_amount: Optional[float] = _optional_float("SEMANTIC_BREAKPOINT_AMOUNT")


Settings = ChunkingSettings
