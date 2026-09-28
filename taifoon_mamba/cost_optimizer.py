"""
Cost optimizer — routes each brief to an (agent_slug, model) pair based on category.

Routing table (the first segment of the category; a "-replay" suffix matches its chain, so "sol-replay" → sol):
    evm, sol, btc, cosmos, lambda-replay           → coder / claude-sonnet-5
    oracle, aggregator, platform-phase5/phase6     → coder / claude-opus-5-5   (high-complexity work)
    <unknown>                                      → coder / claude-sonnet-5   (safe fallback)

weight_tuning() keeps a running score per category from past outcomes; it does not change routes yet.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SONNET = "claude-sonnet-5"
OPUS   = "claude-opus-5-5"

_ROUTING_TABLE: dict[str, tuple[str, str]] = {
    "evm":              ("coder", SONNET),
    "sol":              ("coder", SONNET),
    "btc":              ("coder", SONNET),
    "cosmos":           ("coder", SONNET),
    "lambda-replay":    ("coder", SONNET),
    "oracle":           ("coder", OPUS),
    "aggregator":       ("coder", OPUS),
    "platform-phase5":  ("coder", OPUS),
    "platform-phase6":  ("coder", OPUS),
}

_FALLBACK: tuple[str, str] = ("coder", SONNET)


@dataclass
class CostOptimizer:
    """Routes briefs to (agent_slug, model) pairs and tunes weights from history."""

    weights: dict[str, float] = field(default_factory=dict)

    def route(self, brief: dict[str, Any]) -> tuple[str, str]:
        """Return (agent_slug, model) for *brief*.

        The category field uses slash-separated paths, e.g. ``"evm/eth"``.
        Only the first segment is matched against the routing table.
        """
        raw_category: str = brief.get("category", "")
        root = raw_category.split("/")[0].lower()
        if root in _ROUTING_TABLE:
            return _ROUTING_TABLE[root]
        return _ROUTING_TABLE.get(root.removesuffix("-replay"), _FALLBACK)

    def weight_tuning(self, history: list[dict[str, Any]]) -> dict[str, Any]:
        """Accept historical task outcomes and return updated routing weights.

        A running average of the verdict score per category (approved 1.0, changes requested 0.5,
        blocked 0.0). Routes do not read these weights yet.

        Args:
            history: list of dicts with at least ``category``, ``cost_usd``,
                     ``verdict`` (``"approved"`` / ``"changes_requested"`` /
                     ``"blocked"``).

        Returns:
            dict mapping category → weight float in [0, 1].
        """
        updated: dict[str, float] = {}
        for record in history:
            cat = str(record.get("category", "")).split("/")[0].lower()
            verdict = str(record.get("verdict", "")).lower()
            score = 1.0 if verdict == "approved" else 0.5 if verdict == "changes_requested" else 0.0
            prev = updated.get(cat, self.weights.get(cat, 1.0))
            updated[cat] = round((prev + score) / 2, 4)
        self.weights.update(updated)
        return dict(self.weights)
