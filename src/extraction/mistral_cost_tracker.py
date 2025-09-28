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
class ChatPricing:
    """Pricing for chat or vision models, in USD per million tokens."""

    input_usd_per_million: float
    output_usd_per_million: float


@dataclass(frozen=True)
class OcrPricing:
    """Pricing for OCR models, in USD per processed page."""

    per_page_usd: float


@dataclass
class ChatUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    calls: int = 0
    estimated_cost_usd: float = 0.0


@dataclass
class OcrUsage:
    pages_processed: int = 0
    calls: int = 0
    estimated_cost_usd: float = 0.0


def _as_int(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, (int, float)) and not math.isnan(value):
        return int(value)
    if isinstance(value, str) and value.strip():
        try:
            return int(float(value))
        except ValueError:  # pragma: no cover - defensive parsing
            return 0
    if isinstance(value, Mapping):
        return _as_int(value.get("value"))
    return 0


def _get_usage_attribute(usage: Any, key: str) -> int:
    if usage is None:
        return 0
    if isinstance(usage, Mapping):
        return _as_int(usage.get(key))
    return _as_int(getattr(usage, key, 0))


class MistralCostTracker:
    """Collects per-model usage statistics and estimates API costs."""

    def __init__(
        self,
        *,
        chat_pricing: Optional[Mapping[str, ChatPricing]] = None,
        ocr_pricing: Optional[Mapping[str, OcrPricing]] = None,
    ) -> None:
        self._lock = Lock()
        self._chat_usage: Dict[str, ChatUsage] = {}
        self._ocr_usage: Dict[str, OcrUsage] = {}
        self._chat_pricing: Dict[str, ChatPricing] = dict(chat_pricing or {})
        self._ocr_pricing: Dict[str, OcrPricing] = dict(ocr_pricing or {})

    # --- configuration ----------------------------------------------------------------
    def configure_chat_pricing(self, model: str, pricing: ChatPricing) -> None:
        with self._lock:
            self._chat_pricing[model] = pricing

    def configure_ocr_pricing(self, model: str, pricing: OcrPricing) -> None:
        with self._lock:
            self._ocr_pricing[model] = pricing

    def configure_from_environment(self, env_var: str = "MISTRAL_PRICE_OVERRIDES") -> None:
        raw = os.getenv(env_var)
        if not raw:
            return

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            _log.warning("Failed to parse %%s; expected JSON object", env_var)
            return

        if not isinstance(payload, Mapping):
            _log.warning(
                "Unexpected pricing overrides format (expected mapping, got %s)",
                type(payload).__name__,
            )
            return

        chat_section = payload.get("chat")
        if isinstance(chat_section, Mapping):
            for model, data in chat_section.items():
                if not isinstance(data, Mapping):
                    continue
                try:
                    input_rate = float(data["input_usd_per_million"])
                    output_rate = float(
                        data.get("output_usd_per_million", input_rate)
                    )
                except (KeyError, TypeError, ValueError):  # pragma: no cover - defensive
                    _log.warning(
                        "Invalid chat pricing override for model %s", model
                    )
                    continue
                self.configure_chat_pricing(
                    model,
                    ChatPricing(
                        input_usd_per_million=input_rate,
                        output_usd_per_million=output_rate,
                    ),
                )

        ocr_section = payload.get("ocr")
        if isinstance(ocr_section, Mapping):
            for model, data in ocr_section.items():
                if not isinstance(data, Mapping):
                    continue
                try:
                    per_page = float(data["per_page_usd"])
                except (KeyError, TypeError, ValueError):  # pragma: no cover - defensive
                    _log.warning(
                        "Invalid OCR pricing override for model %s", model
                    )
                    continue
                self.configure_ocr_pricing(model, OcrPricing(per_page_usd=per_page))

    # --- recording --------------------------------------------------------------------
    def record_chat_completion(self, model: str, usage: Any) -> None:
        prompt_tokens = _get_usage_attribute(usage, "prompt_tokens")
        completion_tokens = _get_usage_attribute(usage, "completion_tokens")
        total_tokens = _get_usage_attribute(usage, "total_tokens")

        with self._lock:
            stats = self._chat_usage.setdefault(model, ChatUsage())
            stats.prompt_tokens += prompt_tokens
            stats.completion_tokens += completion_tokens
            stats.total_tokens += max(total_tokens, prompt_tokens + completion_tokens)
            stats.calls += 1

            pricing = self._chat_pricing.get(model) or self._chat_pricing.get("*")
            if pricing:
                stats.estimated_cost_usd += self._estimate_chat_cost(
                    prompt_tokens, completion_tokens, pricing
                )

    def record_ocr(self, model: str, pages_processed: Optional[int]) -> None:
        pages = pages_processed or 0
        if pages <= 0:
            return

        with self._lock:
            stats = self._ocr_usage.setdefault(model, OcrUsage())
            stats.pages_processed += pages
            stats.calls += 1

            pricing = self._ocr_pricing.get(model) or self._ocr_pricing.get("*")
            if pricing:
                stats.estimated_cost_usd += pricing.per_page_usd * pages

    # --- reporting --------------------------------------------------------------------
    def report(self) -> Dict[str, Any]:
        with self._lock:
            chat_report = {
                model: {
                    **asdict(usage),
                    "pricing": asdict(self._chat_pricing.get(model))
                    if model in self._chat_pricing
                    else asdict(self._chat_pricing.get("*"))
                    if "*" in self._chat_pricing
                    else None,
                }
                for model, usage in sorted(
                    self._chat_usage.items(),
                    key=lambda item: item[1].estimated_cost_usd,
                    reverse=True,
                )
            }

            ocr_report = {
                model: {
                    **asdict(usage),
                    "pricing": asdict(self._ocr_pricing.get(model))
                    if model in self._ocr_pricing
                    else asdict(self._ocr_pricing.get("*"))
                    if "*" in self._ocr_pricing
                    else None,
                }
                for model, usage in sorted(
                    self._ocr_usage.items(),
                    key=lambda item: item[1].estimated_cost_usd,
                    reverse=True,
                )
            }

            total_cost = sum(
                usage["estimated_cost_usd"] for usage in chat_report.values()
            ) + sum(usage["estimated_cost_usd"] for usage in ocr_report.values())

            return {
                "chat": chat_report,
                "ocr": ocr_report,
                "total_cost_usd": total_cost,
            }

    def format_report(self) -> str:
        report = self.report()
        if not report["chat"] and not report["ocr"]:
            return "Mistral API usage: no tracked calls."

        lines = ["Mistral API usage:"]

        if report["chat"]:
            lines.append("- Chat / vision models:")
            for model, stats in report["chat"].items():
                pricing = stats.get("pricing")
                cost = stats["estimated_cost_usd"]
                price_hint = (
                    f" @ ${pricing['input_usd_per_million']:.4f} / ${pricing['output_usd_per_million']:.4f} per 1M tokens"
                    if pricing
                    else " (pricing not set)"
                )
                lines.append(
                    f"  • {model}: {stats['calls']} calls, {stats['prompt_tokens']} prompt + {stats['completion_tokens']} completion tokens => ${cost:.6f}{price_hint}"
                )
        else:
            lines.append("- Chat / vision models: none")

        if report["ocr"]:
            lines.append("- OCR models:")
            for model, stats in report["ocr"].items():
                pricing = stats.get("pricing")
                cost = stats["estimated_cost_usd"]
                price_hint = (
                    f" @ ${pricing['per_page_usd']:.6f} per page"
                    if pricing
                    else " (pricing not set)"
                )
                lines.append(
                    f"  • {model}: {stats['pages_processed']} pages across {stats['calls']} calls => ${cost:.6f}{price_hint}"
                )
        else:
            lines.append("- OCR models: none")

        lines.append(f"- Total estimated cost: ${report['total_cost_usd']:.6f}")
        return "\n".join(lines)

    def reset(self) -> None:
        with self._lock:
            self._chat_usage.clear()
            self._ocr_usage.clear()

    # --- helpers ----------------------------------------------------------------------
    @staticmethod
    def _estimate_chat_cost(
        prompt_tokens: int, completion_tokens: int, pricing: ChatPricing
    ) -> float:
        return (
            (prompt_tokens / _MILLION) * pricing.input_usd_per_million
            + (completion_tokens / _MILLION) * pricing.output_usd_per_million
        )


# Default instance shared across the project (values sourced from
# https://docs.mistral.ai/platform/pricing, retrieved October 2024).
_default_chat_pricing: Dict[str, ChatPricing] = {
    "pixtral-12b": ChatPricing(
        input_usd_per_million=0.15,
        output_usd_per_million=0.15,
    ),
}
_default_ocr_pricing: Dict[str, OcrPricing] = {
    "mistral-ocr-latest": OcrPricing(per_page_usd=0.001),
}

mistral_cost_tracker = MistralCostTracker(
    chat_pricing=_default_chat_pricing,
    ocr_pricing=_default_ocr_pricing,
)

# Apply environment overrides eagerly so any consumer sees configured pricing
mistral_cost_tracker.configure_from_environment()


__all__ = [
    "ChatPricing",
    "OcrPricing",
    "MistralCostTracker",
    "mistral_cost_tracker",
]
