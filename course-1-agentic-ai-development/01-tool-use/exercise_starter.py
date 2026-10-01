"""Module 1 — exercise (solved): a two-tool parallel call.

get_time was added alongside get_weather, and the prompt below asks a
question that needs both in one turn. The interesting part is handling
MULTIPLE tool_use blocks in a single response.content — executing every one
of them, then sending all their results back as ONE user message.

Run: python exercise_starter.py
Requires: ANTHROPIC_API_KEY in the environment.
"""

import anthropic

client = anthropic.Anthropic()

tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
    {
        "name": "get_time",
        "description": "Get the current time for a timezone.",
        "input_schema": {
            "type": "object",
            "properties": {"timezone": {"type": "string"}},
            "required": ["timezone"],
        },
    }
]


def get_weather(city: str) -> str:
    return f"{city}: 68F, partly cloudy"


def get_time(timezone: str) -> str:
    return f"{timezone}: 14:32"


TOOL_FNS = {"get_weather": get_weather, "get_time": get_time}


def main() -> None:
    messages = [{"role": "user", "content": "What's the weather in Boston?"}]

    response = client.messages.create(
        model="claude-sonnet-5", max_tokens=1024, tools=tools, messages=messages
    )

    if response.stop_reason == "tool_use":
        # response.content may also hold a ThinkingBlock — filter to tool_use only.
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
        print(f"Model requested {len(tool_use_blocks)} tool call(s): "
              f"{[b.name for b in tool_use_blocks]}")

        # Must append the FULL response.content (thinking + all tool_use blocks),
        # not just the tool_use blocks you filtered above — see 01-tool-use/README.md
        # Deep dive §3 and §7.
        messages.append({"role": "assistant", "content": response.content})

        # Execute every tool_use block, then send ALL results back in ONE user
        # message — never split parallel results across multiple messages.
        tool_results = []
        for block in tool_use_blocks:
            output = TOOL_FNS[block.name](**block.input)
            print(f"  {block.name}({block.input}) -> {output!r}")
            tool_results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": output}
            )
        messages.append({"role": "user", "content": tool_results})

        final = client.messages.create(
            model="claude-sonnet-5", max_tokens=1024, tools=tools, messages=messages
        )
        print(f"\n{final.content[0].text}")
    else:
        print(response.content[0].text)


if __name__ == "__main__":
    main()
