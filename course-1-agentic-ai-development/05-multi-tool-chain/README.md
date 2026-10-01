# Module 5: Multi-step agent — chaining 3 tools

Real agent tasks rarely resolve in one tool call — the output of one tool
becomes the input to deciding the next, and the model has to track state
across the chain without you hardcoding the order. This module extends the
Module 2 loop with three tools that have a natural dependency (list → read →
analyze) so you can watch the model sequence them correctly on its own. The
loop itself doesn't change from Module 2 — only the tool set does, which is
the point: a well-built loop scales to N tools with no modification.

## Run the working example

```bash
python example_solution.py
```

## Exercise

Run the prompt in `example_solution.py` and log each step's action and
observation. Confirm the model calls `list_py_files` first, `count_lines` on
each candidate, then `read_file` only on the winner — with no ordering
hardcoded anywhere in the code.

## What success looks like

The model completes the task in 3–5 tool calls with the sequencing logic
living entirely in its own reasoning, driven only by the tools' descriptions.
