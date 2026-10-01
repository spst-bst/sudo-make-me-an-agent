"""Module 5 — working example: regression testing against a frozen baseline.

Concept: freeze a golden test suite and its baseline pass rate per
model/prompt version; re-run it on every model upgrade, prompt edit, or
tool-description change; diff against baseline with a tolerance band (some
variance is normal given non-determinism, so flag only drops beyond it, not
any drop at all).

Run: python regression_check.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "04-eval-harness"))
from eval_harness import TEST_CASES, mock_agent_fn, run_eval_suite  # noqa: E402

BASELINE_PASS_RATE = 0.90
TOLERANCE = 0.05


def check_regression(results: list) -> bool:
    pass_rate = sum(r.passed for r in results) / len(results)
    regressed = pass_rate < BASELINE_PASS_RATE - TOLERANCE
    status = "REGRESSED — block release" if regressed else "OK — safe to release"
    print(
        f"Current: {pass_rate:.0%}, baseline: {BASELINE_PASS_RATE:.0%}, "
        f"tolerance: ±{TOLERANCE:.0%} -> {status}"
    )
    return regressed


if __name__ == "__main__":
    results = run_eval_suite(mock_agent_fn, TEST_CASES, repeats=20)
    blocked = check_regression(results)
    sys.exit(1 if blocked else 0)  # non-zero exit -> fails a CI gate
