import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass
class EmbeddingSettings:
    api_key: str = os.getenv("GEMINI_API_KEY", "")
    model: str = os.getenv("GEMINI_EMBED_MODEL", "models/text-embedding-004")
    batch_size: int = int(os.getenv("BATCH_SIZE", 128))


    def ensure_api_key(self) -> str:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is required")
        return self.api_key
