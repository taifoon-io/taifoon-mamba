# taifoon-mamba

Reads a queue of job briefs, sorts each one into a category, and picks the agent and model to route it to: the
cheapest route that meets the task's bar. Python 3.12+, standard library only.

- **What:** a dispatcher (queue → category → route) and a cost-optimizer routing table.
- **Why:** most briefs don't need the most capable model. Rules pick the category, and a table maps each category to
  an agent and a model, so routine work goes to a cheaper model and the hard categories to the strongest.
- **How:** drop briefs into a JSONL queue; the dispatcher routes each new one and writes a heartbeat a dashboard can
  read.

Part of [Taifoon](https://taifoon.io). Licence: [TSUL v1.0](LICENSE.md).

## Install

Not on PyPI. Install from GitHub:

```bash
pip install "git+https://github.com/taifoon-io/taifoon-mamba"
```

## Use

```bash
mkdir -p .data/dispatch
echo '{"job_id":"j1","title":"Solana adapter replay fix","status":"queued"}' >> .data/dispatch/queue.jsonl
echo '{"job_id":"j2","description":"stale oracle price feed","status":"queued"}' >> .data/dispatch/queue.jsonl

taifoon-mamba --once
# [dispatcher] j1 → category=sol-replay volume=A agent=coder model=claude-sonnet-5
# [dispatcher] j2 → category=oracle volume=S agent=coder model=claude-opus-5-5
```

| Command | What it does |
|---|---|
| `taifoon-mamba` | Watch the queue and route new briefs every 5 s (`--interval <s>`); Ctrl-C stops it |
| `taifoon-mamba --once` | Route what is queued now, then exit |
| `python -m taifoon_mamba.synthetic --ticks 10` | Write a demo heartbeat, for building a dashboard without real jobs |

The data directory is `$TAIFOON_MAMBA_DATA` (default `./.data`):

- `dispatch/queue.jsonl`: one brief per line, `{"job_id", "title", "description", "status": "queued"}`. Only
  `queued` briefs are routed, each once.
- `dispatch/heartbeat.json`: written on every tick, `{"last_tick_ms", "tick_count", "jobs_per_hour"}`.

In code:

```python
from taifoon_mamba.cost_optimizer import CostOptimizer

CostOptimizer().route({"category": "oracle"})   # ('coder', 'claude-opus-5-5')
```

## How a brief is routed

1. **Category**, from whole words in the title and description: `sol-replay`, `btc-replay`, `cosmos-replay`, `oracle`,
   `aggregator`, else `evm-replay`. See [docs/DISPATCHER.md](docs/DISPATCHER.md).
2. **Route**, from the table in `cost_optimizer.py`. A `-replay` category uses its chain's route. See
   [docs/COST_OPTIMIZER.md](docs/COST_OPTIMIZER.md).

| Category | Agent | Model |
|---|---|---|
| evm, sol, btc, cosmos, lambda-replay | coder | claude-sonnet-5 |
| oracle, aggregator, platform-phase5, platform-phase6 | coder | claude-opus-5-5 |
| anything else | coder | claude-sonnet-5 |

## What is not here

This repository is the dispatcher and the router. It does not run the agents. The hosted service around it is operated
by Taifoon and is not part of this repository: job intake on taifoon.io, bounty scoping for the Builders Programme and
the reviewers. The dispatcher prints each routing decision; delivering the brief to an agent is up to whatever runs it.

## Status

`0.1.1`. Classification is rules only, with no model. `CostOptimizer.weight_tuning()` keeps a score per category from
past outcomes, but routes don't use it yet.

## Develop

```bash
git clone https://github.com/taifoon-io/taifoon-mamba && cd taifoon-mamba
pip install -e ".[dev]"
ruff check . && pyright . && pytest
```

Security issues: see [SECURITY.md](SECURITY.md). Questions: taifooon@proton.me.
