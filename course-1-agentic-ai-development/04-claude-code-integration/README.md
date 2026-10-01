# Module 4: Connect the MCP server to Claude via Claude Code

Claude Code discovers MCP servers through project- or user-level config, then
exposes each server's tools to the agent loop automatically — no custom
client-side integration code needed. Registration is a one-time `claude mcp
add` command that tells Claude Code how to launch your server process. Once
connected, `read_file` behaves exactly like a built-in tool: Claude decides
when to call it based on its description alone.

## Steps

```bash
# from the course-1 root, register the server you wrote in Module 3
claude mcp add codebase-reader -- python "$(pwd)/03-mcp-server/mcp_server.py"

# confirm it registered
claude mcp list

# in a Claude Code session, ask naturally — don't name the tool:
# "Read main.py from the codebase and summarize what it does."
```

## Exercise

Register the server, then in an actual Claude Code session ask it to read a
file from `sample_project/` using only natural language. Confirm it selects
`read_file` on its own from the tool's description — you didn't tell it
which tool to use.

## What success looks like

You can explain the difference between the loop you hand-built in
`02-react-loop/` (code you control end to end) and what Claude Code does
here (the same reason/act/observe loop, run by the harness on your behalf).
This distinction is a common principal-level technical question.

## The model is still doing all the reasoning — MCP just standardizes the plumbing

It's easy to read "Claude Code discovers MCP servers automatically" and
think some of the reasoning moved into the framework. It didn't — the
model is exactly as "in the loop" here as it was in `02-react-loop/`; MCP
only standardizes how tool definitions reach the model and how tool
results get sent back, instead of you hand-writing both.

Mapping this module directly onto `02-react-loop/exercise_starter.py`:

- **Tool specs → model**: instead of hand-writing the `TOOL_SPECS` list
  (`name`/`description`/`input_schema` dicts) and passing it to
  `client.messages.create(tools=TOOL_SPECS, ...)`, Claude Code discovers
  `read_file`/`list_files` from your running MCP server and builds that
  same `tools=[...]` list for you, then passes it into its own internal
  `messages.create` call.
- **Model decides to call a tool**: identical to your loop — the model
  looks at the prompt plus tool descriptions and returns a `tool_use`
  block, exactly like `response.content` in your code.
- **Act**: instead of your `TOOLS[block.name](**block.input)` dict
  lookup, the harness routes that `tool_use` block over the MCP
  connection to your server process, which runs `read_file(...)` and
  returns the string.
- **Observe**: the harness appends the result back into the conversation
  as a `tool_result` — the same message shape your loop builds by hand
  (`{"type": "tool_result", "tool_use_id": ..., "content": output}`).
- **Loop continues**: the harness calls the model again with that
  observation added, same as your `for step in range(max_steps)` guard —
  until the model responds with plain text and the loop ends.

So the model call count, the reason/act/observe cycle, and the message
structure are all the same as what you hand-built in Module 2. MCP
standardizes the *tool definitions and the transport for invoking them*
so any client (Claude Code, Claude Desktop, a custom agent) can use any
MCP server without bespoke integration code — it doesn't change who's
doing the reasoning.

## How tool selection actually happens: menu first, then the model picks

A natural question when a prompt like "Read main.py from the codebase and
summarize what it does" works correctly: does Claude Code inspect the
request first and route it to a matching tool, or does it hand everything
to the model and let the model decide? It's the latter, and it works the
same way at every layer of this course:

- **Every eligible tool is sent to the model on every turn** — native
  tools (`Read`, `Edit`, `Bash`, ...) plus every connected MCP server's
  tools, all assembled into one `tools=[...]` list, exactly like your own
  `TOOL_SPECS` being passed whole to `client.messages.create(...)` in
  `02-react-loop/`. There's no prompt-inspection step beforehand that
  narrows the list down to "this looks like a file-reading request."
- **The model alone decides whether to call a tool, and which one**,
  based purely on the tool descriptions/schemas and what it's trying to
  accomplish — the same decision your loop's `response.content` /
  `tool_use` handling reacts to.
- **The only thing decided client-side, before the model sees anything,
  is the *menu itself* — not the *selection*.** Is a given MCP server
  currently connected? Is it registered for this project? Are there
  permission settings excluding a tool? That filtering determines which
  tools are even offered; it never picks one *for* the model.
- **Why the model reaches for a tool at all on a generic-sounding request
  like "read main.py"**: the model has no memorized knowledge of *this*
  specific local file — "main.py" being a common filename doesn't help,
  because the request is about this file's actual current contents,
  which the model simply doesn't have. A tool whose description matches
  the need ("read a file from the codebase directory") is the only way
  to get that information, so the model calls it rather than guessing.

**A wrinkle worth knowing when you verify this exercise**: Claude Code
ships with its own built-in file-reading tool (`Read`), which can read
any file on disk — not just ones inside `sample_project/`. Once you
register `codebase-reader`, a prompt like "read main.py" can be satisfied
by *either* the native `Read` tool or your MCP server's `read_file`, and
which one fires isn't guaranteed by the prompt alone — it depends on how
the model weighs the two descriptions. Check the actual tool-call name in
the transcript rather than just checking that *a* file got read. To
remove the ambiguity entirely, ask something only `list_files` can do
(glob-matching across the tree) — the native `Read` tool has no
equivalent, so a call to it unambiguously proves the MCP server is wired
up correctly.

## Why this matters, and how it's used in practice

This is the payoff of the 02 → 03 → 04 progression: you built the ReAct
loop by hand (02) so you understand what "reason → act → observe" is at
the code level; you learned MCP (03) as the standardized way to expose a
tool instead of hand-writing tool specs bespoke to every client; Module 4
shows that Claude Code's own agent loop isn't fundamentally different
from the one you wrote — it's the same mechanism, run by the harness, and
it consumes tools through MCP instead of a hardcoded `TOOLS` dict.
Frameworks (Claude Code, LangChain agents, AutoGen, etc.) aren't magic —
they're this loop plus error handling, retries, and UI.

In practice, this is exactly the pattern real teams use to give AI tools
access to internal systems. Instead of writing custom integration code
for "Claude talks to our database" and separately "Cursor talks to our
database" and separately "our internal agent talks to our database," a
team writes **one MCP server** for that database/ticketing
system/CI pipeline/internal codebase, and any MCP-compatible client can
use it — often described as "USB-C for AI tools," turning an N×M
integration problem (N clients × M tools) into N+M. Companies stand up
internal MCP servers for things like Jira/Linear, internal wikis,
deployment systems, or (like this module's `codebase-reader` toy)
proprietary codebases, then every engineer's Claude Code, Claude Desktop,
or custom agent gets those capabilities for free just by registering the
server once — exactly what `claude mcp add` does above, just at company
scale instead of for one sample project.
