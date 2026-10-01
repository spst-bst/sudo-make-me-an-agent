"""Module 1 — working example: a single tool-use round trip, with debug
logging at every step so you can see exactly what crosses the wire.

Run: python example_solution.py
Requires: ANTHROPIC_API_KEY in the environment.
"""

import json

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY

tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    }
]


def get_weather(city: str) -> str:
    return f"{city}: 68F, partly cloudy"  # stub — swap for a real API call


def step(label: str) -> None:
    print(f"\n{'=' * 10} {label} {'=' * 10}")


def dump(obj) -> None:
    """Pretty-print a dict/list, or an SDK object via its .model_dump()."""
    if hasattr(obj, "model_dump"):
        obj = obj.model_dump()
    print(json.dumps(obj, indent=2, default=str))


def main() -> None:
    messages = [{"role": "user", "content": "What's the weather in Austin?"}]

    step("1. OUTGOING REQUEST #1")
    print(f"model:    claude-sonnet-5")
    print(f"tools:    {[t['name'] for t in tools]}")
    print(f"messages: {len(messages)} message(s) — the user's question only, so far")
    dump(messages)

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        tools=tools,
        messages=messages,
        thinking={"type": "adaptive", "display": "summarized"}
    )

    step("2. RAW RESPONSE #1")
    print(f"stop_reason: {response.stop_reason!r}")
    print(f"content blocks returned: {[b.type for b in response.content]}")
    dump(response.content)

    if response.stop_reason == "tool_use":
        tool_block = next(b for b in response.content if b.type == "tool_use")

        step("3. MODEL PROPOSED A TOOL CALL")
        print(f"tool_use_id: {tool_block.id}")
        print(f"tool name:   {tool_block.name}")
        print(f"tool input:  {tool_block.input}  (already JSON-parsed by the SDK)")

        step("4. YOUR CODE EXECUTES IT LOCALLY")
        print(f"calling get_weather(**{tool_block.input}) ...")
        result = get_weather(**tool_block.input)
        print(f"local function returned: {result!r}")

        step("5. APPENDING TO HISTORY BEFORE THE NEXT CALL")
        print("appending the assistant's tool_use turn (not just its text) ...")
        messages.append({"role": "assistant", "content": response.content})
        print("appending a user turn carrying the tool_result, linked by tool_use_id ...")
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": tool_block.id, "content": result}
                ],
            }
        )

        step("6. OUTGOING REQUEST #2 — full history resent (the API is stateless)")
        print(f"messages: {len(messages)} message(s) now")
        dump(messages)

        final = client.messages.create(
            model="claude-sonnet-5", max_tokens=1024, tools=tools, messages=messages, thinking={"type": "adaptive", "display": "summarized"}
        )

        step("7. RAW RESPONSE #2")
        print(f"stop_reason: {final.stop_reason!r}  (no more tool_use — Claude is done)")
        dump(final.content)

        step("8. FINAL ANSWER")
        print(final.content[0].text)
    else:
        step("MODEL ANSWERED WITHOUT ANY TOOL CALL")
        print(response.content[0].text)


if __name__ == "__main__":
    main()
