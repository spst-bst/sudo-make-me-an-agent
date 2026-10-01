# Course 3: Agent Evaluation and Observability

Understand how to test, evaluate, and monitor AI agents in production with
enough depth to design an evaluation framework for enterprise agents. Every
module's code here runs standalone (no API key needed) using a mock agent
function — swap in the real `react_loop` from
`../course-1-agentic-ai-development/02-react-loop/` once you've built it, per
the comments in `04-eval-harness/`.

## Prerequisites

- Course 1's `react_loop` and tool set, ideally working locally (not
  strictly required — the harness here runs against a mock agent too)
- Optional: `npm install -g promptfoo` for Module 3

## Weekly schedule

| Day | Hours | Focus | Folder |
| --- | --- | --- | --- |
| 1 | 1h | Why agent evaluation is hard | `01-why-eval-is-hard/` |
| 2 | 1h | Evaluation dimensions | `02-eval-dimensions/` |
| 3 | 1h | Evaluation frameworks overview | `03-frameworks-overview/` |
| 4 | 2h | Build an evaluation harness | `04-eval-harness/` |
| 5 | 1.5h | Regression testing for agents | `05-regression-testing/` |
| 6 | 1.5h | Observability, tracing, token economics | `06-observability/`, `07-token-economics/` |
| 7 | 1.5h | Capstone | `08-capstone-measurement-framework/` |

## Modules

1. **[Why evaluation is hard](01-why-eval-is-hard/)** — non-determinism,
   multi-step failure amplification, context sensitivity.
2. **[Evaluation dimensions](02-eval-dimensions/)** — correctness, safety,
   consistency, latency, cost.
3. **[Frameworks overview](03-frameworks-overview/)** — LangSmith,
   Braintrust, PromptFoo — what each is for.
4. **[Evaluation harness](04-eval-harness/)** — a runnable Python harness
   that scores an agent across repeated runs.
5. **[Regression testing](05-regression-testing/)** — detecting when a
   model/prompt update breaks existing behavior.
6. **[Observability](06-observability/)** — structured logging and trace IDs
   across agent steps.
7. **[Token economics](07-token-economics/)** — measuring and optimizing
   token spend at scale.
8. **[Capstone: measurement framework](08-capstone-measurement-framework/)**
   — a registry-wide metrics/dashboard/alerts spec.

## Capstone: Registry-wide measurement framework

See [`08-capstone-measurement-framework/`](08-capstone-measurement-framework/)
— fill in `TEMPLATE.md` for a registry of agents spanning multiple teams;
`EXAMPLE.md` is a filled reference to check your work against, not to copy.

**What success looks like:** you can defend every row's rationale out loud
in under two minutes each, and you can explain why human-override rate
belongs on the dashboard even though no module builds it directly — it's
the earliest signal of drift, surfacing before a golden-suite pass rate
(which only tests what it was written to test) would show anything wrong.

## Technical FAQ

1. "How do you know an agent is ready for production?" — not from one
   successful run; agents are non-deterministic, so a single pass/fail
   tells you almost nothing. Readiness means a high pass rate across
   *repeated* runs of a golden test suite, scored across correctness,
   safety, consistency, latency, and cost — not correctness alone.
2. "A model provider ships a new version — how do you know if it's safe to
   upgrade?" — re-run the same frozen golden suite against the new version
   and diff its pass rate against the recorded baseline, allowing a
   tolerance band for normal non-deterministic variance. A drop beyond that
   band is a release blocker, exactly like a failing CI test.
3. "How would you track cost and reliability across hundreds of agents
   built by different teams?" — centralized observability, not per-team ad
   hoc tracking: every prompt/tool call/result logged under one trace ID
   per request, token cost accounted for per call (including context bloat
   from resent tool history), rolled up into a registry-wide measurement
   framework with dashboards and alerts.
