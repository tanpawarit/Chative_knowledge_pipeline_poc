import os

# Quiet noisy gRPC warnings about ALTS credentials when running outside GCP.
os.environ.setdefault("GRPC_VERBOSITY", "NONE")
os.environ.setdefault("GRPC_LOG_SEVERITY", "ERROR")
os.environ.setdefault("ABSL_LOGGING_STDERR_THRESHOLD", "3")

from typing import List

import google.generativeai as genai
import numpy as np

from src.chunking.config import Settings


class GeminiEmbedder:
    def __init__(self, settings: Settings):
        if not settings.genai_api_key:
            raise RuntimeError("GEMINI_API_KEY is required")
        genai.configure(api_key=settings.genai_api_key)
        self.model = settings.model_emb
        self.bs = settings.batch_size


    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        if not texts:
            return []
        out: List[np.ndarray] = []
        B = self.bs
        for i in range(0, len(texts), B):
            batch = texts[i:i + B]
            for item in batch:
                resp = genai.embed_content(model=self.model, content=item)
                out.append(np.array(resp["embedding"], dtype=np.float32))
        return out
