"""Module 2 — working example: a hand-built ReAct loop.

Run: python example_solution.py
Requires: ANTHROPIC_API_KEY in the environment.
"""

import anthropic

client = anthropic.Anthropic()


def search_docs(query: str) -> str:
    fake_index = {
        "kubernetes": "K8s is a container orchestrator.",
        "mcp": "MCP is a protocol for connecting tools to LLMs.",
    }
    return fake_index.get(query.lower(), "No match found.")


def calculator(expression: str) -> str:
    return str(eval(expression, {"__builtins__": {}}))  # demo only — sandbox in real use


TOOLS = {"search_docs": search_docs, "calculator": calculator}
TOOL_SPECS = [
    {
        "name": "search_docs",
        "description": "Search internal docs by keyword.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "calculator",
        "description": "Evaluate a math expression.",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    },
]


def react_loop(user_prompt: str, max_steps: int = 5) -> str:
    messages = [{"role": "user", "content": user_prompt}]
    print(f"[start] prompt={user_prompt!r}")

    for step in range(max_steps):
        print(f"\n===== step {step} — calling model with {len(messages)} message(s) in history =====")
        response = client.messages.create(
            model="claude-sonnet-5", max_tokens=4096, tools=TOOL_SPECS, messages=messages
        )
        block_types = [b.type for b in response.content]
        print(f"[step {step}] stop_reason={response.stop_reason} "
              f"usage=in:{response.usage.input_tokens}/out:{response.usage.output_tokens} "
              f"blocks={block_types}")
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            # stop_reason != "tool_use" does NOT guarantee content[0] is a
            # finished text block — e.g. stop_reason="max_tokens" can cut
            # generation off mid-"thinking" block, which has no .text attr.
            # Pull out whatever text blocks did complete instead of assuming
            # position 0 is safe to index.
            text_blocks = [b.text for b in response.content if b.type == "text"]
            if not text_blocks:
                print(f"[step {step}] stop_reason={response.stop_reason} but no completed "
                      f"text block (blocks={block_types}) — likely truncated mid-generation")
                return (f"Error: response ended with stop_reason={response.stop_reason} "
                        f"and no usable text content. Try raising max_tokens.")
            print(f"[step {step}] no tool_use block — treating as final answer, loop ends")
            return "\n".join(text_blocks)

        tool_results = []
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"[step {step}] thought={block.text.strip()!r}")
            elif block.type == "tool_use":
                print(f"[step {step}] action={block.name} input={block.input} tool_use_id={block.id}")
                try:
                    output = TOOLS[block.name](**block.input)
                except Exception as exc:  # surfaced to the model as an observation, not raised
                    output = f"Error: {exc}"
                    print(f"[step {step}] tool {block.name} raised: {exc!r}")
                print(f"[step {step}] observation={output}")
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": output}
                )
        print(f"[step {step}] appending {len(tool_results)} tool_result(s) back into messages, "
              f"looping to step {step + 1}")
        messages.append({"role": "user", "content": tool_results})

    print(f"\n===== guard fired — max_steps={max_steps} reached without end_turn =====")
    return "Max steps reached without a final answer."


if __name__ == "__main__":
    print(react_loop("Explain your plan, then look up MCP and compute 12 * (7 + 3)?"))
