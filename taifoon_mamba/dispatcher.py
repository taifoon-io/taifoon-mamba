"""
taifoon-mamba dispatcher — reads queued job briefs, scopes them into bounties.

Usage:
    python -m taifoon_mamba.dispatcher --watch

Requires:
    TAIFOON_NEXT_DATA_ROOT — path to taifoon-next/.data (default: ../taifoon-next/.data)
    TAIFOON_REGISTRY_ADDR  — BuildersRegistry contract address on devnet
    TAIFOON_RPC_URL        — Taifoon devnet RPC
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from taifoon_mamba.cost_optimizer import CostOptimizer

THIS_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = THIS_DIR.parent

NEXT_DATA = Path(os.environ.get(
    "TAIFOON_NEXT_DATA_ROOT",
    str(REPO_ROOT / "taifoon-next" / ".data"),
))
QUEUE_FILE = NEXT_DATA / "dispatch" / "queue.jsonl"
HEARTBEAT = NEXT_DATA / "dispatch" / "heartbeat.json"


def _ensure_dirs() -> None:
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)


def _write_heartbeat(tick: int, jph: float = 0.0) -> None:
    HEARTBEAT.write_text(json.dumps({
        "last_tick_ms": int(time.time() * 1000),
        "tick_count": tick,
        "jobs_per_hour": jph,
    }, indent=2))


def _classify(brief: dict) -> tuple[str, str]:
    """Returns (category, volume_class). Stub — v0.2 uses nemotron/taifoon."""
    text = (brief.get("description", "") + " " + brief.get("title", "")).lower()
    if "solana" in text or "sol" in text:
        return "sol-replay", "A"
    if "bitcoin" in text or "btc" in text:
        return "btc-replay", "B"
    if "cosmos" in text:
        return "cosmos-replay", "B"
    if "oracle" in text:
        return "oracle", "S"
    if "aggregator" in text:
        return "aggregator", "S"
    return "evm-replay", "A"


def watch_loop(interval_s: int = 5) -> None:
    _ensure_dirs()
    seen: set[str] = set()
    tick = 0
    jobs_dispatched = 0
    start = time.time()
    router = CostOptimizer()

    print(f"taifoon-mamba dispatcher watching {QUEUE_FILE}", file=sys.stderr)

    while True:
        tick += 1
        elapsed = time.time() - start
        jph = (jobs_dispatched / elapsed * 3600) if elapsed > 0 else 0.0
        _write_heartbeat(tick, jph)

        if QUEUE_FILE.exists():
            lines = QUEUE_FILE.read_text().splitlines()
            for line in lines:
                try:
                    job = json.loads(line)
                    jid = job.get("job_id", "")
                    if not jid or jid in seen or job.get("status") != "queued":
                        continue
                    seen.add(jid)
                    cat, vol = _classify(job)
                    agent_slug, model = router.route({"category": cat})
                    print(
                        f"[dispatcher] {jid} → category={cat} volume={vol}"
                        f" agent={agent_slug} model={model}",
                        file=sys.stderr,
                    )
                    jobs_dispatched += 1
                except (json.JSONDecodeError, KeyError):
                    continue

        time.sleep(interval_s)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--watch", action="store_true", default=True,
                    help="Watch queue and dispatch (default)")
    ap.add_argument("--interval", type=int, default=5,
                    help="Poll interval in seconds")
    args = ap.parse_args()

    if args.watch:
        watch_loop(args.interval)


if __name__ == "__main__":
    main()
