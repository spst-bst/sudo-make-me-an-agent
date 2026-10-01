"""Module 5 — working example: chaining 3 tools (list -> count -> read).

Reuses the same react_loop from Module 2 — only the tool set changes.

The point of this module: Module 2's react_loop() has no idea what tools it's
calling or why. It just sends whatever is in TOOL_SPECS to the model, and
dispatches whatever tool_use blocks come back to whatever is in TOOLS. That
means we can swap in a completely different, interdependent set of tools
(list -> count -> read) without touching a single line of the loop itself.
The *sequencing* (which tool to call first, second, third) is decided by
Claude at runtime from the tool descriptions and the running conversation —
not by any if/else we write here.

Run: python example_solution.py
Requires: ANTHROPIC_API_KEY in the environment.
"""

import sys
from pathlib import Path

import anthropic

# Module 2 (02-react-loop/example_solution.py) defines react_loop() plus its
# own TOOLS/TOOL_SPECS globals. We don't want to copy/paste the loop, so we
# add that directory to sys.path and import the module directly. This is a
# teaching shortcut, not a packaging pattern you'd use in production code —
# a real project would make react_loop importable via a proper package.
sys.path.insert(0, str(Path(__file__).parent.parent / "02-react-loop"))
import example_solution as react_module  # noqa: E402 -- reuse Module 2's loop

client = anthropic.Anthropic()

# All file paths the tools hand back to the model are relative to this root.
# Resolving it once, up front, means every tool function below can do
# `ROOT / relative_path` without worrying about the current working
# directory the script happens to be launched from.
ROOT = (Path(__file__).parent.parent / "sample_project").resolve()


def list_py_files(_: dict = {}) -> str:
    """Tool 1 — discovery. Returns every .py file under sample_project.

    This has no required inputs, but Claude's tool-use protocol always sends
    a JSON object as the tool input (an empty {} here), so the function
    still needs to accept one positional/keyword arg even though it's
    unused. This is the tool the model is expected to call *first*, since
    every other tool needs a relative_path that only this one can supply.
    """
    files = list(ROOT.rglob("*.py"))
    print(f"[tool:list_py_files] scanned {ROOT}")
    print(f"[tool:list_py_files] found {len(files)} file(s):")
    for f in files:
        print(f"[tool:list_py_files]   - {f.relative_to(ROOT)}")
    return "\n".join(str(p.relative_to(ROOT)) for p in files)


def read_file(relative_path: str) -> str:
    """Tool 3 — content retrieval. Reads one file's full text by path.

    Expensive relative to count_lines (returns the whole file, not just a
    number), which is exactly why a well-reasoning model should call this
    *last*, only on the single file it has already decided is the answer —
    not on every candidate.
    """
    path = ROOT / relative_path
    content = path.read_text()
    print(
        f"[tool:read_file] relative_path={relative_path!r} -> "
        f"{len(content)} chars / {len(content.splitlines())} lines read"
    )
    return content


def count_lines(relative_path: str) -> str:
    """Tool 2 — cheap metric. Returns the line count of one file as a string.

    Returning str (not int) matters: tool_result content blocks are text,
    so whatever a tool returns gets stringified anyway for the model — doing
    it explicitly here avoids relying on implicit conversion.
    """
    path = ROOT / relative_path
    line_count = len(path.read_text().splitlines())
    print(f"[tool:count_lines] relative_path={relative_path!r} -> {line_count} lines")
    return str(line_count)


# TOOLS maps a tool name (as the model will reference it in a tool_use
# block) to the actual Python callable the loop should run.
TOOLS = {"list_py_files": list_py_files, "read_file": read_file, "count_lines": count_lines}

# TOOL_SPECS is what actually gets sent to the Anthropic API. The model
# never sees our Python code — it only sees these name/description/
# input_schema entries, and decides which tool to call (and in what order)
# purely from this text. If the descriptions were vague or wrong, the model
# could just as easily call read_file on every candidate before counting
# lines, or skip count_lines altogether — the schema is the entire contract.
TOOL_SPECS = [
    {
        "name": "list_py_files",
        "description": "List all Python files in the project.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "read_file",
        "description": "Read a file's contents by relative path.",
        "input_schema": {
            "type": "object",
            "properties": {"relative_path": {"type": "string"}},
            "required": ["relative_path"],
        },
    },
    {
        "name": "count_lines",
        "description": "Count lines in a file by relative path.",
        "input_schema": {
            "type": "object",
            "properties": {"relative_path": {"type": "string"}},
            "required": ["relative_path"],
        },
    },
]

if __name__ == "__main__":
    # react_loop() in Module 2 reads TOOLS/TOOL_SPECS as module-level
    # globals *inside react_module*, not as function arguments. So to point
    # the same loop at a different tool set, we overwrite those globals on
    # the imported module object before calling it. This works because
    # Python modules are just mutable objects — react_loop looks these up
    # by name at call time, after we've already replaced them.
    print("[main] swapping react_module.TOOLS/TOOL_SPECS with Module 5's 3-tool set")
    react_module.TOOLS = TOOLS
    react_module.TOOL_SPECS = TOOL_SPECS

    prompt = "Find the largest Python file by line count and show me its contents."
    print(f"[main] invoking react_loop with prompt={prompt!r}")

    result = react_module.react_loop(prompt)

    print("\n[main] ===== final answer =====")
    print(result)
