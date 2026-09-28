"""
Synthetic mode: writes a steady demo heartbeat, so a dashboard that reads heartbeat.json can be built and tested
without real jobs. It routes nothing.

Usage:
    python -m taifoon_mamba.synthetic --interval 2        (Ctrl-C to stop)
    python -m taifoon_mamba.synthetic --ticks 10          write 10 ticks and exit
"""
from __future__ import annotations

import argparse
import random
import time

from taifoon_mamba import dispatcher


def run(interval_s: float = 2.0, ticks: int | None = None, seed: int | None = None) -> int:
    """Write synthetic heartbeats; returns how many were written."""
    rng = random.Random(seed)
    tick = 0
    while ticks is None or tick < ticks:
        tick += 1
        dispatcher._write_heartbeat(tick, round(rng.uniform(4, 20), 1))
        if ticks is None or tick < ticks:
            time.sleep(interval_s)
    return tick


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--interval", type=float, default=2.0, help="seconds between ticks (default 2)")
    ap.add_argument("--ticks", type=int, default=None, help="stop after this many ticks (default: run until Ctrl-C)")
    args = ap.parse_args()
    if args.interval <= 0:
        ap.error("--interval must be positive")
    try:
        run(args.interval, args.ticks)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
