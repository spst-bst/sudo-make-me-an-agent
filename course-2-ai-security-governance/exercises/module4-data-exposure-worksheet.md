# Worksheet: Data exposure risk mapping

Use the same agent from Module 2/3's worksheets, or the Course 1 capstone
code review agent.

## 1. Trace every data flow

List every place data enters or is stored during this agent's operation:

- What goes into the prompt/context window on a typical task?
- What gets written to logs or traces (full tool arguments? full model
  output? both)?
- If it uses RAG — is the retrieval index shared across more than one
  customer/tenant/team?

## 2. Classify each source

For every data source you listed above, assign a tier: **Public**,
**Internal**, **Confidential**, or **Restricted**. Flag any source where
you're not actually sure what tier it should be — that uncertainty is
itself a finding.

| Data source | Tier | Where it enters (prompt / log / RAG index) |
| --- | --- | --- |
| | | |

## 3. Cross-tenant check

If more than one tenant/customer/team's data touches this agent: could a
cleverly phrased query from one tenant retrieve another tenant's data?
Where exactly would that isolation be enforced — the prompt, the retrieval
query, or the index itself? (If the answer is "the prompt," that's a gap,
not a control.)

## 4. Design the defense

For your highest-tier data source: where in the pipeline would
redaction/DLP actually run (ingestion? pre-prompt? pre-log? output?), and
why there specifically rather than anywhere else?

## 5. Say it out loud

Write a 3-sentence answer to: "Why can't you just redact sensitive data
after it's already in the vector store?" Time yourself — aim for under 45
seconds without notes.
