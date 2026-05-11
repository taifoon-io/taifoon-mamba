# Contributing to taifoon-mamba

TSUL v1.0. See [`taifoon-io/license`](https://github.com/taifoon-io/license) for terms.

taifoon-mamba is the Pro dispatcher layer on top of open-mamba. The underlying engine is open-source at [`taifoon-io/open-mamba`](https://github.com/taifoon-io/open-mamba) — contributions to the engine go there.

Contributions welcome to:
- `taifoon_mamba/cost_optimizer.py` — model/agent routing table weight tuning
- `taifoon_mamba/dispatcher.py` — job classification, bounty scoping, COE gate logic
- `tests/` — additional pytest coverage for edge cases
- `docs/` — documentation improvements

---

## Setup

```bash
git clone https://github.com/taifoon-io/taifoon-mamba
cd taifoon-mamba
pip install -e ".[dev]"    # or: pip install ruff pyright pytest
```

Requires Python 3.12+.

---

## Before opening a PR

```bash
ruff check .          # zero lint warnings
pyright .             # zero type errors
pytest tests/ -v      # all tests pass
```

CI runs all three on every push.

---

## Adding a new category to the cost optimizer

1. Add an entry to `_ROUTING_TABLE` in `cost_optimizer.py`
2. Add the corresponding test case to `tests/test_cost_optimizer.py`
3. Update the routing table docstring at the top of `cost_optimizer.py`
4. Document the new category in `docs/COST_OPTIMIZER.md`

---

## License

TSUL v1.0 — see [`taifoon-io/license`](https://github.com/taifoon-io/license/blob/main/LICENSE.md).
Contributor License Agreement mirrors the open-mamba CLA.

Questions: **taifooon@proton.me**
