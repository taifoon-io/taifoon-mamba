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
