"""Factory helpers for configuring embedding runtimes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Protocol, Sequence

from langchain_core.embeddings import Embeddings

from src.shared.cost_management.openai_cost_tracker import openai_cost_tracker
from src.shared.config.config import EmbeddingSettings
from src.shared.embeddings.providers import OpenAIEmbedder, OpenAIEmbeddings
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class BatchEmbedder(Protocol):
    """Protocol describing batch embedding behavior."""

    def embed_batch(self, texts: List[str]) -> List[Sequence[float]]:
        ...


@dataclass
class EmbeddingRuntime:
    """Container holding cohesive embedding utilities for callers."""

    client: BatchEmbedder
    embeddings: Embeddings
    reset_usage: Callable[[], None]
    usage_report: Callable[[], str]


def create_embedding_runtime(settings: EmbeddingSettings) -> EmbeddingRuntime:
    """Instantiate embedder + LangChain bindings + cost hooks."""

    embedder = OpenAIEmbedder(settings)
    embeddings = OpenAIEmbeddings(embedder)

    def _reset() -> None:
        openai_cost_tracker.reset()
        openai_cost_tracker.configure_from_environment()

    def _report() -> str:
        return openai_cost_tracker.format_report()

    logger.debug(
        "Initialized OpenAI embedding runtime", model=settings.model
    )
    return EmbeddingRuntime(
        client=embedder,
        embeddings=embeddings,
        reset_usage=_reset,
        usage_report=_report,
    )


__all__ = ["EmbeddingRuntime", "create_embedding_runtime"]
