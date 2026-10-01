# Module 1: How tool use / function calling works

The model doesn't execute code — you give it a schema describing available
tools (name, description, JSON Schema for inputs), and when it decides a tool
would help, it returns a structured `tool_use` block instead of plain text.
Your code executes the requested function with those arguments, then sends
the result back as a `tool_result` message so the model can continue
reasoning with the new information. This propose → execute → feed-back cycle
is the entire mechanism underneath every agent framework you'll encounter.

## Deep dive

### 1. The tool definition — what Claude actually sees

Every tool needs three things:

```json
{
  "name": "get_weather",
  "description": "Get the current weather for a city.",
  "input_schema": {
    "type": "object",
    "properties": {"city": {"type": "string"}},
    "required": ["city"]
  }
}
```

That's exactly what `example_solution.py` sends. The critical detail most
people get wrong: **the `description` is the only thing Claude uses to
decide *when* to call the tool.** It's not documentation for you — it's the
decision criterion for the model. A vague description ("weather stuff") gets
skipped or misused; a prescriptive one ("Call this when the user asks about
current conditions in a specific city") gets triggered reliably. This
matters even more on recent models, which have gotten more conservative
about reaching for tools — a description that only states *what* the tool
does, without *when* to use it, measurably under-triggers.

### 2. What "the model requests a tool" actually looks like on the wire

When Claude decides a tool would help, the response isn't special — it's a
normal `Message` object, but:

- `response.stop_reason` is `"tool_use"` (instead of `"end_turn"`)
- `response.content` contains a `tool_use` content block shaped like:

```json
{
  "type": "tool_use",
  "id": "toolu_01A09q90qw90lq917835lq9",
  "name": "get_weather",
  "input": {"city": "Austin"}
}
```

That `id` is important — it's how the result you send back gets matched to
*this specific request*. In the example script:

```python
tool_block = next(b for b in response.content if b.type == "tool_use")
result = get_weather(**tool_block.input)
```

`tool_block.input` has already been JSON-parsed for you by the SDK into a
Python dict — that's why `**tool_block.input` works directly as kwargs.

### 3. Sending the result back — and why the whole history goes with it

The Messages API is **completely stateless** per request — there's no
session on Anthropic's side remembering what you asked before. So every
follow-up call has to resend the *entire* conversation, including Claude's
own prior turn:

```python
messages.append({"role": "assistant", "content": response.content})  # Claude's tool_use request
messages.append({
    "role": "user",
    "content": [{"type": "tool_result", "tool_use_id": tool_block.id, "content": result}]
})
```

Two things people miss here:

- You must append `response.content` (the raw content blocks), not just the
  text — if you extract and resend only a string summary, the `tool_use`
  block is gone and Claude has no record of what it asked for.
- `tool_result` blocks are sent with `role: "user"` — they're structurally a
  user turn from the API's point of view, "here's data you asked for," not
  an assistant turn.

### 4. Controlling *whether* Claude uses tools at all — `tool_choice`

The example uses the default (`"auto"` — Claude decides), but there are four
modes:

| Value | Behavior |
| --- | --- |
| `{"type": "auto"}` | Claude decides (default) |
| `{"type": "any"}` | Claude must call *some* tool |
| `{"type": "tool", "name": "..."}` | Claude must call *this specific* tool |
| `{"type": "none"}` | Tools are off for this turn |

This is worth knowing for the exercise specifically: when you force a
two-tool question, you're relying on `"auto"` letting Claude choose to call
both — you're not forcing it.

### 5. Parallel tool calls — the thing the exercise is actually testing

By default, Claude can request **multiple tool_use blocks in one
response** — that's exactly what the exercise (`get_weather` + `get_time` in
one turn) is exercising. The rule that trips people up:

> Handle *every* `tool_use` block before continuing, and send **all**
> results back in a **single** `user` message — not one message per result.

If you split parallel results across multiple messages, you don't get an
error — you just silently train the pattern of Claude making fewer parallel
calls over the conversation. This is why the loop in
`../02-react-loop/example_solution.py` collects `tool_results` into a list
first and appends it as one message, rather than appending after each tool
executes.

### 6. Error handling — tell Claude, don't crash

If a tool fails, don't raise and don't fabricate a fake success — return the
failure *as* the tool result with `is_error: true`:

```json
{"type": "tool_result", "tool_use_id": "toolu_01...", "content": "City not found", "is_error": true}
```

