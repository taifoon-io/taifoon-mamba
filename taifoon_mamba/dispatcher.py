"""
taifoon-mamba dispatcher: watches a queue of job briefs, classifies each one and picks the agent and model to route it to.

Usage:
    python -m taifoon_mamba.dispatcher             watch the queue (Ctrl-C to stop)
    python -m taifoon_mamba.dispatcher --once      process the queue once and exit

Data directory (queue and heartbeat): $TAIFOON_MAMBA_DATA, default ./.data
    <data>/dispatch/queue.jsonl       one JSON brief per line: {"job_id", "title", "description", "status": "queued"}
    <data>/dispatch/heartbeat.json    written on every tick: {"last_tick_ms", "tick_count", "jobs_per_hour"}
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

from taifoon_mamba.cost_optimizer import CostOptimizer

DATA = Path(os.environ.get("TAIFOON_MAMBA_DATA", ".data"))
QUEUE_FILE = DATA / "dispatch" / "queue.jsonl"
HEARTBEAT = DATA / "dispatch" / "heartbeat.json"

# Whole words only: "sol" must not match "solution", "btc" must not match inside another word.
_RULES: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"\b(solana|sol)\b"), "sol-replay", "A"),
    (re.compile(r"\b(bitcoin|btc)\b"), "btc-replay", "B"),
    (re.compile(r"\bcosmos\b"), "cosmos-replay", "B"),
    (re.compile(r"\boracles?\b"), "oracle", "S"),
    (re.compile(r"\baggregators?\b"), "aggregator", "S"),
]


def _ensure_dirs() -> None:
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)


def _write_heartbeat(tick: int, jph: float = 0.0) -> None:
    HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT.write_text(json.dumps({
        "last_tick_ms": int(time.time() * 1000),
        "tick_count": tick,
        "jobs_per_hour": jph,
    }, indent=2))


def _classify(brief: dict) -> tuple[str, str]:
    """Return (category, volume_class) from the brief's title and description. Rules, no model."""
    text = f"{brief.get('description', '')} {brief.get('title', '')}".lower()
    for pattern, category, volume in _RULES:
        if pattern.search(text):
            return category, volume
    return "evm-replay", "A"


def process_queue(seen: set[str], router: CostOptimizer) -> list[dict]:
    """Route every queued brief not seen before. Returns one decision per routed brief."""
    if not QUEUE_FILE.exists():
        return []
    decisions: list[dict] = []
    for line in QUEUE_FILE.read_text().splitlines():
        try:
            job = json.loads(line)
        except json.JSONDecodeError:
            continue
        jid = job.get("job_id", "") if isinstance(job, dict) else ""
        if not jid or jid in seen or job.get("status") != "queued":
            continue
        seen.add(jid)
        category, volume = _classify(job)
        agent, model = router.route({"category": category})
        decisions.append({"job_id": jid, "category": category, "volume_class": volume, "agent": agent, "model": model})
    return decisions


def watch_loop(interval_s: float = 5, once: bool = False) -> None:
    _ensure_dirs()
    seen: set[str] = set()
    tick = 0
    routed = 0
    start = time.time()
    router = CostOptimizer()
    print(f"taifoon-mamba dispatcher watching {QUEUE_FILE}", file=sys.stderr)
    while True:
        tick += 1
        for d in process_queue(seen, router):
            routed += 1
            print(f"[dispatcher] {d['job_id']} → category={d['category']} volume={d['volume_class']}"
                  f" agent={d['agent']} model={d['model']}", file=sys.stderr)
        # at least a one-minute window, so a burst at start-up (or --once) is not read as millions per hour
        _write_heartbeat(tick, round(routed / max(time.time() - start, 60) * 3600, 1))
        if once:
            return
        time.sleep(interval_s)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--once", action="store_true", help="process the queue once and exit")
    ap.add_argument("--interval", type=float, default=5, help="poll interval in seconds (default 5)")
    args = ap.parse_args()
    if args.interval <= 0:
        ap.error("--interval must be positive")
    try:
        watch_loop(args.interval, once=args.once)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
