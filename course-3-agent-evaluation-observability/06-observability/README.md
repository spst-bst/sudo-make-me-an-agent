# Module 6: Observability for agents

Log every prompt, every tool call with its arguments, every tool result, the
final response, latency, and token counts. Use one **trace ID per user
request** and a **span ID per tool call**, so a multi-step agent run is one
traceable unit instead of disconnected log lines — without that, debugging a
multi-step failure is guesswork.

## Run it

```bash
python traced_agent.py
```

Every line is a JSON log event sharing the same `trace_id` — that's what
lets you reconstruct one agent run from a pile of logs later. Pipe the
output through `jq 'select(.trace_id=="<id>")'` to see the filtering in
action once you have a real trace ID.

## Exercise

Wire this into the real Course 1 `react_loop` — wrap each tool execution
call with a `log(..., "tool_call", ...)` before and `log(..., "tool_result",
...)` after, instead of the pre-baked `tool_calls` list this demo uses.

## FAQ — explained in plain terms

"If an agent misbehaves in production, the trace ID is what lets us
reconstruct exactly which tool calls it made, in what order, and why —
without that, we're debugging a multi-step failure from memory and
guesswork."
