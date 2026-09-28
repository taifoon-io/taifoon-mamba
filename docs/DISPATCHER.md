# Dispatcher

The dispatcher reads job briefs from a queue, classifies each one, and asks the cost optimizer where to route it.

## Flow

```
<data>/dispatch/queue.jsonl      one JSON brief per line
        │   only "status": "queued", each job_id once
        ▼
classify(brief)                  category + volume class, from whole words in title and description
        │
        ▼
CostOptimizer.route(category)    agent + model
        │
        ▼
a decision per brief             printed: job_id, category, volume class, agent, model
```

`<data>` is `$TAIFOON_MAMBA_DATA`, default `./.data`. Lines that are not JSON, have no `job_id`, or are not `queued`
are skipped.

## Heartbeat

Written to `<data>/dispatch/heartbeat.json` on every tick:

```json
{ "last_tick_ms": 1790600000000, "tick_count": 42, "jobs_per_hour": 12.0 }
```

`jobs_per_hour` counts routed briefs over the time since start, with a one-minute minimum window.
`python -m taifoon_mamba.synthetic` writes the same file with demo numbers.

## Categories

The first rule that matches wins. Words match whole, so "solution" is not Solana.

| Words | Category | Volume class |
|---|---|---|
| solana, sol | `sol-replay` | A |
| bitcoin, btc | `btc-replay` | B |
| cosmos | `cosmos-replay` | B |
| oracle, oracles | `oracle` | S |
| aggregator, aggregators | `aggregator` | S |
| anything else | `evm-replay` | A |

## Not in this package

Bounty drafts, reviewer assignment and the human review gate belong to the hosted service. The dispatcher here stops
at the routing decision.
