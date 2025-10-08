from __future__ import annotations

import json
import logging
import math
import os
from dataclasses import asdict, dataclass
from threading import Lock
from typing import Any, Dict, Mapping, Optional

_log = logging.getLogger(__name__)

_MILLION = 1_000_000


@dataclass(frozen=True)
class EmbeddingPricing:
    """Pricing for OpenAI embedding models, in USD per million tokens."""

    usd_per_million_tokens: float


@dataclass
class EmbeddingUsage:
    tokens: int = 0
    calls: int = 0
    estimated_cost_usd: float = 0.0
    approximate_tokens: int = 0


def _safe_int(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return 0
        return int(value)
    if isinstance(value, str) and value.strip():
        try:
            return int(float(value))
        except ValueError:  # pragma: no cover - defensive parsing
            return 0
    if isinstance(value, Mapping):
        return _safe_int(value.get("value"))
    return 0


def _lookup_usage_token_count(usage: Any) -> int:
    if usage is None:
        return 0
    if isinstance(usage, Mapping):
        for key in ("total_tokens", "prompt_tokens", "input_tokens"):
            if key in usage:
                return _safe_int(usage.get(key))
        metadata = usage.get("usage_metadata")
        if isinstance(metadata, Mapping):
            return _lookup_usage_token_count(metadata)
    return (
        _safe_int(getattr(usage, "total_tokens", 0))
        or _safe_int(getattr(usage, "prompt_tokens", 0))
        or _safe_int(getattr(usage, "input_tokens", 0))
    )


def _estimate_tokens_from_text(text: Optional[str]) -> int:
    if not text:
        return 0
    approx = int(math.ceil(len(text) / 4.0))
    if approx <= 0 and text.strip():  # pragma: no cover - defensive guard
        return len(text.split()) or 1
    return max(approx, 0)


class OpenAIEmbeddingCostTracker:
    """Collect usage statistics and cost estimates for OpenAI embeddings."""

    def __init__(
        self, *, pricing: Optional[Mapping[str, EmbeddingPricing]] = None
    ) -> None:
        self._lock = Lock()
        self._pricing: Dict[str, EmbeddingPricing] = dict(pricing or {})
        self._usage: Dict[str, EmbeddingUsage] = {}

    # --- configuration ----------------------------------------------------------------
    def configure_pricing(self, model: str, pricing: EmbeddingPricing) -> None:
        with self._lock:
            self._pricing[model] = pricing

    def configure_from_environment(
        self, env_var: str = "OPENAI_EMBED_PRICE_OVERRIDES"
    ) -> None:
        raw = os.getenv(env_var)
        if not raw:
            return

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            _log.warning("Failed to parse %s; expected JSON object", env_var)
            return

        if not isinstance(payload, Mapping):
            _log.warning(
                "Unexpected pricing overrides format (expected mapping, got %s)",
                type(payload).__name__,
            )
            return

        for model, data in payload.items():
            if not isinstance(data, Mapping):
                continue
            try:
                usd_per_million = float(data["usd_per_million_tokens"])
            except (KeyError, TypeError, ValueError):
                _log.warning(
                    "Invalid OpenAI embed pricing override for model %s", model
                )
                continue
            self.configure_pricing(
                model,
                EmbeddingPricing(usd_per_million_tokens=usd_per_million),
            )

    # --- recording --------------------------------------------------------------------
    def record_embedding(
        self,
        model: str,
        *,
        response_usage: Optional[Any] = None,
        token_count: Optional[int] = None,
        text: Optional[str] = None,
    ) -> None:
        tokens = token_count or _lookup_usage_token_count(response_usage)
        approximate = 0
        if tokens <= 0:
            approximate = _estimate_tokens_from_text(text)
            tokens = approximate

        with self._lock:
            stats = self._usage.setdefault(model, EmbeddingUsage())
            stats.calls += 1
            stats.tokens += max(tokens, 0)
            if approximate > 0:
                stats.approximate_tokens += approximate

            pricing = self._pricing.get(model) or self._pricing.get("*")
            if pricing and tokens > 0:
                stats.estimated_cost_usd += self._estimate_cost(tokens, pricing)

    # --- reporting --------------------------------------------------------------------
    def report(self) -> Dict[str, Any]:
        with self._lock:
            report = {
                model: {
                    **asdict(usage),
                    "pricing": asdict(self._pricing.get(model))
                    if model in self._pricing
                    else asdict(self._pricing.get("*"))
                    if "*" in self._pricing
                    else None,
                }
                for model, usage in sorted(
                    self._usage.items(),
                    key=lambda item: item[1].estimated_cost_usd,
                    reverse=True,
                )
            }
            total_cost = sum(data["estimated_cost_usd"] for data in report.values())
            total_tokens = sum(data["tokens"] for data in report.values())
            return {
                "models": report,
                "total_cost_usd": total_cost,
                "total_tokens": total_tokens,
            }

    def format_report(self) -> str:
        report = self.report()
        models = report["models"]
        if not models:
            return "OpenAI embedding usage: no tracked calls."

        lines = ["OpenAI embedding usage:"]
        for model, stats in models.items():
            pricing = stats.get("pricing")
            price_hint = (
                f" @ ${pricing['usd_per_million_tokens']:.6f} per 1M tokens"
                if pricing
                else " (pricing not set)"
            )
            approx_tokens = stats.get("approximate_tokens", 0)
            approx_hint = (
                f", {approx_tokens} tokens estimated"
                if approx_tokens
                else ""
            )
            lines.append(
                f"- {model}: {stats['calls']} calls, {stats['tokens']} tokens{approx_hint} => ${stats['estimated_cost_usd']:.6f}{price_hint}"
            )
        lines.append(
            f"- Total estimated cost: ${report['total_cost_usd']:.6f} across {report['total_tokens']} tokens"
        )
        return "\n".join(lines)

    def reset(self) -> None:
        with self._lock:
            self._usage.clear()

    # --- helpers ----------------------------------------------------------------------
    @staticmethod
    def _estimate_cost(tokens: int, pricing: EmbeddingPricing) -> float:
        return (tokens / _MILLION) * pricing.usd_per_million_tokens


# Default instance shared across the project
_default_openai_pricing: Dict[str, EmbeddingPricing] = {}
_default_price = os.getenv("OPENAI_EMBED_USD_PER_MILLION")
if _default_price:
    try:
        _default_openai_pricing["*"] = EmbeddingPricing(
            usd_per_million_tokens=float(_default_price)
        )
    except ValueError:
        _log.warning(
            "Invalid OPENAI_EMBED_USD_PER_MILLION value: %s", _default_price
        )


openai_cost_tracker = OpenAIEmbeddingCostTracker(pricing=_default_openai_pricing)

openai_cost_tracker.configure_from_environment()


__all__ = [
    "EmbeddingPricing",
    "EmbeddingUsage",
    "OpenAIEmbeddingCostTracker",
    "openai_cost_tracker",
]
