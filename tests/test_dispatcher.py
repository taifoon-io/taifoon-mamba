"""Tests for taifoon_mamba.dispatcher classification and heartbeat logic."""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from taifoon_mamba.dispatcher import _classify, _write_heartbeat

# ---------------------------------------------------------------------------
# _classify tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("desc,expected_cat", [
    ("Solana adapter replay fix", "sol-replay"),
    ("Bitcoin BTC bridge reconciliation", "btc-replay"),
    ("Cosmos IBC relay latency", "cosmos-replay"),
    ("Oracle price feed aggregator", "oracle"),  # "oracle" check comes before "aggregator"
    ("stale oracle feed", "oracle"),
    ("EVM cross-chain bridge", "evm-replay"),
    ("", "evm-replay"),
])
def test_classify_returns_expected_category(desc: str, expected_cat: str) -> None:
    brief = {"description": desc, "title": ""}
    cat, _ = _classify(brief)
    assert cat == expected_cat


def test_classify_volume_class_s_for_oracle() -> None:
    _, vol = _classify({"description": "oracle price feed", "title": ""})
    assert vol == "S"


def test_classify_volume_class_a_for_evm() -> None:
    _, vol = _classify({"description": "EVM relay", "title": ""})
    assert vol == "A"


def test_classify_uses_title_field() -> None:
    brief = {"description": "", "title": "Solana SPL token adapter"}
    cat, _ = _classify(brief)
    assert cat == "sol-replay"


# ---------------------------------------------------------------------------
# _write_heartbeat tests
# ---------------------------------------------------------------------------

def test_write_heartbeat_creates_file(tmp_path: Path) -> None:
    hb = tmp_path / "heartbeat.json"

    import taifoon_mamba.dispatcher as mod
    original = mod.HEARTBEAT
    mod.HEARTBEAT = hb
    try:
        _write_heartbeat(tick=1, jph=12.5)
        assert hb.exists()
        data = json.loads(hb.read_text())
        assert data["tick_count"] == 1
        assert abs(data["jobs_per_hour"] - 12.5) < 1e-6
        assert data["last_tick_ms"] <= int(time.time() * 1000) + 100
    finally:
        mod.HEARTBEAT = original


@pytest.mark.parametrize("desc", ["a solution for the relayer", "console output cleanup", "debtc ledger"])
def test_classify_matches_whole_words_only(desc: str) -> None:
    cat, _ = _classify({"description": desc, "title": ""})
    assert cat == "evm-replay"


def test_every_category_reaches_a_route_not_the_fallback() -> None:
    from taifoon_mamba.cost_optimizer import _ROUTING_TABLE, CostOptimizer
    router = CostOptimizer()
    for desc in ["solana", "bitcoin", "cosmos", "oracle", "aggregator", "evm bridge"]:
        cat, _ = _classify({"description": desc, "title": ""})
        assert router.route({"category": cat}) in _ROUTING_TABLE.values()
        root = cat.split("/")[0]
        assert root in _ROUTING_TABLE or root.removesuffix("-replay") in _ROUTING_TABLE


def test_process_queue_routes_queued_briefs_once(tmp_path: Path) -> None:
    import taifoon_mamba.dispatcher as mod
    from taifoon_mamba.cost_optimizer import OPUS, CostOptimizer
    q = tmp_path / "queue.jsonl"
    q.write_text("\n".join([
        json.dumps({"job_id": "j1", "title": "stale oracle feed", "status": "queued"}),
        json.dumps({"job_id": "j2", "title": "done already", "status": "closed"}),
        "not json",
        json.dumps({"title": "no id", "status": "queued"}),
    ]))
    original = mod.QUEUE_FILE
    mod.QUEUE_FILE = q
    try:
        seen: set[str] = set()
        router = CostOptimizer()
        first = mod.process_queue(seen, router)
        assert [d["job_id"] for d in first] == ["j1"]
        assert first[0]["category"] == "oracle" and first[0]["model"] == OPUS
        assert mod.process_queue(seen, router) == []          # already seen
    finally:
        mod.QUEUE_FILE = original


def test_watch_once_writes_a_heartbeat(tmp_path: Path) -> None:
    import taifoon_mamba.dispatcher as mod
    originals = (mod.QUEUE_FILE, mod.HEARTBEAT)
    mod.QUEUE_FILE, mod.HEARTBEAT = tmp_path / "d" / "queue.jsonl", tmp_path / "d" / "heartbeat.json"
    try:
        mod.watch_loop(once=True)
        assert json.loads(mod.HEARTBEAT.read_text())["tick_count"] == 1
    finally:
        mod.QUEUE_FILE, mod.HEARTBEAT = originals


def test_synthetic_runs_standalone(tmp_path: Path) -> None:
    import taifoon_mamba.dispatcher as mod
    from taifoon_mamba import synthetic
    original = mod.HEARTBEAT
    mod.HEARTBEAT = tmp_path / "heartbeat.json"
    try:
        assert synthetic.run(interval_s=0.001, ticks=3, seed=1) == 3
        data = json.loads(mod.HEARTBEAT.read_text())
        assert data["tick_count"] == 3 and 4 <= data["jobs_per_hour"] <= 20
    finally:
        mod.HEARTBEAT = original


def test_once_reports_a_sane_rate(tmp_path: Path) -> None:
    import taifoon_mamba.dispatcher as mod
    originals = (mod.QUEUE_FILE, mod.HEARTBEAT)
    mod.QUEUE_FILE, mod.HEARTBEAT = tmp_path / "queue.jsonl", tmp_path / "heartbeat.json"
    mod.QUEUE_FILE.write_text(json.dumps({"job_id": "j1", "title": "oracle", "status": "queued"}))
    try:
        mod.watch_loop(once=True)
        assert json.loads(mod.HEARTBEAT.read_text())["jobs_per_hour"] == 60.0   # 1 job over the one-minute floor
    finally:
        mod.QUEUE_FILE, mod.HEARTBEAT = originals
