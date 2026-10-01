# Worksheet: Prompt injection threat model

Pick one agent from your own work history (or the Course 1 capstone code
review agent) and fill this in. Aim for specific, not generic, answers.

## 1. Describe the agent

- What does it do, in one sentence?
- What tools does it have, and what can each one actually *do* (read,
  write, send, delete, pay)?
- What untrusted content does it read as part of doing its job (emails,
  web pages, tickets, file contents, another user's data)?

## 2. Find the injection surface

For each untrusted input source you listed above:

- Could it contain attacker-controlled text? (Yes if any external party —
  customer, sender, web page author — can influence the content.)
- If the model followed an instruction hidden in that content, what's the
  worst tool call it could trigger?

## 3. Design the defense

For your worst-case scenario above:

- **Structural defense** — how would you make tool output unable to be
  read as instructions (delimiting, structured fields, a separate
  "untrusted content" message role)?
- **Permission defense** — does the triggered tool call need to be
  possible at all without a human in the loop? Could it be scoped away
  entirely?
- **Detection defense** — would a prompt-injection classifier or an
  anomaly check on tool call patterns have caught this before it executed?

## 4. Say it out loud

Write a 3-sentence answer to: "Walk me through a prompt injection attack on
this specific agent, and how you'd stop it." Time yourself — aim for under
45 seconds without notes.
