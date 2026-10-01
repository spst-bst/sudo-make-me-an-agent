"""Small math helpers used by main.py."""


def add(*values: float) -> float:
    """Return the sum of the given values."""
    return sum(values)


def divide(numerator: float, denominator: float) -> float:
    """Return numerator / denominator."""
    return numerator / denominator
