# Changelog

## [0.1.1] — 2026-09-28

### Fixed

- Classification matches whole words: "solution" or "console" no longer count as Solana.
- `-replay` categories reach their chain's route in the cost optimizer. Before, they all fell through to the fallback.
- `jobs_per_hour` uses a one-minute minimum window, so a start-up burst is not reported as millions per hour.
- Synthetic mode runs on its own. Before, it needed code outside this repository.

### Changed

- The data directory is `$TAIFOON_MAMBA_DATA`, default `./.data`.
- `--once` routes the queue once and exits. `synthetic --ticks N` stops after N ticks. `--interval` must be positive.
- Models: `claude-sonnet-5` and `claude-opus-5-5`.
- `pyproject.toml` declares its build backend and a `dev` extra. CI runs Python 3.12 and 3.13.
- README and docs describe what this package does today, and install from GitHub (it is not on PyPI).

## [0.1.0] — 2026-05-10

Initial scaffold: dispatcher and cost-optimizer routing.

### Added

- `taifoon_mamba.dispatcher` — queue watcher, heartbeat writer, brief classifier
- `taifoon_mamba.synthetic` — demo heartbeat loop
- Dispatcher flow: queue.jsonl → classify → BountyDraft v1 → /builders/bounties
- Heartbeat at `.data/dispatch/heartbeat.json` every poll tick (LiveBrain integration)
- Category taxonomy: evm/sol/btc/cosmos/lambda-replay, oracle, aggregator, platform-phase5/6
- COE gate conditions documented
- `docs/DISPATCHER.md` — full flow, endpoints, category taxonomy
- `docs/COST_OPTIMIZER.md` — routing table, weight tuning, fallback, config vars
- Tests: 21 pytest tests (cost optimizer × 10, dispatcher classify × 11) — all pass
- CI: ruff + pyright + pytest + gitleaks on every push/PR
- `pyproject.toml` — ruff + pyright config, `taifoon-mamba` entry point
