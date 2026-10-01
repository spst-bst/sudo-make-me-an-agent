# Measurement Framework — Example

A filled reference to check your own TEMPLATE.md against — not a model
answer to copy verbatim. Adjust specifics to whatever organization you're
actually describing.

## Per-agent metrics

| Metric | Why it matters |
| --- | --- |
| Golden-suite pass rate | The one number that answers "is this agent still doing its job" — a frozen baseline plus a tolerance band (Module 5), re-checked on every model or prompt change before rollout, not after. |
| p50 / p95 latency | p50 is the typical experience; p95 is the worst case a real slice of users actually hits. An agent can look fast on average and still be unusable for 1 in 20 requests if only p50 is tracked. |
| Cost per run | Dollars compound with call volume (Module 7) — a cheap-looking per-call cost can still blow a budget at scale, especially once context bloat from resent tool history is factored in. |
| Safety-incident count | Correctness and safety are independent axes (Module 2) — an agent can be highly correct and still take a disallowed action. This is the metric that catches that failure mode directly, not as a side effect of tracking correctness. |
| Human-override rate | The earliest signal of drift: people start correcting or overriding the agent before the golden suite shows a pass-rate drop, because the suite only tests what it was written to test. A rising override rate on tasks the suite still calls "passing" means the suite has a blind spot — not that nothing's wrong. |

## Dashboards

- Fleet dashboard: every registered agent's pass rate, cost, and incident
  count in one view, sorted by risk tier, so a reviewer can scan hundreds
  of agents without opening any single one.
- Per-agent drill-down: pass-rate trend, cost trend, and every safety
  incident or override for one agent, each linked to the actual trace
  (Module 6) that produced it — not just an aggregate number.
- Cost-by-team view: spend rolled up by owning team, so a budget
  conversation starts from "which team's agents are driving spend" instead
  of one undifferentiated total.

## Alerts

| Trigger | Who's notified | Action |
| --- | --- | --- |
| Pass-rate regression beyond tolerance | Owning team's on-call | Block the pending release (Module 5's CI gate); investigate before retrying, don't just rerun until it passes. |
| Cost spike beyond budget | Owning team + platform team | Page only if sudden/sharp; otherwise a daily digest — most cost spikes are gradual context bloat, not an emergency. |
| Safety incident | Owning team on-call + security on-call | Immediate: disable the agent's credentials at the identity layer, not a code deploy; blameless postmortem afterward. |
| Latency SLO breach | Owning team's on-call | Check whether it's a model-provider-side slowdown or an agent-side regression before escalating further — the fix differs completely. |

---

**One-sentence answer:** "Human-override rate matters because it's the
leading indicator of drift — people stop trusting an agent's output well
before that shows up as a measurable pass-rate drop on a golden suite that
was only ever written to catch failure modes someone already knew about."
