# Worksheet: AI supply chain vetting

Use the same agent from the earlier worksheets, or the Course 1 capstone
code review agent (which depends on the `anthropic` SDK and, if you wired
in MCP, an MCP server).

## 1. Inventory every third-party component

List everything in this agent's supply chain:

- The model provider(s) it calls.
- Every MCP server it connects to (name, what repo/maintainer it comes
  from, last time anyone reviewed its code).
- Every external data source it retrieves from.
- Any other third-party package with meaningful runtime behavior (not just
  a utility library).

## 2. Pick one new MCP server to vet

Imagine an engineer wants to add one new, real or hypothetical MCP server
to this agent's tool set. Walk through:

- Who reviews it before it's allowed, and what are they actually checking
  (read the source? run it sandboxed? check maintainer reputation?)?
- What does "pinned and signed" mean concretely for this dependency — a
  commit hash? a published, signed release? a vendored copy?
- Where does it run — same trust boundary as your production agent, or
  sandboxed with restricted filesystem/network access?

## 3. Blast radius if it's compromised

If that MCP server's maintainer account were compromised tomorrow and it
shipped a malicious update: given the permissions you scoped in Module 3's
worksheet, what's the worst it could actually do? If the answer is "quite a
lot," which of Module 3's tiering/scoping ideas would shrink that?

## 4. Say it out loud

Write a 3-sentence answer to: "An engineer wants to connect our agent to a
new third-party MCP server — what's your process?" Time yourself — aim for
under 45 seconds without notes.
