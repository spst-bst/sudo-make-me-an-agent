# AI Governance Framework — Example, large engineering organization

A filled reference to check your own TEMPLATE.md against — not a model
answer to copy verbatim. Adjust specifics to whatever organization you're
actually describing.

## Purpose & scope

- Covers: all production use of LLMs/agents that touch company data, customer
  data, or take automated actions on either.
- Does not cover: personal experimentation in an isolated sandbox with no
  access to production data or systems.

## Model & tool registry

- Approved models/providers: a short list vetted for data-handling terms and
  security posture; new models require a review before any team can adopt
  them for production traffic.
- Approved MCP servers process: security review + code read + sandboxed test
  run before an MCP server is added to the internal registry; unregistered
  servers are blocked in CI and infra policy, not just discouraged.
- Review/renewal cadence: quarterly for Tier 3 (external-effect) tools,
  annually for Tier 1 (read-only).

## Data classification matrix

| Data tier | May be used with |
| --- | --- |
| Public | Any approved model, no restrictions |
| Internal | Approved models only, standard logging |
| Confidential | Approved models with a signed DPA, enhanced logging, no third-party MCP tools |
| Restricted | On-prem / VPC-isolated models only, no external network egress from the tool, dual sign-off for any related agent going to production |

## Autonomy tiers

| Tier | Definition | Example actions | Approval required |
| --- | --- | --- | --- |
| 1 | Read-only, reversible, no external effect | Read a file, query a metric, search docs | None — auto-execute, logged |
| 2 | Internal write, reversible | Update a ticket, write to an internal wiki | Logged, reviewed weekly by the owning team |
| 3 | External effect, irreversible, or restricted data | Send email, deploy, pay, delete, touch restricted data | Human approval per action before execution |

## Required controls

- Audit logging standard: every prompt, tool call (with arguments), tool
  result, and model response logged with a correlation/trace ID; same
  retention and access-control bar as existing HIPAA/ISO 27001-scoped
  systems.
- Retention period: matches the underlying data's own classification-driven
  retention policy, minimum 1 year for Tier 2/3 actions.
- Red-team / eval cadence: golden-suite regression pass (Course 3) plus a
  prompt-injection test pass required before any Tier 2/3 agent's first
  production promotion, and after any model version upgrade.

## Incident response

- Who's paged: the owning team's on-call, plus security on-call for any
  Tier 3 incident or suspected data exposure.
- How an agent is disabled: a kill switch per registered agent (registry
  entry flips to disabled, blocking its credentials at the identity layer)
  — not a code deploy.
- Post-incident review requirement: blameless postmortem within 5 business
  days for any Tier 3 incident, findings feed back into the registry's
  review checklist.

## Ownership

- Registry owner: central AI platform/security team.
- Exception approver: platform team lead + security lead, joint sign-off.
- Escalation path: owning team → platform team → security → CISO org, same
  ladder as existing infra incident escalation.

---

**If asked "what's the first control you'd cut under budget pressure?"** —
Relax the registry review cadence for Tier 1 (read-only) tools first — from
quarterly to annual. Audit logging and Tier 3 human-approval gates stay
non-negotiable regardless of budget, because they're what makes an incident
containable instead of catastrophic.
