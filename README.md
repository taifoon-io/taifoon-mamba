# taifoon-mamba

> The Pro tier of open-mamba. Hosted dispatcher, Builders Programme intake, cost-optimizer routing.

`taifoon-mamba` is the commercial layer that runs on top of the **[open-mamba](https://github.com/taifoon-io/open-mamba)** engine. The open-mamba bus handles task durability, dispatch, and agent orchestration. taifoon-mamba adds the surfaces that make that engine production-grade and externally accessible: job intake from the Taifoon OS web UI, bounty scoping for the Builders Programme, SSO/RBAC, audit logs, and branded delivery.

**License:** TSUL v1.0 — see [`taifoon-io/license`](https://github.com/taifoon-io/license).

---

## How it fits

```
  [ taifoon.io/os/submit-job ]    [ Builders Programme ]    [ taifoon-intel signals ]
             │                             │                          │
             ▼                             ▼                          ▼
  ┌──────────────────────────────────────────────────────────────────────────┐
  │                         taifoon-mamba (Pro)                              │
  │  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────────────┐   │
  │  │  job dispatcher │  │  bounty scoper   │  │  cost-optimizer router│   │
  │  │  triage → draft │  │  acceptance crit │  │  model/agent selector │   │
  │  └────────┬────────┘  └────────┬─────────┘  └───────────┬───────────┘   │
  └───────────┼────────────────────┼────────────────────────┼───────────────┘
              │                    │                         │
              └────────────────────▼─────────────────────────┘
                                   │
                          POST /ingest
                                   │
                                   ▼
                     ┌─────────────────────────┐
                     │      open-mamba bus      │
                     │      :1337 (engine)      │
                     └──────────┬──────────────┘
                                │
               ┌────────────────┼───────────────────┐
               ▼                ▼                   ▼
          openfang          nemotron           nemotron
        (claude agents)   (taifoon-intel)   (protocol-intel)
```

---

## What taifoon-mamba adds over open-mamba

| Feature | open-mamba (free) | taifoon-mamba (Pro) |
|---|---|---|
| Task bus + DuckDB queue | ✓ | ✓ |
| Claude + Nemotron dispatch | ✓ | ✓ |
| Webhook + cron triggers | ✓ | ✓ |
| Job intake from taifoon.io UI | — | ✓ |
| Builders Programme bounty scoper | — | ✓ |
| Cost-optimizer model routing | — | ✓ |
| SSO / RBAC | — | ✓ |
| Audit log + compliance export | — | ✓ |
| Branded Telegram / Slack delivery | — | ✓ |
| SLA (72h triage, 99.5% uptime) | — | ✓ |

---

## Dispatcher — job intake flow

When anyone submits a job at `taifoon.io/os/submit-job`:

```
POST /api/dispatch/submit-job
           │
           ▼
    [ TRIAGE QUEUE ]         ← .data/dispatch/queue.jsonl
           │
           ▼
    [ job dispatcher ]
    reads brief, classifies category,
    scopes acceptance criteria,
    drafts BountyDraft v1
           │
    ┌──────┴──────┐
    │  COE gate?  │
    └──────┬──────┘
       yes │  no
           │   └──────────────────────► POST to /builders/bounties
           ▼
    [ COE REVIEW QUEUE ]
           │ approved
           └──────────────────────────► POST to /builders/bounties
```

Heartbeat written to `.data/dispatch/heartbeat.json` every 2s — the LiveBrain on `/os/dispatch` polls it and pulses the Volt indicator on every tick.

### Dispatcher endpoints

| Endpoint | Purpose |
|---|---|
| `POST /mamba/triage` | Receive a queued job brief, return a scoped bounty draft |
| `GET  /mamba/heartbeat` | Liveness probe + jobs/h rate |
| `GET  /mamba/queue` | Sanitized public snapshot of the dispatcher queue |

---

## Builders Programme — reviewer pipeline

Bounties posted to the Builders Programme go through a deterministic reviewer fleet before any merge. taifoon-mamba coordinates this via the open-mamba bus:

```
1. Contributor pushes submission
2. taifoon-mamba reads bounties.xml → assigns reviewers
3. Each reviewer agent dispatched via POST /ingest (assigned_agent: reviewer-slug)
4. Reviewer emits signed verdict: pass | fail | inconclusive
5. Two pass → auto-merge after 24h challenge window
   Any fail → reject, return to OPEN
   Any inconclusive → human reviewer queue
```

Reviewer agents are themselves open-mamba agents — versioned, auditable, bonded on devnet. Anyone can register a new reviewer agent via the Builders Programme flow.

---

## Cost-optimizer routing

taifoon-mamba inspects each task before forwarding to the bus and selects the lowest-cost model/agent that meets the task's quality bar:

| Task type | Default routing |
|---|---|
| Protocol intel query | `nemotron/taifoon` (fast, cheap, no Claude cost) |
| Code delivery | `coder` → claude-opus-4-7 (highest capability) |
| Code review | `code-reviewer` → claude-sonnet-4-6 |
| Bounty triage | deterministic rules dispatcher (no LLM cost for v0.1) |

The optimizer uses historical cost + verdict data from the open-mamba DuckDB lake to tune routing weights over time.

---

## Self-host the open-mamba engine

taifoon-mamba Pro is hosted at `taifoon.dev`. The underlying engine is free and open:

```bash
# Run the full stack locally:
cd ~/projects/open-mamba && cargo build --bin open-mamba
mamba up
# → bus at localhost:1337, openfang at localhost:4200
```

See [open-mamba](https://github.com/taifoon-io/open-mamba) for full setup docs.

---

## Status

`v0.1` — dispatcher scaffold + cost-optimizer routing wired. Bounty scoper uses deterministic rules. The Mamba-class model for triage arrives in `v0.2` once the loop has enough real dispatcher decisions to fine-tune against.

---

Access, pricing, or integration questions: **taifooon@proton.me**.

Part of the Taifoon OS — [taifoon.io](https://taifoon.io).
