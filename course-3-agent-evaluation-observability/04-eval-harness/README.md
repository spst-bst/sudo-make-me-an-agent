# Module 4: Building a simple evaluation harness

A minimal harness is exactly a test runner plus a scoring function, run N
times per case because of non-determinism, with a pass rate reported instead
of a single pass/fail.

## Run it

```bash
python eval_harness.py
```

Run it a few times — the mock agent is deliberately ~15% flaky, so the pass
rate moves between runs. That instability *is* the lesson: a single run
tells you almost nothing.

## Exercise

Open `exercise_starter.py` and wire `run_eval_suite` up to the real
`react_loop` from `../../course-1-agentic-ai-development/02-react-loop/`
(the import pattern is commented at the bottom of `eval_harness.py`). Add at
least one new `TestCase` that exercises a tool call, not just a
knowledge question.

## What success looks like

You get a real pass rate (not the mock's) across at least 5 repeats per
case, and you can explain why a single run passing tells you nothing about
whether the agent is reliable.

## FAQ — explained in plain terms

"This is a unit test suite with one change: each test runs multiple times,
because the model isn't deterministic. The pass rate across repeats is the
real signal — a single run passing or failing tells you almost nothing."
