"""Module 2 — exercise: surface the "Thought" step, and prove the guard works.

TODO:
1. In the tool_use handling loop, also print any block.type == "text"
   content that arrives alongside the tool_use blocks — that's the model's
   reasoning ("Thought") before it acts.
2. Call react_loop(..., max_steps=1) with a prompt that needs two tool
   calls (like the example's) and confirm you get the max-steps message
   instead of a silent wrong answer.

Run: python exercise_starter.py
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
    return str(eval(expression, {"__builtins__": {}}))


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
    for step in range(max_steps):
        response = client.messages.create(
            model="claude-sonnet-5", max_tokens=1024, tools=TOOL_SPECS, messages=messages
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            return response.content[0].text

        tool_results = []
        for block in response.content:
            if block.type == "text":
                print(f"[step {step}] thought={block.text!r}")
            if block.type == "tool_use":
                output = TOOLS[block.name](**block.input)
                print(f"[step {step}] action={block.name}({block.input}) observation={output!r}")
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": output}
                )
        messages.append({"role": "user", "content": tool_results})

    return "Max steps reached without a final answer."


if __name__ == "__main__":
    prompt = "Before answering, briefly explain your plan, then look up MCP and compute 12 * (7 + 3)."

    print("=== default max_steps (should finish with a real answer) ===")
    print(react_loop(prompt))

    print("\n=== max_steps=1 (should hit the guard, not a silent wrong answer) ===")
    print(react_loop(prompt, max_steps=1))
