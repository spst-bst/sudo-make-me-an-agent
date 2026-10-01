"""Module 2 — working example: the 5 dimensions of an agent eval result.

Concept: correctness, safety, consistency, latency, and cost together tell
you whether an agent is fit to run unattended at scale. A demo only needs
correctness; a production agent needs all five measured continuously.

Run: python eval_result.py
"""

from dataclasses import dataclass


@dataclass
class EvalResult:
    correctness: float  # 0-1, matched expected outcome
    safety: float  # 0-1, avoided disallowed actions
    consistency: float  # 0-1, agreement across N repeated runs
    latency_ms: float
    cost_usd: float

    def is_production_ready(
        self,
        min_correctness: float = 0.9,
        min_safety: float = 1.0,
        min_consistency: float = 0.85,
        max_latency_ms: float = 5000,
        max_cost_usd: float = 0.10,
    ) -> bool:
        return (
            self.correctness >= min_correctness
            and self.safety >= min_safety
            and self.consistency >= min_consistency
            and self.latency_ms <= max_latency_ms
            and self.cost_usd <= max_cost_usd
        )


if __name__ == "__main__":
    candidates = [
        EvalResult(correctness=0.94, safety=1.0, consistency=0.88, latency_ms=2100, cost_usd=0.04),
        EvalResult(correctness=0.96, safety=0.99, consistency=0.80, latency_ms=1800, cost_usd=0.03),
    ]
    for i, result in enumerate(candidates, 1):
        print(f"Candidate {i}: {result} -> production ready: {result.is_production_ready()}")
