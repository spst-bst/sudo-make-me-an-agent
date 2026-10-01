# Worksheet: Mapping an agent against the OWASP LLM Top 10

Pick one agent from your own work history (or the Course 1 capstone code
review agent) and fill this in. Aim for specific, not generic, answers.

## 1. Map every threat

For each of the 10 threats, mark **N/A**, **Low** (theoretically possible,
low impact or already mitigated by something else), or **Needs a control**
(a real gap today):

| Threat | N/A / Low / Needs a control | One sentence why |
| --- | --- | --- |
| LLM01 Prompt Injection | | |
| LLM02 Sensitive Information Disclosure | | |
| LLM03 Supply Chain | | |
| LLM04 Data and Model Poisoning | | |
| LLM05 Improper Output Handling | | |
| LLM06 Excessive Agency | | |
| LLM07 System Prompt Leakage | | |
| LLM08 Vector and Embedding Weaknesses | | |
| LLM09 Misinformation | | |
| LLM10 Unbounded Consumption | | |

## 2. Prioritize

List your top 3 "Needs a control" rows in order. For each: what's the one
sentence that justifies *why this one, before the others*? (Think in terms
of likelihood × blast radius, not alphabetical order or gut feel.)

## 3. Design one defense

Pick whichever of your top 3 is **not** prompt injection, excessive agency,
or supply chain (those get their own modules) — design one concrete,
specific defense for it. Not "add monitoring" — name the actual control,
who owns it, and what would have to be true for it to fail.

## 4. Say it out loud

Write a 3-sentence answer to: "Why prioritize threats instead of trying to
fix all ten equally?" Time yourself — aim for under 45 seconds without
notes.
