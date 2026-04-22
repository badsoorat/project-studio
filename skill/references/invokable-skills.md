# Invokable skills

project-studio is a stand-alone orchestration skill. It does not list any other
skill as a hard boot dependency — no probe, no cache, no halt gate.

Specialist subagents the Chief of Staff spawns **do** load other skills by name
when the work warrants it. The two most consequential invokable families are
`graphify` (structural analysis) and the `gstack-team:*` plugin (methodology).
This doc explains when a spawned subagent should load each (solo or in
combination), how to express that in a Task-tool prompt, and what the subagent
is expected to return.

**v3.1 change:** The combo matrix below now enumerates `gstack-team:*` skills as
primary downstream-analysis partners for graphify. Before v3.1, these were
unqualified aliases (`review`, `cso`, `investigate`, etc.). Per the namespace
migration, specialists must invoke the fully qualified `gstack-team:` form so
the correct implementation loads. See `references/skill-catalog.md` for the
full catalog.

## Why per-subagent instead of pre-build

Earlier versions of project-studio required CoS to run `graphify .` up front
and cache a report the whole team read. That broke on three edges:

1. Repos without committed code (new scaffolds, docs-only repos) had nothing
   to graph — the pre-build step either failed or produced noise.
2. Multi-module parents tried to graph the whole tree at once, which was
   expensive and mixed sibling module internals into one blob.
3. The cached report drifted. By the time a Friday retro read it, the graph
   reflected Monday's code.

Invokable loading moves the cost to the moment and the scope where it pays:
one subagent, one specific question, fresh graph every call.

## When to load graphify

Load graphify in a spawned subagent whenever **all** of the following are
true:

- The scale-mode is `standard` or `heavy` (skip on `light`).
- The module's type is code-bearing — engineering, platform, data-systems,
  ML, infra, devops, browser-QA, release-readiness, security-audit. Not
  applicable to pure research, design, or marketing modules unless they are
  reading a code artifact.
- The specialist's answer genuinely depends on **structure across files**:
  call graphs, dependency clusters, blast radius, architectural drift, dead
  code, cluster health. A single-file reading task does not need graphify.
- The repo has enough code to graph (roughly: `git ls-files | wc -l` > 20,
  or a `src/`-style tree is present).

If any of those is false, skip graphify and spawn the specialist with its
normal skill loadout.

## When to load a gstack-team:* methodology skill

Load a `gstack-team:*` skill in a spawned subagent whenever the turn has a
**methodology shape** that matches a skill's purpose:

| Turn shape | Skill |
|---|---|
| Pre-merge / pre-land code review with Scope Drift Detection | `gstack-team:review` |
| Security audit — OWASP + STRIDE | `gstack-team:cso` |
| Root-cause investigation of a bug, error, or regression | `gstack-team:investigate` |
| Live QA of a deployed site (navigation, responsive, bug evidence) | `gstack-team:qa` |
| Visual design audit on a deployed site (hierarchy, AI-slop) | `gstack-team:design-review` |
| Plan-level strategy critique | `gstack-team:plan-ceo-review` |
| Plan-level engineering critique | `gstack-team:plan-eng-review` |
| Plan-level design critique | `gstack-team:plan-design-review` |
| Plan-level DX critique | `gstack-team:plan-devex-review` |
| Teaching mode — explain without modifying | `gstack-team:learn` |
| End-to-end feature planning | `gstack-team:autoplan` |
| YC-style product interrogation | `gstack-team:office-hours` |
| Milestone retrospective | `gstack-team:retro` |
| Raise rigor for high-stakes changes | `gstack-team:careful` |
| Brand / design-system consultation | `gstack-team:design-consultation` |

These are **methodology** skills. They frame how the specialist thinks, not
what the specialist reads. A `gstack-team:review` spawn still needs to read
the code under review — typically via `graphify` (for structural evidence)
plus direct file reads (for line-level analysis).

## Solo vs combo loadouts

### Solo — graphify only

Use when the question is purely structural: *"Map this codebase and tell me
where the complexity clusters are"*, *"What modules does `auth/` transitively
depend on?"*, *"Generate a dependency audit for the platform module."*

The subagent's only job is to run graphify against a scoped path, read the
resulting HTML/JSON/audit report, and return a distilled slice.

### Solo — gstack-team:* methodology only

Use when the turn is **not code-bearing** but has a methodology shape:
- A plan-critique lens on a design plan (no codebase involved) → `gstack-team:plan-design-review` solo.
- A retro on a sprint of marketing / research work → `gstack-team:retro` solo.
- A teaching-mode explanation of a concept → `gstack-team:learn` solo.
- A YC office-hours interrogation of a product idea → `gstack-team:office-hours` solo.

### Combo — graphify + gstack-team:* + (optionally) a domain skill

Use when graphify's structural output is evidence that a `gstack-team:*`
methodology skill will turn into a decision. Typical pairings:

| Question the CoS is answering | Combo loadout |
|---|---|
| Is this branch ready to land? | `graphify` + `gstack-team:review` |
| Is this codebase secure? | `graphify` + `gstack-team:cso` |
| Why is this test / endpoint / feature broken? | `graphify` + `gstack-team:investigate` |
| Does the deployed app pass live QA? | `gstack-team:qa` + `gstack-team:browse` (no graphify — QA is behavioural) |
| Does the deployed UI hold up visually? | `gstack-team:design-review` + `gstack-team:browse` (no graphify — audit is visual) |
| Is this module's architecture coherent enough to ship? | `graphify` + `clean-architecture` + `gstack-team:review` |
| Where are the performance hotspots we should fix first? | `graphify` + `postgresql-performance-expert` + `system-design` |
| Can this module absorb the new billing feature without a rewrite? | `graphify` + `saas-architecture-deep-dive` + `software-design-philosophy` |
| Is this integration layer fragile — retry/idempotency holes? | `graphify` + `integration-patterns-mastery` + `release-it` |
| What refactor will most r