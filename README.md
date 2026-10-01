# Agentic AI Engineering — 3-Course Curriculum

Practical, code-first curriculum covering the full lifecycle of working with
LLM agents: build a working agent, understand how to secure one, and know how
to evaluate one in production. Each course is designed for 1–2 hours/day over
a week; total is roughly 30–40 hours.

| Course | Folder | Focus |
| --- | --- | --- |
| 1 | [`course-1-agentic-ai-development/`](course-1-agentic-ai-development/) | Build a working multi-step agent with tool use and MCP |
| 2 | [`course-2-ai-security-governance/`](course-2-ai-security-governance/) | OWASP LLM Top 10, prompt injection, least privilege, enterprise governance |
| 3 | [`course-3-agent-evaluation-observability/`](course-3-agent-evaluation-observability/) | Eval harnesses, regression testing, tracing, token economics |

## Layout convention

Every numbered module folder in Courses 1 and 3 follows the same shape:

- `README.md` — concept (short), what to build, what success looks like
- `example_solution.py` (or similarly named) — a **working, runnable** reference implementation
- `exercise_starter.py` — a stub with `TODO`s for the part you build yourself, where applicable

Course 2 is reading + written exercises (no code) — worksheets live in
`exercises/`, and the capstone is a fill-in-the-blank template.

## Setup (once)

There are two separate prerequisites — don't confuse a missing key for a
missing package, or vice versa:

1. **The `anthropic` package installed**, in an activated virtual
   environment.
2. **`ANTHROPIC_API_KEY` exported** in that same shell, so
   `anthropic.Anthropic()` picks it up automatically — no code changes
   needed.

```bash
cd course-1-agentic-ai-development   # or course-3-...
python3 -m venv agentic-course-env
source agentic-course-env/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...   # console.anthropic.com
```

`agentic-course-env` is just a name — call it whatever you like, but keep it
consistent across terminal sessions (re-run `source
agentic-course-env/bin/activate` each time you open a new shell; the
`pip install` only needs to happen once per environment). If you use a
different venv tool (`uv`, `conda`, `pyenv`), the two prerequisites above are
still the same — only the activation command changes.

Course 3's harness and observability examples run standalone (no API key
needed) using a mock agent function — swap in the real `react_loop` from
Course 1 once you've built it, per the comments in each file.

## Tools & frameworks used across the curriculum

| Tool / framework | Type | Used in | Purpose |
| --- | --- | --- | --- |
| **Anthropic Python SDK** (`anthropic`) | LLM API client | Course 1 (all modules); Course 3 (optional, wiring a real agent into the harness) | Every hand-built tool-use loop and ReAct loop calls `client.messages.create()` directly — no agent framework in between. |
| **MCP** (Model Context Protocol) / `mcp` (FastMCP) | Protocol + Python SDK | Course 1, Modules 3-4 | Standardizes tool discovery/exposure so any MCP-compliant client can call a server's tools without bespoke integration code. |
| **MCP Inspector** (`mcp dev`) | Dev tool | Course 1, Module 3 | Interactive UI for sanity-checking an MCP server's exposed tools before wiring it into a real client. |
| **Claude Code CLI** | Agent harness | Course 1, Module 4 | Shows the same reason/act/observe loop run by a production harness instead of hand-rolled code. |
| **PromptFoo** | Open-source eval CLI | Course 3, Module 3 (hands-on) | Config-driven (YAML) prompt/model testing — the CI-gate-shaped tool in the eval framework comparison. |
| **LangSmith** | Hosted tracing + eval platform | Course 3, Module 3 (compared, not run hands-on) | Tracing-first platform; eval built on the same data as production traces. |
| **Braintrust** | Hosted eval platform | Course 3, Module 3 (compared, not run hands-on) | Eval-first platform built around experiment diffing and non-engineer review workflows. |
| **Java (JDK/`javac`)** | Language/runtime | Course 1 capstone (concurrency fixtures) | Used to demonstrate the code-review agent working on a second language via regex-based static checks, not just Python's `ast` module. |
| **`jq`** | CLI utility | Course 3, Module 6 | Filters structured JSON trace logs by `trace_id` to reconstruct one agent run from a mixed log stream. |
| **Python 3.11+ standard library** | Language/runtime | All 3 courses | Every hand-rolled example deliberately favors stdlib (`ast`, `dataclasses`, `pathlib`, `re`, `uuid`, `json`) over third-party dependencies, so the mechanics stay visible rather than hidden behind a framework. |
| **OWASP Top 10 for LLM Applications** | Security standard (reference, not software) | Course 2, all modules | The industry-standard ranked list of LLM/agent security risks the whole course is structured around. |

Course 2 is deliberately tool-free — it's reading and judgment, not code, so
nothing in that course requires installing anything.
