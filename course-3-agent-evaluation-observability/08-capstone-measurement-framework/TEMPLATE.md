# Measurement Framework — Enterprise Agent Registry

Fill in every `_____`. For each row, be ready to say in one sentence why
that metric earns its place on the dashboard rather than being "nice to
have."

## Per-agent metrics

| Metric | Why it matters |
| --- | --- |
| Golden-suite pass rate | _____ |
| p50 / p95 latency | _____ |
| Cost per run | _____ |
| Safety-incident count | _____ |
| Human-override rate | _____ |

## Dashboards

- Fleet dashboard: _____
- Per-agent drill-down: _____
- Cost-by-team view: _____

## Alerts

| Trigger | Who's notified | Action |
| --- | --- | --- |
| Pass-rate regression beyond tolerance | _____ | _____ |
| Cost spike beyond budget | _____ | _____ |
| Safety incident | _____ | _____ |
| Latency SLO breach | _____ | _____ |

---

**One-sentence answer:** "Human-override rate matters
because _____" (this is the one metric most people forget — it's the early
signal of drift before the pass rate itself drops).
