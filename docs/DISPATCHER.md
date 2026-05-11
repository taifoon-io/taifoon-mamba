# taifoon-mamba — Dispatcher Reference

The dispatcher is the first-mile triage layer. It reads incoming job briefs from the queue and converts them into structured `BountyDraft v1` objects that get posted to the Builders Programme.

## Flow

```
POST /api/dispatch/submit-job
           │
           ▼
    .data/dispatch/queue.jsonl        ← append-only JSONL queue
           │
     dispatcher picks up
           │
           ▼
    classify(brief)                   ← category + volume class
           │
           ▼
    scope(brief, category)            ← acceptance criteria + reviewer set
           │
           ▼
    BountyDraft v1
     {
       bounty_id:           uuid,
       category:            "evm-replay" | "sol-replay" | ...,
       volume_class:        "S" | "A" | "B" | "C" | "ALL",
       title:               string,
       acceptance_criteria: string[],
       reviewers:           string[],     // slugs from reviewers.xml
       creator_slice_bps:   70,
       reviewer_slice_bps:  20,
       ecosystem_slice_bps: 10,
       status:              "OPEN",
       draft_at:            iso8601,
     }
           │
    COE gate?  ────no────► POST /builders/bounties
           │
          yes
           │
           ▼
    .data/dispatch/coe_queue.jsonl    ← human review
           │  approved
           └──────────────────────► POST /builders/bounties
```

## Heartbeat

The dispatcher writes to `.data/dispatch/heartbeat.json` every 2 seconds:

```json
{
  "ts":            "2026-05-10T12:00:00Z",
  "queue_depth":   3,
  "jobs_per_hour": 12,
  "last_bounty":   "b-a3f9c2e1",
  "status":        "running"
}
```

The `taifoon-next` LiveBrain polls this file at `/api/dispatch/live-state` and pulses the Volt indicator on `/os/dispatch` on every heartbeat tick.

## Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/mamba/triage` | POST | Receive a queued brief, return a `BountyDraft v1` |
| `/mamba/heartbeat` | GET | Liveness probe + jobs/h rate |
| `/mamba/queue` | GET | Sanitized public snapshot of the queue |

## Category taxonomy

| Category | Reviewer set |
|---|---|
| `evm-replay` | evm-replay, schema-conformer |
| `sol-replay` | sol-replay, schema-conformer |
| `btc-replay` | btc-replay, schema-conformer |
| `cosmos-replay` | cosmos-replay, schema-conformer |
| `lambda-replay` | lambda-replay, schema-conformer |
| `oracle` | oracle-checker, schema-conformer |
| `aggregator` | aggregator-decomposer, schema-conformer |
| `platform-phase5` | platform-checker, schema-conformer |
| `platform-phase6` | platform-checker, dossier-builder |

## COE gate conditions

A draft is routed to the COE queue when:
- `volume_class == "ALL"` (highest traffic routes)
- `category == "platform-phase6"`
- `creator_slice_bps` override requested by the submitter

All other drafts post automatically after a 24h challenge window.
