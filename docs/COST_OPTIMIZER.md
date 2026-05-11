# taifoon-mamba — Cost Optimizer

The cost optimizer sits between job intake and the open-mamba bus. It inspects each task and routes it to the lowest-cost model/agent that meets the quality bar.

## Routing table

| Task type | Default route | Rationale |
|---|---|---|
| Protocol intel query | `nemotron/taifoon` | Fine-tuned on protocol data; no Claude cost |
| Code delivery | `coder` → claude-sonnet-4-6 | Full reasoning required |
| Code review | `code-reviewer` → claude-opus-4-7 | Highest accuracy for security review |
| Bounty triage (v0.1) | deterministic rules dispatcher | No LLM cost for classification |
| Bounty triage (v0.2) | `nemotron/taifoon` fine-tuned | Post fine-tune on real dispatcher decisions |

## Weight tuning

The optimizer pulls historical cost + verdict data from the open-mamba DuckDB lake (via `mamba-lake` crate API) and recomputes routing weights every 6 hours:

```
weight(agent, task_type) = quality_score(agent, task_type) / median_cost(agent, task_type)
```

Where `quality_score` is derived from:
- `code-reviewer` verdict rate: `APPROVED` / total tasks routed
- Token efficiency: tasks completed within budget / total tasks

## Fallback

If the preferred route fails (agent not found, 5xx from nemotron), the optimizer falls back to the next-cheapest route and logs the fallback decision in DuckDB for weight adjustment.

## Configuration

Set in `~/.mamba/runtime.env`:

```bash
# Disable optimizer, always use specified model:
MAMBA_OPTIMIZER_DISABLED=1

# Override quality threshold (default 0.85):
MAMBA_QUALITY_THRESHOLD=0.90

# Cap per-task cost in USD (tasks exceeding cap are rejected):
MAMBA_COST_CAP_USD=0.50
```
