"""Module 7 — working example: estimating LLM spend at enterprise scale.

Concept: cost per call is (input tokens * input price) + (output tokens *
output price), multiplied by call volume — but the biggest hidden cost
driver in agents is context bloat: every tool result gets resent on every
loop iteration, so cost grows faster than step count unless it's controlled.

Run: python token_cost_calculator.py
"""

PRICES = {  # $ per million tokens, illustrative
    "claude-sonnet-5": {"input": 3.00, "output": 15.00},
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    p = PRICES[model]
    return (input_tokens / 1e6) * p["input"] + (output_tokens / 1e6) * p["output"]


def monthly_cost(calls_per_day: int, tokens_per_call: tuple[int, int], model: str) -> float:
    per_call = estimate_cost(model, *tokens_per_call)
    return per_call * calls_per_day * 30


def context_bloat_demo(base_tokens: int, tool_result_tokens: int, steps: int) -> int:
    """Every loop iteration resends the FULL history, including every prior
    tool result — so a 5-step run doesn't cost 5x one step, it costs the
    sum of 1+2+3+4+5 units of tool-result context, roughly triangular
    growth, not linear."""
    total = 0
    for step in range(1, steps + 1):
        total += base_tokens + tool_result_tokens * step
    return total


if __name__ == "__main__":
    monthly = monthly_cost(calls_per_day=5000, tokens_per_call=(4000, 500), model="claude-sonnet-5")
    print(f"Estimated monthly cost @ 5,000 calls/day: ${monthly:,.2f}\n")

    print("Context bloat: input tokens actually sent as a loop runs longer")
    for steps in [1, 3, 5, 10]:
        tokens = context_bloat_demo(base_tokens=500, tool_result_tokens=300, steps=steps)
        print(f"  {steps:>2} steps -> {tokens:,} cumulative input tokens sent")
    print(
        "\nCaching the static system prompt/tool defs, and trimming stale "
        "tool results before re-injecting them, is usually a bigger lever "
        "than switching to a cheaper model."
    )
