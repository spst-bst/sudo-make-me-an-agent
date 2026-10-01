# Module 3: Evaluation frameworks overview

**LangSmith** — tracing, eval, and a prompt playground, tightly integrated
with LangChain but usable standalone; strongest when you're already tracing
production calls and want eval built on the same data.

**Braintrust** — an eval-first platform built around scoring functions and
regression tracking, strong when non-engineers (PMs, domain experts) need to
review and label outputs collaboratively.

**PromptFoo** — open-source, config-driven (YAML), no vendor lock-in; the
natural choice for CI-gated regression tests on prompt or model changes,
since it runs as a CLI step.

## Try it

```bash
npm install -g promptfoo
cd 03-frameworks-overview
export ANTHROPIC_API_KEY=sk-ant-...
promptfoo eval -c promptfooconfig.yaml
```

Both test cases should `[PASS]`. Worth a close look at the second one's
assertion (`contains: "except"`) — it would still pass even if the model had
just echoed the input code back without analyzing it, since the source
itself contains the literal string `except:`. A tighter assertion (e.g.
`contains: "bare except"`, or an `llm-rubric` check) only passes if the
model actually diagnosed the problem. Same trap applies to any regression
suite built in Module 5 — a weak assertion will keep reporting "passing"
long after the thing it was supposed to catch has stopped being caught.

## Assertion syntax: `type` and `value`

Every assertion is two parts — `type` (which check to run) and `value` (the
argument to it) — the same decomposition as a JUnit assertion: `type` is the
equivalent of picking `assertEquals` vs `assertTrue` vs a Hamcrest matcher
like `containsString(...)`, and `value` is the expected argument passed to
it. Common `type`s:

- `equals` / `icontains` — exact or case-insensitive match, JUnit-style.
- `contains` / `contains-any` — substring checks (what's used above).
- `regex` — pattern matching.
- `javascript` / `python` — arbitrary code returning true/false, for logic
  too complex for a canned assertion type (closest to a custom matcher).
- `cost` / `latency` — threshold checks on the API call's price/speed,
  something a traditional unit-test framework has no concept of at all.
- **`llm-rubric`** — no JUnit equivalent. `value` is a natural-language
  grading criterion (e.g. "the response correctly identifies the exception
  is silently swallowed"), and PromptFoo sends the agent's output plus that
  rubric to a separate LLM call to judge pass/fail — a model grading
  another model's output, which a deterministic assertion simply can't do.

The deeper difference from JUnit isn't the syntax, it's what's on the other
side of the assertion: JUnit checks deterministic code, so passing once
means passing always. Every assertion type here — even a plain `contains`
— checks a non-deterministic model, so passing once tells you nothing about
passing reliably. That's why Module 4's harness insists on repeated runs
and a pass *rate*, instead of a single green check the way JUnit reports
results.

## Each tool in more depth

**LangSmith** — tracing first, eval second. Every agent/tool/LLM call is
logged as a nested trace tree (inputs, outputs, latency, tokens) — the same
idea as Module 6's trace-ID-per-request, as a hosted product instead of
something hand-rolled. Datasets and evaluators get built *from* those
traces, so production failures convert directly into regression test cases
without being rewritten from scratch. Best fit: teams who want eval running
on the same pipe as their production observability. Trade-off: heavier to
adopt outside the LangChain ecosystem; cost scales with trace volume.

**Braintrust** — eval-first, with tracing as a secondary feature. Every run
against a dataset becomes a named "experiment," and the UI is built around
diffing experiments against each other — the closest thing to `git diff`
for a prompt or model change. Ships **Autoevals**, an open-source library of
ready-made scorers (factuality, moderation, semantic similarity) so you're
not writing every scoring function from scratch. Its defining feature is a
human-review UI a non-engineer can use directly — a PM or domain expert can
label outputs "good/bad" without touching code or YAML, a materially
different audience than PromptFoo's engineer-only CLI. Best fit: orgs where
non-engineers need to be in the loop judging output quality. Trade-off: less
of a capture-everything-by-default observability layer than LangSmith.

**PromptFoo** — a test matrix: one YAML file defines prompts × providers ×
test cases, and it runs the full cross-product, which is exactly the
side-by-side comparison table format you see in the CLI output above.
Assertion types range from the blunt `contains` check (see above) to
`llm-rubric` (model-graded scoring) and arbitrary JS functions. It also
ships a **red-teaming mode** — automated jailbreak/prompt-injection
probing — a direct, practical way to automate Course 2's prompt-injection
worksheet against a real agent instead of doing it by hand. Best fit:
CI-gated regression checks (Module 5's exact use case) with zero infra to
stand up. Trade-off: it's a test runner, not a continuous production
dashboard of live traffic.

**The real dividing line** — all three can technically run-prompts/score/
compare; what differs is the primary artifact and primary user:

| Tool | Primary artifact | Primary user |
| --- | --- | --- |
| LangSmith | A production trace | An engineer debugging live behavior |
| Braintrust | An experiment diff | A reviewer (engineer or non-engineer) judging quality |
| PromptFoo | A CI pass/fail | A pipeline, not a person |

That also explains the course sequence: Module 4 has you hand-build the
thing PromptFoo automates, and Module 6 hand-builds the thing LangSmith
automates — in both cases, so you understand what you'd be buying before
you buy it.

## Scaling beyond a toy example

`promptfooconfig.yaml`'s test cases are one-line functions pasted inline —
fine for teaching the YAML shape, not representative of testing against a
real codebase. Three things change at real scale:

- **Inline strings → file references.** PromptFoo supports `vars` pointing
  at external files (`code: file://path/to/real_file.py`) instead of
  pasting source directly in the YAML, so at least a single real file stays
  manageable without turning the config into a wall of text.
- **One prompt can't hold a whole codebase.** Context limits aside, dumping
  a multi-file repo into one `"review this: {{code}}"` prompt is exactly
  the brute-force approach the Course 1 capstone avoids by using tools
  (`list_files`/`read_file`/`find_issues`) instead of one giant prompt.
  PromptFoo's `providers` field can point at a custom script/function
  instead of a bare model completion — so a real test would wire in the
  actual Course 1 `react_loop` + capstone tool set as the provider, feed it
  a prompt like *"review sample_project for issues,"* and let the agent
  decide what to read, same as running it directly. PromptFoo becomes a
  harness wrapped *around* the real agent, not a replacement for it.
- **The assertion style has to scale too.** `contains: "ZeroDivisionError"`
  works for one expected issue in one tiny function. A real multi-file
  review producing a dozen issues needs either an `llm-rubric` assertion
  (model-graded: does this report identify issues X/Y/Z and avoid false
  positives on W) or a structured diff against a golden/expected issue
  list — scoring recall/precision across a whole report, not matching one
  keyword.

## FAQ — explained in plain terms

"We don't hand-inspect every model or prompt update — we run the agent's
test suite through an eval framework in CI, the same way a unit test suite
gates a code change. PromptFoo is the lightweight option for that CI gate;
LangSmith or Braintrust earn their keep when you also need tracing or
non-engineer review built in."
