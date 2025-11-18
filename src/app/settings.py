"""Application-specific configuration wrappers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from src.shared.config.config import ChunkingSettings, EmbeddingSettings, MilvusSettings
from src.shared.config.env import optional_env


@dataclass
class QstashSignatureSettings:
    """Holds signing keys used to verify QStash webhook requests."""

    current_signing_key: Optional[str] = field(
        default_factory=lambda: optional_env("QSTASH_CURRENT_SIGNING_KEY")
    )
    next_signing_key: Optional[str] = field(
        default_factory=lambda: optional_env("QSTASH_NEXT_SIGNING_KEY")
    )

    def is_enabled(self) -> bool:
        return bool(self.current_signing_key and self.next_signing_key)


@dataclass
class AppSettings:
    """Bundle together the settings the FastAPI app depends on."""

    qstash_signature: QstashSignatureSettings = field(
        default_factory=QstashSignatureSettings
    )
    chunking: ChunkingSettings = field(default_factory=ChunkingSettings)
    embedding: EmbeddingSettings = field(default_factory=EmbeddingSettings)
    milvus: MilvusSettings = field(default_factory=MilvusSettings)
