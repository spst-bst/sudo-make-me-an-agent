# Capstone: Code Review Agent

**Deliverable:** `code_review_agent.py` — a script that runs a 4-tool ReAct
loop (`list_files`, `read_file`, `find_issues`, `write_report`) over a
codebase and produces a markdown report of issues with suggested fixes.

`list_files`, `find_issues`, and `write_report` are given to you in
`code_review_agent_starter.py` — your job is to wire them into a tool set
and loop (reuse the pattern from `05-multi-tool-chain/`) and prompt it end
to end. A full reference solution is in `code_review_agent_solution.py` —
try the starter first.

`find_issues` dispatches on file extension: `.py` files get real AST-based
checks (bare `except`, undocumented public functions) via Python's `ast`
module; `.java` files get regex/pattern heuristics for common concurrency
bugs (non-volatile/non-atomic shared fields, threads started without
`join()`, inconsistent lock ordering). Comments are stripped from Java
source before pattern-matching, since a comment like `// no t1.join() here`
otherwise contributes a literal `.join()` substring that masks the bug it's
describing.

## Build it

```bash
python code_review_agent_starter.py
```

Prompt it with: *"List the Java files under sample_project/java, review each
one for concurrency issues, suggest specific fixes for each, and write the
results to a report."* (or point it at `sample_project/main.py` for the
original Python-only version — both work through the same tool set.)

## What success looks like

`review_report.md` exists, lists each issue with a file/line reference and a
concrete fix (not "add error handling"), and you can walk the agent's
tool-call sequence end-to-end without notes — this is your work-sample
artifact for a "show me something you built" conversation.

## Tool chain: who does what

Worth being able to explain this breakdown cold — it's the answer to "walk
me through what happens when the agent reviews a file":

1. **Your prompt** — states the goal in plain language; no ordering implied.
2. **`react_loop`** (reused unmodified from Module 2) — pure plumbing. Sends
   messages + tool specs to the model, dispatches whichever tool the model
   asks for, feeds the result back, repeats until the model stops calling
   tools. It has no idea what Java, concurrency, or "done" mean.
3. **The model** — the planner. Decides the *order* (list → read + find_issues
   per file → write) purely from tool descriptions and prior results; nothing
   in the code hardcodes this sequence.
4. **`list_files`** — discovery: returns candidate files matching a glob.
5. **`read_file`** — fetches raw source; lets the model reason about things no
   static tool checks (e.g. severity, why a fix matters).
6. **`find_issues`** — static analysis: hands back raw, mechanical findings
   per file (no prose, no judgment calls).
7. **The model, again** — synthesis: turns raw findings + full source into
   the polished write-up (explanations, severity, fix code, summary table).
8. **`write_report`** — pure I/O sink: writes whatever markdown string the
   model produced to `review_report.md`.

Net takeaway: tools only supply raw facts, the loop only plumbs messages —
all sequencing, interpretation, and writing is the model's own reasoning.
