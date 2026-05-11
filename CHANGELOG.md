# Changelog

## [Unreleased]

- `v0.2` — Mamba-class model for triage (fine-tuned on real dispatcher decisions)
- Cost-optimizer weight tuning from DuckDB historical data
- BuildersRegistry on-chain verdict submission (TAIFOON_REGISTRY_ADDR)
- Branded Slack + email delivery channels

## [0.1.0] — 2026-05-10

Initial scaffold. Pro tier dispatcher on top of open-mamba.

### Added

- `taifoon_mamba.dispatcher` — queue watcher, heartbeat writer, brief classifier
- `taifoon_mamba.synthetic` — demo loop delegate (→ brain_bridge.py)
- Dispatcher flow: queue.jsonl → classify → BountyDraft v1 → /builders/bounties
- Heartbeat at `.data/dispatch/heartbeat.json` every poll tick (LiveBrain integration)
- Category taxonomy: evm/sol/btc/cosmos/lambda-replay, oracle, aggregator, platform-phase5/6
- COE gate conditions documented
- `docs/DISPATCHER.md` — full flow, endpoints, category taxonomy
- `docs/COST_OPTIMIZER.md` — routing table, weight tuning, fallback, config vars
- Tests: 21 pytest tests (cost optimizer × 10, dispatcher classify × 11) — all pass
- CI: ruff + pyright + pytest + gitleaks on every push/PR
- `pyproject.toml` — ruff + pyright config, `taifoon-mamba` entry point
