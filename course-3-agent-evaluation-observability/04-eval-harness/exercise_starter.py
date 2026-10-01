"""Module 4 — exercise: point the harness at the real Course 1 agent.

TODO:
1. Import react_loop from ../../course-1-agentic-ai-development/02-react-loop/
   (see the commented example at the bottom of eval_harness.py).
2. Add at least one TestCase that requires a real tool call (e.g. something
   your calculator or search_docs tool can answer), not just knowledge.
3. Run run_eval_suite against react_loop with repeats=5 and summarize().
4. Requires ANTHROPIC_API_KEY in the environment.

Run: python exercise_starter.py
"""

import sys
from pathlib import Path

from eval_harness import EvalRun, TestCase, run_eval_suite, score, summarize  # noqa: F401

sys.path.insert(
    0,
    str(
        Path(__file__).parent.parent.parent
        / "course-1-agentic-ai-development"
        / "02-react-loop"
    ),
)
from example_solution import react_loop  # noqa: E402

TEST_CASES = [
    TestCase(prompt="What is MCP?", expected_contains=["protocol", "tool"]),
    # Requires a real tool call (the calculator tool), not just recalled
    # knowledge — exercises the actual request/execute/feed-back loop.
    TestCase(prompt="What is 12 * (7 + 3)?", expected_contains=["120"]),
]

if __name__ == "__main__":
    results = run_eval_suite(react_loop, TEST_CASES, repeats=5)
    summarize(results)
