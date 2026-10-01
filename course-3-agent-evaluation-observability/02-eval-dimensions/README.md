# Module 2: Evaluation dimensions

Five dimensions matter, and correctness is only one of them: **correctness**
(did it get the right answer/outcome), **safety** (did it avoid disallowed
or destructive actions), **consistency** (does it agree with itself across
repeated runs on the same input), **latency** (is it fast enough for the
interaction pattern it's used in), and **cost** (tokens and dollars per
run). A demo only needs correctness; a production agent needs all five
measured continuously.

## Run it

```bash
python eval_result.py
```

Notice candidate 2 has *higher* correctness than candidate 1 but fails the
production-ready bar anyway — safety and consistency gate it. That's the
point of measuring on 5 axes instead of 1.

## Real-world stakes per dimension

- **Correctness** — did the Course 1 capstone code review agent actually
  catch the bare `except:` and the lock-order deadlock, or miss them /
  hallucinate issues that aren't there. The only dimension a one-off demo
  run can measure at all.
- **Safety** — independent of whether the *answer* was right: a support
  agent with DB write access (Course 2 Module 3's example) that occasionally
  runs an unintended `DROP TABLE`. `safety=0.99` means 1 in 100 runs took a
  disallowed action — at 50,000 tickets/day that's ~500 violations daily,
  which is why production gates default to `min_safety=1.0`: "almost always
  safe" isn't a passing grade for anything with real side effects.
- **Consistency** — does it agree with itself on the *identical* input
  across repeated runs (this is Module 1's non-determinism point, measured
  directly). A triage agent classifying the same ticket "billing" on one run
  and "technical" on a re-run is invisible in a single demo but breaks any
  downstream routing/automation at scale — 80% self-agreement means roughly
  1 in 5 tickets gets handled inconsistently depending on which run happened
  to execute.
- **Latency** — fast enough for *its* interaction pattern, not fast in the
  abstract. A customer-facing chat agent needs sub-2-3-second responses; an
  async CI code-review job can take 30+ seconds with nobody noticing. The
  threshold has to match the use case, not a fixed number.
- **Cost** — only becomes real money at volume. $0.04/run is nothing once;
  at 50,000 calls/day that's $2,000/day — and Module 7 (token economics)
  shows the actual risk multiplier is usually context bloat from resending
  tool-call history every loop iteration, not the sticker price per token.

**The actual lesson:** a reviewer looking only at "candidate 2 is 2% more
correct and cheaper" would ship the worse agent. The 5-axis gate exists to
catch exactly that — a correctness gain is worthless if it's bought with a
safety or consistency regression that doesn't surface until the agent is
running unattended at scale.

## FAQ — explained in plain terms

"Correctness alone tells you the agent worked once. Safety, consistency,
latency, and cost together tell you whether it's fit to run unattended at
scale — that's the actual difference between a demo and something we'd run
unattended across the whole org."
