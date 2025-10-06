"""Shared configuration helpers for the pipeline components."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv


load_dotenv()


def _str_env(key: str, default: str = "") -> str:
    value = os.getenv(key)
    if value is None:
        return default
    value = value.strip()
    return value if value else default


def _int_env(key: str, default: int) -> int:
    value = _str_env(key, "")
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _float_env(key: str, default: float) -> float:
    value = _str_env(key, "")
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _optional_float_env(key: str) -> Optional[float]:
    value = _str_env(key, "")
    if not value or value.lower() == "auto":
        return None
    try:
        return float(value)
    except ValueError:
        return None


@dataclass
class MilvusSettings:
    uri: str = field(default_factory=lambda: _str_env("MILVUS_ADDR"))
    username: str = field(default_factory=lambda: _str_env("MILVUS_USERNAME"))
    password: str = field(default_factory=lambda: _str_env("MILVUS_PASSWORD"))
    collection_name: str = field(default_factory=lambda: _str_env("MILVUS_COLLECTION"))
    partition_key_value: str = field(default_factory=lambda: _str_env("MILVUS_PARTITION_KEY"))
    dense_metric: str = field(default_factory=lambda: _str_env("MILVUS_DENSE_METRIC", "COSINE"))
    sparse_metric: str = field(default_factory=lambda: _str_env("MILVUS_SPARSE_METRIC", "IP"))
    consistency_level: str = field(default_factory=lambda: _str_env("MILVUS_CONSISTENCY_LEVEL", "Bounded"))

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
    api_key: str = field(default_factory=lambda: _str_env("GEMINI_API_KEY"))
    model: str = field(default_factory=lambda: _str_env("GEMINI_EMBED_MODEL", "models/text-embedding-004"))
    batch_size: int = field(default_factory=lambda: _int_env("BATCH_SIZE", 128))
    milvus: MilvusSettings = field(default_factory=MilvusSettings)
    embed_price_per_million_tokens: Optional[float] = field(
        default_factory=lambda: _optional_float_env("GEMINI_EMBED_USD_PER_MILLION")
    )

    def ensure_api_key(self) -> str:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is required")
        return self.api_key


@dataclass
class ChunkingSettings:
    embedding: EmbeddingSettings = field(default_factory=EmbeddingSettings)
    presplit_min_chars: int = field(default_factory=lambda: _int_env("PRESPLIT_MIN_CHARS", 1200))
    presplit_overlap_chars: int = field(default_factory=lambda: _int_env("PRESPLIT_OVERLAP_CHARS", 0))
    min_chars_per_subchunk: int = field(default_factory=lambda: _int_env("MIN_CHARS", 400))
    semantic_buffer_size: int = field(default_factory=lambda: _int_env("SEMANTIC_BUFFER_SIZE", 1))
    semantic_breakpoint_type: str = field(default_factory=lambda: _str_env("SEMANTIC_BREAKPOINT_TYPE", "percentile"))
    semantic_breakpoint_amount: Optional[float] = field(
        default_factory=lambda: _optional_float_env("SEMANTIC_BREAKPOINT_AMOUNT")
    )


@dataclass
class ExtractionSettings:
    ocr_model: str = field(default_factory=lambda: _str_env("MISTRAL_OCR_MODEL", "mistral-ocr-latest"))
    picture_model: str = field(default_factory=lambda: _str_env("MISTRAL_PICTURE_MODEL", "pixtral-12b"))
    picture_prompt: str = field(
        default_factory=lambda: _str_env(
            "MISTRAL_PICTURE_PROMPT",
            "Summarize the picture in 2-3 sentences, capturing layout, text, and key visuals.",
        )
    )
    ocr_cost_per_page: float = field(default_factory=lambda: _float_env("MISTRAL_OCR_COST_PER_PAGE", 0.005))
    picture_input_cost_per_million: float = field(
        default_factory=lambda: _float_env("MISTRAL_PICTURE_INPUT_COST_PER_MILLION", 1.8)
    )
    picture_output_cost_per_million: float = field(
        default_factory=lambda: _float_env("MISTRAL_PICTURE_OUTPUT_COST_PER_MILLION", 5.4)
    )


__all__ = [
    "MilvusSettings",
    "EmbeddingSettings",
    "ChunkingSettings",
    "ExtractionSettings",
]
