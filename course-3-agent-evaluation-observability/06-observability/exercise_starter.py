"""Module 6 — exercise: wire structured trace logging into the real agent loop.

traced_agent.py's working example takes pre-baked (tool, input, output)
tuples and logs around them — no model call, so duration_ms is always ~0.
This re-implements the request/execute/feed-back cycle against a real
model (reusing the real search_docs/calculator tools from Course 1 Module
2), with log() calls wrapping actual tool execution instead of react_loop's
plain print() debugging — so duration_ms reflects genuine API/tool latency
and the tool sequence reflects genuine model decisions, not a scripted list.

Run: python exercise_starter.py
Requires: ANTHROPIC_API_KEY in the environment.
"""

import sys
import time
import uuid
from pathlib import Path

import anthropic

from traced_agent import log

sys.path.insert(
    0,
    str(
        Path(__file__).parent.parent.parent
        / "course-1-agentic-ai-development"
        / "02-react-loop"
    ),
)
from example_solution import TOOLS, TOOL_SPECS  # noqa: E402 -- reuse the real tools, not the loop

client = anthropic.Anthropic()


def traced_react_loop(user_prompt: str, agent_id: str, max_steps: int = 5) -> str:
    trace_id = str(uuid.uuid4())
    start = time.time()
    log(trace_id, "run_start", agent_id=agent_id, prompt=user_prompt)

    messages = [{"role": "user", "content": user_prompt}]

    for step in range(max_steps):
        response = client.messages.create(
            model="claude-sonnet-5", max_tokens=4096, tools=TOOL_SPECS, messages=messages
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            text_blocks = [b.text for b in response.content if b.type == "text"]
            final_answer = "\n".join(text_blocks) if text_blocks else "(no text content)"
            log(trace_id, "run_end", duration_ms=int((time.time() - start) * 1000), agent_id=agent_id)
            return final_answer

        tool_results = []
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
        for i, block in enumerate(tool_use_blocks):
            span_id = f"{trace_id}:{step}.{i}"
            span_start = time.time()
            log(trace_id, "tool_call", span_id=span_id, tool=block.name, input=block.input)
            try:
                output = TOOLS[block.name](**block.input)
            except Exception as exc:  # surfaced to the model as an observation, not raised
                output = f"Error: {exc}"
            log(
                trace_id,
                "tool_result",
                span_id=span_id,
                tool=block.name,
                output=output,
                duration_ms=int((time.time() - span_start) * 1000),
            )
            tool_results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": output}
            )
        messages.append({"role": "user", "content": tool_results})

    log(
        trace_id,
        "run_end",
        duration_ms=int((time.time() - start) * 1000),
        agent_id=agent_id,
        note="max_steps reached",
    )
    return "Max steps reached without a final answer."


if __name__ == "__main__":
    result = traced_react_loop(
        user_prompt="What is MCP, and what is 12 * (7 + 3)?",
        agent_id="react-loop-real",
    )
    print(f"\nResult: {result}")
