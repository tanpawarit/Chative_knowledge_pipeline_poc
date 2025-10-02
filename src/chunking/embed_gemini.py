import os

# Quiet noisy gRPC warnings about ALTS credentials when running outside GCP.
os.environ.setdefault("GRPC_VERBOSITY", "NONE")
os.environ.setdefault("GRPC_LOG_SEVERITY", "ERROR")
os.environ.setdefault("ABSL_LOGGING_STDERR_THRESHOLD", "3")

from typing import List

import google.generativeai as genai
import numpy as np

from langchain_core.embeddings import Embeddings

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


class GeminiEmbeddings(Embeddings):
    """LangChain-compatible embedding wrapper around `GeminiEmbedder`."""

    def __init__(self, embedder: GeminiEmbedder):
        self._embedder = embedder


    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        vectors = self._embedder.embed_batch(texts)
        return [vec.tolist() for vec in vectors]


    def embed_query(self, text: str) -> List[float]:
        doc_vecs = self.embed_documents([text])
        return doc_vecs[0] if doc_vecs else []
