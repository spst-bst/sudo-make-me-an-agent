# Module 1: Why agent evaluation is hard

Agent evaluation breaks the usual unit-test model in three ways:
**non-determinism** (the same prompt can produce a different tool-call
sequence or answer across runs, so a single pass/fail is meaningless),
**multi-step failure amplification** (a 95%-reliable step, chained five
times, yields roughly a 77% end-to-end success rate — errors compound rather
than average), and **context sensitivity** (a small change to a tool
description or system prompt can shift behavior far more than the
equivalent change would in deterministic code).

## Run it

```bash
python compounding_failure.py
```

## FAQ — explained in plain terms

"An agent can pass the exact same test nine times and fail the tenth on
identical input, so evaluation has to measure a pass rate across repeated
runs, not a single green checkmark. And because failures compound across
steps, a system that looks 95% reliable per action can be well under 80%
reliable end-to-end by the time it's five steps deep — that's the number
that actually matters to the business."
