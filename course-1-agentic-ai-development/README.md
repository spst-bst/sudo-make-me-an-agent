# Course 1: Hands-On Agentic AI Development

Build a working multi-step AI agent with tool use and MCP integration — real
code you write and run yourself. By the end you'll have a capstone "code
review agent" and be able to explain every line of the loop underneath it.

## Prerequisites

- Python 3.11+, `pip install -r requirements.txt`
- `ANTHROPIC_API_KEY` set (console.anthropic.com)
- Claude Code CLI installed (`claude --version`) — needed for Module 4

## Weekly schedule

| Day | Hours | Focus | Folder |
| --- | --- | --- | --- |
| 1 | 1.5h | How tool use actually works | `01-tool-use/` |
| 2 | 2h | Build a ReAct loop from scratch | `02-react-loop/` |
| 3 | 1.5h | Stand up an MCP server | `03-mcp-server/` |
| 4 | 1h | Wire the MCP server into Claude Code | `04-claude-code-integration/` |
| 5 | 1.5h | Chain 3 tools in one agent | `05-multi-tool-chain/` |
| 6–7 | 2h + 2h | Build and polish the capstone | `06-capstone-code-review-agent/` |

## Modules

1. **[Tool use / function calling](01-tool-use/)** — how the model requests a
   tool call and how you feed the result back.
2. **[ReAct loop from scratch](02-react-loop/)** — reason → act → observe →
   repeat, hand-built so you can debug any agent framework later.
3. **[MCP server basics](03-mcp-server/)** — expose a `read_file` tool over
   MCP using FastMCP.
4. **[Connect to Claude Code](04-claude-code-integration/)** — register the
   server, watch Claude select the tool from its description alone.
5. **[Multi-tool chain](05-multi-tool-chain/)** — 3 tools with a real
   dependency (list → read → analyze), same loop, no hardcoded ordering.
6. **[Capstone: code review agent](06-capstone-code-review-agent/)** — reads
   a Python file, finds issues, suggests fixes, writes a report.

`sample_project/` is the shared fixture codebase every module reads from —
don't edit it except to add more test cases.

## Technical FAQ

1. "Walk me through what happens, step by step, when an LLM agent decides
   to call a tool." — the model returns `stop_reason: "tool_use"` with a
   `tool_use` block (name + parsed JSON input); it never executes anything
   itself. Your code runs the real function, appends the assistant's full
   response plus a `tool_result` block (linked by `tool_use_id`) to the
   message history, and resends the whole history — the API is stateless —
   so the model can read the result and decide whether to call another tool
   or answer in plain text.
2. "How is MCP different from writing custom tool-calling code yourself?"
   — hand-written tool-calling code is bespoke per project; MCP standardizes
   tool discovery and the call protocol so a server declares its tools once
   and any MCP-compliant client can use them unchanged. The model's
   reasoning doesn't change — MCP only standardizes the plumbing.
3. "How do you prevent an agent from looping forever or taking unbounded
   actions?" — a hard `max_steps` guard that fails loudly instead of
   looping silently, tool errors fed back to the model as observations
   instead of crashing so it can self-correct, and scoping each tool to the
   minimum permission it needs so even a runaway loop has a bounded blast
   radius.
