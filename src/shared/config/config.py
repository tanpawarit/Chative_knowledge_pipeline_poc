"""Shared configuration helpers for the pipeline components."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from src.shared.config.env import (
    MissingEnvironmentVariable,
    optional_env,
    optional_float_env,
    require_env,
    require_float_env,
    require_int_env,
)


DEFAULT_MISTRAL_PICTURE_PROMPT = (
    "Summarize the picture in 2-3 sentences, capturing layout, text, and key visuals."
)


def _semantic_breakpoint_amount_env() -> Optional[float]:
    value = optional_env("SEMANTIC_BREAKPOINT_AMOUNT")
    if value is None:
        return None
    if value.lower() == "auto":
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise MissingEnvironmentVariable(
            "SEMANTIC_BREAKPOINT_AMOUNT must be a float or 'auto'"
        ) from exc


@dataclass
class MilvusSettings:
    uri: str = field(default_factory=lambda: require_env("MILVUS_ADDR"))
    username: str = field(default_factory=lambda: require_env("MILVUS_USERNAME"))
    password: str = field(default_factory=lambda: require_env("MILVUS_PASSWORD"))
    collection_name: str = field(default_factory=lambda: require_env("MILVUS_COLLECTION"))
    partition_key_value: Optional[str] = field(
        default_factory=lambda: optional_env("MILVUS_PARTITION_KEY")
    )
    dense_metric: str = field(default_factory=lambda: require_env("MILVUS_DENSE_METRIC"))
    sparse_metric: str = field(default_factory=lambda: require_env("MILVUS_SPARSE_METRIC"))
    consistency_level: str = field(
        default_factory=lambda: require_env("MILVUS_CONSISTENCY_LEVEL")
    )

    def token(self) -> Optional[str]:
        if self.username and self.password:
            return f"{self.username}:{self.password}"
        if self.username or self.password:
            return self.username or self.password or None
        return None

    def is_configured(self) -> bool:
        return bool(self.uri and self.collection_name)

    def ensure_ready(self) -> "MilvusSettings":
        if not self.uri:
            raise RuntimeError("MILVUS_ADDR is required to connect to Milvus")
        if not self.collection_name:
            raise RuntimeError("MILVUS_COLLECTION is required to connect to Milvus")
        return self


@dataclass
class EmbeddingSettings:
    api_key: Optional[str] = None
    model: Optional[str] = None
    batch_size: int = field(default_factory=lambda: require_int_env("BATCH_SIZE"))
    milvus: MilvusSettings = field(default_factory=MilvusSettings)
    embed_price_per_million_tokens: Optional[float] = field(
        default_factory=lambda: optional_float_env("OPENAI_EMBED_USD_PER_MILLION")
    )

    def __post_init__(self) -> None:
        if not self.api_key:
            self.api_key = require_env("OPENAI_API_KEY")
        if not self.model:
            self.model = require_env("OPENAI_EMBED_MODEL")

        if not self.api_key:
            raise MissingEnvironmentVariable("Embedding API key is required")
        if not self.model:
            raise MissingEnvironmentVariable("Embedding model is required")

    def ensure_api_key(self) -> str:
        if not self.api_key:
            raise RuntimeError("Embedding API key is required for embedding calls")
        return self.api_key


@dataclass
class ChunkingSettings:
    embedding: EmbeddingSettings = field(default_factory=EmbeddingSettings)
    presplit_min_chars: int = field(default_factory=lambda: require_int_env("PRESPLIT_MIN_CHARS"))
    presplit_overlap_chars: int = field(
        default_factory=lambda: require_int_env("PRESPLIT_OVERLAP_CHARS")
    )
    min_chars_per_subchunk: int = field(default_factory=lambda: require_int_env("MIN_CHARS"))
    semantic_buffer_size: int = field(default_factory=lambda: require_int_env("SEMANTIC_BUFFER_SIZE"))
    semantic_breakpoint_type: str = field(
        default_factory=lambda: require_env("SEMANTIC_BREAKPOINT_TYPE")
    )
    semantic_breakpoint_amount: Optional[float] = field(
        default_factory=_semantic_breakpoint_amount_env
    )


@dataclass
class ExtractionSettings:
    ocr_model: str = field(default_factory=lambda: require_env("MISTRAL_OCR_MODEL"))
    picture_model: str = field(default_factory=lambda: require_env("MISTRAL_PICTURE_MODEL"))
    picture_prompt: str = field(default=DEFAULT_MISTRAL_PICTURE_PROMPT)
    ocr_cost_per_page: float = field(
        default_factory=lambda: require_float_env("MISTRAL_OCR_COST_PER_PAGE")
    )
    picture_input_cost_per_million: float = field(
        default_factory=lambda: require_float_env("MISTRAL_PICTURE_INPUT_COST_PER_MILLION")
    )
    picture_output_cost_per_million: float = field(
        default_factory=lambda: require_float_env("MISTRAL_PICTURE_OUTPUT_COST_PER_MILLION")
    )


__all__ = [
    "MilvusSettings",
    "EmbeddingSettings",
    "ChunkingSettings",
    "ExtractionSettings",
]
