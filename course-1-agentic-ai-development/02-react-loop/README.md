# Module 2: Building a ReAct agent loop from scratch

ReAct interleaves reasoning ("Thought") with tool calls ("Action") and their
results ("Observation"), looping until the model has enough information to
answer. Building this loop by hand — instead of calling a framework's
`.run()` — is what lets you debug or extend any agent framework you'll meet
on the job, since they're all this same loop with more error handling around
it. The loop ends either when the model replies with plain text (no more
tool calls) or a max-iteration guard fires, which is itself a safety control
worth being able to name clearly.

## Run the working example

```bash
python example_solution.py
```

Watch the printed `[step N] action=... observation=...` lines — that's the
loop's reasoning made visible.

## Exercise

Open `exercise_starter.py`:

1. Print the model's reasoning text (the non-`tool_use` content blocks
   alongside each `tool_use` block) so you can see the "Thought" step
   explicitly, not just the action.
2. Set `max_steps=1` and confirm the guard fires cleanly on a question that
   needs two tools.

## What success looks like

You can point to the exact lines that implement each part of the loop:

- **reason** — the `client.messages.create(...)` call
- **act** — `TOOLS[block.name](**block.input)`
- **observe** — appending the `tool_result` back into `messages`
