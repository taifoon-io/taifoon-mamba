# Cost optimizer

`CostOptimizer.route(brief)` returns `(agent, model)` for a brief's `category`.

## Routing table

The first segment of the category is looked up (`"aggregator/uniswap"` → `aggregator`). If it is not in the table and
ends in `-replay`, its chain is looked up instead (`"sol-replay"` → `sol`). Anything else gets the fallback.

| Category | Agent | Model | Why |
|---|---|---|---|
| evm, sol, btc, cosmos, lambda-replay | coder | claude-sonnet-5 | Routine adapter and replay work |
| oracle, aggregator, platform-phase5, platform-phase6 | coder | claude-opus-5-5 | Harder reasoning, higher cost of a mistake |
| anything else | coder | claude-sonnet-5 | Safe fallback |

To add a category: add it to `_ROUTING_TABLE` in `cost_optimizer.py`, add a test in `tests/test_cost_optimizer.py`,
and add a row here.

## Weights

`weight_tuning(history)` takes past outcomes, `[{ "category", "cost_usd", "verdict" }]`, where verdict is `approved`
(1.0), `changes_requested` (0.5) or anything else (0.0). It keeps a running average per category and returns the
weights. Routes do not read the weights yet.
