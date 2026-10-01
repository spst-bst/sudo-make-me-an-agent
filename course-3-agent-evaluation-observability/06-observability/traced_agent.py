"""Module 6 — working example: structured logging with a trace ID per run.

Concept: log every prompt, tool call with its arguments, tool result, final
response, latency, and token counts. Use one trace ID per user request and
a span ID per tool call, so a multi-step agent run is one traceable unit
instead of disconnected log lines.

Run: python traced_agent.py
"""

import json
import time
import uuid


def log(trace_id: str, event: str, **fields) -> None:
    # One JSON object per line (not pretty-printed) — this is the format
    # log aggregators (Datadog, CloudWatch, etc.) expect: each line is an
    # independently parseable event, and trace_id is just another field they
    # can filter/group on, same as `jq 'select(.trace_id=="...")'` does here.
    print(json.dumps({"trace_id": trace_id, "event": event, **fields}))


def traced_react_loop(user_prompt: str, agent_id: str, tool_calls: list[tuple[str, dict, str]]) -> str:
    """tool_calls simulates what a real react_loop would execute, as
    (tool_name, tool_input, tool_output) tuples, so this module runs
    standalone without needing the real agent or an API key."""
    # Minted once per run, attached to every event below — this is what
    # lets you later pull every log line belonging to this one request out
    # of a stream of many concurrent runs, in order.
    trace_id = str(uuid.uuid4())
    start = time.time()
    log(trace_id, "run_start", agent_id=agent_id, prompt=user_prompt)

    for i, (tool_name, tool_input, tool_output) in enumerate(tool_calls):
        # span_id = trace_id + index: simplest possible scheme that still
        # uniquely identifies "the Nth tool call within this run" — a real
        # system would mint an independent span ID per call, but the
        # loop-index suffix is enough to demonstrate the hierarchy here.
        span_id = f"{trace_id}:{i}"
        span_start = time.time()
        log(trace_id, "tool_call", span_id=span_id, tool=tool_name, input=tool_input)
        # ... the real call would execute the tool here — this module takes
        # tool_output as a pre-supplied value instead, so duration_ms below
        # measures ~nothing (no API key, no real work, no real latency).
        log(
            trace_id,
            "tool_result",
            span_id=span_id,
            tool=tool_name,
            output=tool_output,
            duration_ms=int((time.time() - span_start) * 1000),
        )

    final_answer = "Final answer assembled from the tool results above."
    # run_end brackets run_start with the same trace_id — the pair is what
    # makes "how long did this whole request take" answerable from logs
    # alone, without needing to correlate separate monitoring systems.
    log(trace_id, "run_end", duration_ms=int((time.time() - start) * 1000), agent_id=agent_id)
    return final_answer


if __name__ == "__main__":
    # tool_calls is hardcoded here rather than produced by a real agent —
    # see the exercise in README.md for wiring this logging into the
    # actual Course 1 react_loop, where these tuples would instead come
    # from real tool_use blocks and real tool execution.
    result = traced_react_loop(
        user_prompt="What is MCP, and what is 12 * (7 + 3)?",
        agent_id="react-loop-demo",
        tool_calls=[
            ("search_docs", {"query": "mcp"}, "MCP is a protocol for connecting tools to LLMs."),
            ("calculator", {"expression": "12 * (7 + 3)"}, "120"),
        ],
    )
    print(f"\nResult: {result}")
