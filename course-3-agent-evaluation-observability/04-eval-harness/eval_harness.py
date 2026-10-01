"""Module 4 — working example: a minimal evaluation harness.

Runs standalone against a mock agent (no API key needed) so you can see the
scoring/repeats logic work immediately. To point it at your real Course 1
agent instead, see the bottom of this file.

Run: python eval_harness.py
"""

import random
from dataclasses import dataclass


@dataclass
class TestCase:
    prompt: str
    expected_contains: list[str]


@dataclass
class EvalRun:
    test_case: TestCase
    output: str
    passed: bool


TEST_CASES = [
    TestCase(prompt="What is MCP?", expected_contains=["protocol", "tool"]),
    TestCase(prompt="What is 12 * 13?", expected_contains=["156"]),
]


def mock_agent_fn(prompt: str) -> str:
    """Stands in for a real agent — occasionally 'wrong' to show non-determinism."""
    answers = {
        "What is MCP?": "MCP is a protocol that connects tools to LLMs.",
        "What is 12 * 13?": "12 * 13 is 156.",
    }
    output = answers.get(prompt, "I don't know.")
    if random.random() < 0.15:  # simulate ~15% flakiness, like a real model
        output = "I'm not sure."
    return output


def score(output: str, expected_contains: list[str]) -> bool:
    return all(term.lower() in output.lower() for term in expected_contains)


def run_eval_suite(agent_fn, test_cases: list[TestCase], repeats: int = 5) -> list[EvalRun]:
    results = []
    for case in test_cases:
        for _ in range(repeats):
            output = agent_fn(case.prompt)
            results.append(EvalRun(case, output, score(output, case.expected_contains)))
    return results


def summarize(results: list[EvalRun]) -> None:
    total = len(results)
    passed = sum(r.passed for r in results)
    print(f"Pass rate: {passed}/{total} ({passed / total:.0%})")
    for r in results:
        if not r.passed:
            print(f"  FAIL: '{r.test_case.prompt}' -> {r.output[:80]}")


if __name__ == "__main__":
    results = run_eval_suite(mock_agent_fn, TEST_CASES, repeats=10)
    summarize(results)

    # --- To evaluate the real Course 1 agent instead of the mock: ---
    # import sys
    # from pathlib import Path
    # sys.path.insert(0, str(Path(__file__).parent.parent.parent
    #     / "course-1-agentic-ai-development" / "02-react-loop"))
    # from example_solution import react_loop
    # results = run_eval_suite(react_loop, TEST_CASES, repeats=5)
    # summarize(results)
