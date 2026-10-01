# Module 5: Regression testing for agents

Freeze a golden test suite and its baseline pass rate per model/prompt
version; re-run it on every model upgrade, prompt edit, or tool-description
change; diff against baseline with a tolerance band (some variance is normal
given non-determinism, so flag only drops beyond it, not any drop at all).

## Run it

```bash
python regression_check.py
echo $?   # non-zero = would block a CI/release gate
```

## Exercise

Lower `BASELINE_PASS_RATE` to something unrealistic (e.g. `0.99`) and rerun
— confirm it now flags a regression against the same mock agent, purely
because the bar moved, not because the agent got worse. That's the
difference between "the agent regressed" and "the baseline is wrong" — both
produce the same alert, and knowing which one happened is a judgment call,
not something the script can tell you.

## FAQ — explained in plain terms

"Every model upgrade or prompt tweak reruns the same golden suite before
rollout. If the pass rate drops outside a tolerance band, that's a release
blocker — the same discipline as a failing CI test, applied to a system that
doesn't behave identically every time."
