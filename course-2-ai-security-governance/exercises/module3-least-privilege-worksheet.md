# Worksheet: Agent permissions and least privilege

Use the same agent from Module 2's worksheet, or the Course 1 capstone code
review agent.

## 1. Inventory every tool the agent has

| Tool | What it can do | Blast radius if misused |
| --- | --- | --- |
| e.g. `read_file` | Read any file under the codebase root | Low — read-only, path-traversal guarded |
| e.g. `send_email` | Send email as the service account | High — irreversible, external effect |

Fill in every tool your agent (or the capstone agent) actually has.

## 2. Assign an autonomy tier to each

- **Tier 1 (auto-execute):** read-only, reversible, no external effect
- **Tier 2 (logged + reviewed after the fact):** internal write, reversible
- **Tier 3 (human approval required before execution):** external effect,
  irreversible, or touches restricted-classification data

Which tier is each tool in? Is any tool in the wrong tier today?

## 3. Scope the credential, not just the tool

For each Tier 2/3 tool: what's the narrowest credential that still lets it
do its job? (e.g. a DB tool needs a read-only role unless a specific task
requires write — write should be a *different* tool with its own gate, not
a flag on the same one.)

## 4. Say it out loud

Write a 3-sentence answer to: "How would you redesign this agent's
permissions if you found out today it had standing write access it didn't
need?" Time yourself — aim for under 45 seconds without notes.
