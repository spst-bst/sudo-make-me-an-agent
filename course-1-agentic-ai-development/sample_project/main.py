"""Tiny fixture app used by the MCP and code-review exercises.

Deliberately contains a few issues for the capstone agent to find:
bare except, a public function with no docstring, and a long line.
"""

from utils import add, divide


def run_report(values):
    total = add(*values)
    try:
        average = divide(total, len(values))
    except:
        average = 0
    return {"total": total, "average": average}


def format_report(report, currency_symbol="$", locale="en_US", include_totals=True, include_average=True):
    return f"{currency_symbol}{report['total']} total, {currency_symbol}{report['average']} average"


if __name__ == "__main__":
    data = [10, 20, 30, 40]
    print(format_report(run_report(data)))
