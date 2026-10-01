"""Capstone — starter: wire read_file, find_issues, write_report into an agent.

read_file, find_issues, and write_report are done for you below. TODO:

1. Import react_loop from 02-react-loop/example_solution.py (see the
   sys.path pattern used in 05-multi-tool-chain/example_solution.py).
2. Build TOOLS and TOOL_SPECS for these three functions (follow the shape
   used in every prior module).
3. Swap them into the imported react_loop module's globals.
4. Call react_loop with the prompt below and print the result.
5. Confirm review_report.md is created with real findings.

Run: python code_review_agent_starter.py
Requires: ANTHROPIC_API_KEY in the environment.
"""

import ast
import re
from pathlib import Path

ROOT = (Path(__file__).parent.parent / "sample_project").resolve()

PROMPT = (
    "List the Java files under sample_project/java, review each one for "
    "concurrency issues, suggest specific fixes for each, and write the "
    "results to a report."
)


def list_files(pattern: str) -> str:
    matches = sorted(ROOT.rglob(pattern))
    return "\n".join(str(p.relative_to(ROOT)) for p in matches)


def read_file(relative_path: str) -> str:
    return (ROOT / relative_path).read_text()


def _find_python_issues(source: str) -> list[str]:
    """AST-based checks: bare except, undocumented public functions."""
    issues = []
    if "except:" in source:
        issues.append("Bare except clause — catches SystemExit/KeyboardInterrupt too.")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.FunctionDef)
            and not ast.get_docstring(node)
            and not node.name.startswith("_")
        ):
            issues.append(f"Public function '{node.name}' (line {node.lineno}) has no docstring.")
    return issues


# Java has no stdlib AST like Python's `ast` module, so these are plain
# regex/string heuristics aimed at the specific concurrency bug shapes this
# course plants — not a real parser, and not exhaustive.
_JAVA_INCREMENT_RE = re.compile(r"\b(\w+)\s*(?:\+\+|--)\s*;")
_JAVA_VOLATILE_FIELDS_RE = re.compile(r"private\s+volatile\s+\w+\s+(\w+)")
_JAVA_FIELD_RE = re.compile(r"private\s+(?:boolean|int|long|double)\s+(\w+)\s*(?:=|;)")
_JAVA_NESTED_LOCK_RE = re.compile(
    r"synchronized\s*\(\s*(\w+)\s*\)\s*\{[^{}]*?synchronized\s*\(\s*(\w+)\s*\)", re.DOTALL
)


def _strip_java_comments(source: str) -> str:
    """Drop // and /* */ comments before pattern-matching.

    Without this, a comment like '// BUG: no t1.join() here' contributes a
    literal ".join()" substring that the checks below would count as real
    code, masking the exact bug it's describing.
    """
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", "", source)


def _extract_synchronized_bodies(source: str) -> str:
    """Concatenated text inside every synchronized(...) { ... } block.

    Needs manual brace-matching (not regex) because the blocks nest, e.g.
    synchronized(a) { synchronized(b) { ... } } — a naive regex would stop
    at the first inner '}' and truncate the outer block.
    """
    bodies = []
    for m in re.finditer(r"synchronized\s*\([^)]*\)\s*\{", source):
        depth, i = 1, m.end()
        while i < len(source) and depth > 0:
            depth += source[i] == "{"
            depth -= source[i] == "}"
            i += 1
        bodies.append(source[m.end() : i - 1])
    return "\n".join(bodies)


def _find_java_issues(source: str) -> list[str]:
    """Pattern-based checks for common Java concurrency bugs."""
    issues = []
    is_threaded = "Thread" in source or "Runnable" in source

    if is_threaded:
        synchronized_text = _extract_synchronized_bodies(source)
        volatile_fields = set(_JAVA_VOLATILE_FIELDS_RE.findall(source))
        incremented = set(_JAVA_INCREMENT_RE.findall(source))
        for field in sorted(set(_JAVA_FIELD_RE.findall(source)) - volatile_fields):
            total = len(re.findall(rf"\b{re.escape(field)}\b", source))
            guarded = len(re.findall(rf"\b{re.escape(field)}\b", synchronized_text))
            if total - 1 <= guarded:  # -1 excludes the field's own declaration line
                continue  # every real use is already inside a synchronized block
            if field in incremented:
                issues.append(
                    f"Field '{field}' is incremented/decremented with ++/-- outside "
                    f"any synchronized block and isn't volatile/atomic — lost-update "
                    f"race across threads."
                )
            else:
                issues.append(
                    f"Field '{field}' is mutable, accessed outside any synchronized "
                    f"block, and isn't volatile — writes from one thread may never "
                    f"become visible to another thread."
                )

        starts, joins = source.count(".start()"), source.count(".join()")
        if starts > joins:
            issues.append(
                f"{starts} thread(s) started via .start() but only {joins} .join() "
                f"call(s) — code after start() may run before the threads finish, "
                f"reading stale/partial state."
            )

    lock_pairs = _JAVA_NESTED_LOCK_RE.findall(source)
    reported = set()
    for first, second in lock_pairs:
        if first != second and (second, first) in lock_pairs:
            key = frozenset((first, second))
            if key in reported:
                continue
            reported.add(key)
            a, b = sorted((first, second))
            issues.append(
                f"Locks '{a}' and '{b}' are acquired in opposite orders in different "
                f"methods — classic deadlock risk if two threads call them "
                f"concurrently."
            )

    return issues


def find_issues(relative_path: str) -> str:
    source = (ROOT / relative_path).read_text()
    if relative_path.endswith(".java"):
        issues = _find_java_issues(_strip_java_comments(source))
    else:
        issues = _find_python_issues(source)
    return "\n".join(issues) if issues else "No issues found."


def write_report(content: str) -> str:
    report_path = Path(__file__).parent / "review_report.md"
    report_path.write_text(content)
    return f"Report written to {report_path}"


# TODO: build TOOLS = {...} and TOOL_SPECS = [...] for list_files, read_file,
# find_issues, write_report, then import + call react_loop with PROMPT (see
# 05-multi-tool-chain for the exact pattern of swapping a module's
# TOOLS/TOOL_SPECS globals). Use max_steps=10 — this prompt needs more
# round trips than the single-file version (list, then find_issues + read_file
# per Java file, then write_report).

if __name__ == "__main__":
    raise SystemExit(
        "TODO: wire up react_loop with the tools above, then run this file."
    )
