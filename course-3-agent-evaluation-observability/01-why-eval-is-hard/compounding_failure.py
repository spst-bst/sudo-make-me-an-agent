"""Module 1 — working example: why per-step reliability doesn't tell you
end-to-end reliability.

Concept: agent evaluation breaks the usual unit-test model in three ways —
non-determinism (same prompt, different run, different outcome),
multi-step failure amplification (errors compound rather than average),
and context sensitivity (a small prompt/tool-description change can shift
behavior far more than the equivalent change would in deterministic code).
This script demonstrates the second one concretely.

Run: python compounding_failure.py
"""


def end_to_end_reliability(per_step_success: float, steps: int) -> float:
    return per_step_success**steps


if __name__ == "__main__":
    per_step_success = 0.95
    print(f"Per-step success rate: {per_step_success:.0%}\n")
    for steps in [1, 3, 5, 10, 20]:
        rate = end_to_end_reliability(per_step_success, steps)
        print(f"{steps:>2} steps -> {rate:.0%} end-to-end success")

    print(
        "\nA 95%-reliable step, chained 5 times, drops to ~77% end-to-end. "
        "That's the number that actually matters to the business, not the "
        "per-step number."
    )
