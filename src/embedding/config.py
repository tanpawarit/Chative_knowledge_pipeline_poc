import os
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv


load_dotenv()


@dataclass
class MilvusSettings:
    uri: str = os.getenv("MILVUS_ADDR", "")
    username: str = os.getenv("MILVUS_USERNAME", "")
    password: str = os.getenv("MILVUS_PASSWORD", "")
    collection_name: str = os.getenv("MILVUS_COLLECTION", "")
    # If set, enables partition-key routing using a dedicated field in the schema.
    # The value here is the partition key value to write on each row (e.g., tenant/workspace id).
    partition_key_value: str = os.getenv("MILVUS_PARTITION_KEY", "")
    dense_metric: str = os.getenv("MILVUS_DENSE_METRIC", "COSINE")
    sparse_metric: str = os.getenv("MILVUS_SPARSE_METRIC", "BM25")
    consistency_level: str = os.getenv("MILVUS_CONSISTENCY_LEVEL", "Bounded")


    def token(self) -> Optional[str]:
        if self.username or self.password:
            if self.username:
                return f"{self.username}:{self.password}"
            return self.password or None
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
    api_key: str = os.getenv("GEMINI_API_KEY", "")
    model: str = os.getenv("GEMINI_EMBED_MODEL", "models/text-embedding-004")
    batch_size: int = int(os.getenv("BATCH_SIZE", 128))
    milvus: MilvusSettings = field(default_factory=MilvusSettings)


    def ensure_api_key(self) -> str:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is required")
        return self.api_key
