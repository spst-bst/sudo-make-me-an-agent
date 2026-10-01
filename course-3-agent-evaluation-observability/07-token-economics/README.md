# Module 7: LLM token economics

Cost per call is `(input tokens × input price) + (output tokens × output
price)`, multiplied by call volume — but the biggest hidden cost driver in
agents is context bloat: every tool result gets resent on every loop
iteration, so cost grows faster than step count unless it's controlled. The
main levers are prompt caching (reuse the static system prompt and tool
definitions across calls instead of repricing them every turn), trimming
stale tool results before re-injecting them, routing simple sub-tasks to a
smaller/cheaper model, and setting hard per-team or per-task budgets with
alerts.

## Run it

```bash
python token_cost_calculator.py
```

Watch the `context_bloat_demo` output — cumulative input tokens grow
roughly with the *square* of the step count, not linearly, because the
whole tool-result history gets resent every iteration.

## FAQ — explained in plain terms

"At enterprise scale the lever that matters most usually isn't the
per-token price — it's context bloat. An agent that resends its full
tool-call history on every loop iteration burns tokens faster than the step
count alone would suggest, so prompt caching and trimming stale context
typically save more than switching to a cheaper model."