Claude sees this and typically adapts — retries differently, or tells the
user it couldn't complete the request. The course code doesn't do this yet
(the stub functions can't fail), but it's the pattern you'd add before this
touches anything real — and it's directly relevant to Course 2's "improper
output handling" module.

### 7. Extended thinking — the reasoning happening before the tool call

If you ran `example_solution.py` yourself, you likely noticed a block you
never asked for in `response.content`:

```
ThinkingBlock(signature='...', thinking='', type='thinking')
```

**Sonnet 5 (and every other current-generation model) thinks before acting
by default** — you don't opt in with a `thinking` parameter the way older
models required. What you *do* control is whether that reasoning is visible.
By default, `display` is `"omitted"` — the block is present but its
`thinking` field is an empty string. Thinking still happens and is still
billed either way; `display` only controls visibility, not occurrence or
cost.

To see the actual reasoning, add `thinking` explicitly to the request:

```python
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    tools=tools,
    messages=messages,
    thinking={"type": "adaptive", "display": "summarized"},
)
```

With that set, the same block now carries real text:

```
ThinkingBlock(thinking="I need to look up the weather for Austin, so I'll call the weather function.\n\n", type='thinking')
```

Two things worth knowing:

- **Preserve thinking blocks when you replay history.** Step 5 of the debug
  script appends `response.content` wholesale — including the `ThinkingBlock`
  — into the next request. That's correct and necessary: thinking blocks
  have to be sent back unchanged on the same model, not stripped out.
- **"Adaptive" means the model decides per request, not per conversation.**
  In the two-call round trip, request #1 (deciding whether/how to call a
  tool) produced a thinking block; request #2 (just synthesizing the final
  sentence from the tool result) didn't produce one at all. You can't assume
  every response will contain a thinking block — code defensively around its
  possible absence, the way this module's code already does by only
  special-casing `stop_reason == "tool_use"`, not thinking presence.

### Where this is *not* production-shape, on purpose

This module has you hand-write the request → execute → feed-back cycle
manually, because that's the whole pedagogical point (Module 2 builds the
loop from this). In real production code, Anthropic's SDKs ship a **Tool
Runner** that automates this exact loop — you'd normally reach for that
instead of hand-rolling it. Worth being able to say clearly: "I know how to
build this from scratch, and I know when *not* to — the tool runner covers
this in production, hand-rolling it is for control flow the runner doesn't
fit."

## Run the working example

```bash
python example_solution.py
```

Walk through the code and confirm you can explain why the full message
history — including the model's own prior `tool_use` block — has to be
resent on the second `messages.create` call. (The API is stateless per
request; nothing is remembered between calls unless you resend it.)

## Exercise

Open `exercise_starter.py`. Add a second tool, `get_time(timezone: str)`,
and ask a question that needs both tools in one turn — e.g. "What's the
weather and time in Austin?" Confirm the model requests both `tool_use`
blocks in a single response before you send any results back.

## What success looks like

You can point to the exact place in the code where each of these happens,
without re-reading it:

- the model *proposing* a call (`response.stop_reason == "tool_use"`)
- your code *executing* it (calling the Python function with `**block.input`)
- the result being *fed back* (`tool_result` appended to `messages`)

## Technical FAQ

**Does the model actually execute the tool?**
No. It returns a structured request (a `tool_use` block) — your application
code executes it. The model has no side effects of its own; nothing happens
unless your code runs it.

**Why do you have to resend the entire message history on every call?**
The Messages API is stateless per request — nothing is remembered
server-side between calls. Every follow-up request must carry the full
conversation, including Claude's own prior `tool_use` block.

**What tells the model when to use a tool versus just answering in text?**
The tool's `description` field — it's the only signal the model uses to
decide. It needs to state *when* to call it, not just what it does, or the
model under-triggers.

**How do you know, in code, that the model wants to call a tool?**
`response.stop_reason == "tool_use"`, and a `tool_use` content block is
present in `response.content` with the tool's `name` and parsed `input`.

**What happens if the model requests multiple tools at once?**
Parallel `tool_use` blocks can appear in a single response. You execute all
of them and return all `tool_result` blocks in one `user` message — splitting
them across messages silently discourages future parallel calls.

**How do you handle a tool call that fails?**
Return a `tool_result` with `is_error: true` and a clear message instead of
raising an exception. Claude sees the failure and typically adapts — retries
differently or tells the user it couldn't complete the request.

**What's the difference between `tool_choice: "auto"` and `"any"`?**
`"auto"` lets Claude decide whether to use a tool at all (the default);
`"any"` forces it to call at least one tool this turn.

**Would you hand-roll this request/execute/feed-back loop in production?**
Only when you need control a framework doesn't expose. Anthropic's SDKs ship
a Tool Runner that automates this exact cycle — that's the default choice;
hand-rolling it is for non-standard control flow, or for learning what's
underneath (which is the point of this module).

**Does the model "think" before deciding to call a tool?**
Yes, by default, on current-generation models — you don't have to opt in.
What's optional is *visibility*: reasoning is billed and happens either way,
but only shows up as readable text if you set
`thinking={"type": "adaptive", "display": "summarized"}`; otherwise it's
present but empty. It's also per-request, not per-conversation — a simple
follow-up turn may produce no thinking block at all.
