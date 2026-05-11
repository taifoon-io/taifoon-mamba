"""
Synthetic dispatcher mode — emits a believable demo cadence for /os/dispatch.

Usage:
    python -m taifoon_mamba.synthetic --interval 2
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent.parent
BRAIN_BRIDGE = THIS_DIR.parent / "open-mamba" / "brain_bridge.py"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--interval", type=float, default=2.0, help="tick interval in seconds")
    args = ap.parse_args()

    # Delegate to brain_bridge.py synthetic loop — it writes to
    # ../taifoon-next/.data so /os/dispatch pulses.
    if BRAIN_BRIDGE.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("brain_bridge", BRAIN_BRIDGE)
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        mod.synthetic_loop(interval_s=args.interval)
    else:
        print(
            f"brain_bridge.py not found at {BRAIN_BRIDGE}\n"
            "Set TAIFOON_NEXT_DATA_ROOT or run from spinner/open-mamba/ directly.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
