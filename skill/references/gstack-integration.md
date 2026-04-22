# gstack-team integration

Project Studio takes a direct runtime dependency on the `gstack-team` plugin. This is Model A (runtime wiring) — not Model B (pattern absorption). When a Project Studio specialist or CoS invokes a `gstack-team:*` skill, it runs the actual skill from the installed plugin; it does not recreate the behaviour internally. If the plugin is absent, the capability degrades gracefully per the connector severity gate (Invariant #21).

This doc is the canonical mapping: which gstack-team skill backs which Project Studio capability, when each runs, and how scope is bounded in parent/module sessions.

## Why direct invocation, not absorption

gstack-team is maintained. Its skills evolve. If Project Studio copied the prompts inline, every upstream change would require a sync. Direct invocation keeps Project Studio lean and lets the plugin own the quality bar for the methodology it contributes. The tradeoff is a hard dependency: without gstack-team installed at critical severity, Project Studio runs in a reduced-capability mode. See `references/connectors.md` §degraded-mode.

## Namespace

All references to gstack-team skills use the fully qualified form `gstack-team:<skill>`. No bare references. This is a hard-cut rule — see Invariant #28's cousin rule in `references/skill-catalog.md`.

## Mapping — capability to skill

| Project Studio capability | Backed by | Invoked by | When it runs |
|---|---|---|---|
| Strategy lens on a plan | `gstack-team:plan-ceo-review` | CoS (orchestrator) | Before implementation starts — Invariant #20 |
| Engineering lens on a plan | `gstack-team:plan-eng-review` | CoS | Before implementation starts — Invariant #20 |
| Design lens on a plan | `gstack-team:plan-design-review` | CoS | Before implementation starts — Invariant #20 |
| Developer-experience lens on a plan | `gstack-team:plan-devex-review` | CoS | Before implementation starts — Invariant #20 |
| End-to-end feature planning | `gstack-team:autoplan` | CoS | When user hands over a feature idea for planning; replaces ad-hoc brief-to-plan flow |
| Scoping / idea interrogation | `gstack-team:office-hours` | CoS, optionally a Product specialist | When user is weighing whether to build something before a plan exists |
| Design-system consultation | `gstack-team:design-consultation` | Design specialist | When the module needs a design system spec, not a screen mockup |
| Code review | `gstack-team:review` | Engineering specialist (spawned) | Before merge, against a branch or diff |
| Security audit | `gstack-team:cso` | Security specialist (spawned) | Before production release; also at milestone #0 for a security-sensitive module |
| Root-cause investigation | `gstack-team:investigate` | Engineering specialist (spawned) | When a bug report or error trace arrives |
| Browser QA on deployed URL | `gstack-team:qa` | QA specialist (spawned) | Against staging and production URLs before milestone sign-off |
| Visual design review on deployed site | `gstack-team:design-review` | Design specialist (spawned) | After a design-affecting deploy reaches a live URL |
| Accessibility review on designs or pages | `gstack-team:design:accessibility-review` (from `design` plugin pairing if installed; otherwise a companion skill) | Design specialist | Before handoff and before public release |
| Browsing a page | `gstack-team:browse` | Any specialist | When evidence requires reading a public page or doc |
| Weekly/milestone retrospective | `gstack-team:retro` | CoS + the whole team | At every milestone — Invariant #22 |
| Careful-mode escalation | `gstack-team:careful` | CoS | Default critique stance; escalated explicitly for production-critical changes |
| Context snapshot at session end | `gstack-team:context-save` | CoS | On session wind-down, at checkpoint, and before a risky action |
| Context restore at session start | `gstack-team:context-restore` | CoS | First step of boot when `.cowork/context/` is present |
| Freeze paths | `gstack-team:freeze` | CoS | User-initiated; records paths into `.cowork/freeze.json` |
| Enforce frozen paths before writes | `gstack-team:guard` | CoS, before every Write/Edit | Implicit on every write when `.cowork/freeze.json` is non-empty |
| Unfreeze paths | `gstack-team:unfreeze` | CoS | User-initiated |
| Teach-first walkthrough of a codebase | `gstack-team:learn` | Engineering specialist | When user wants to understand, not change, a system |
| Pre-merge ship sequence | `gstack-team:ship` | Engineering specialist (spawned) | On feature branch when CoS proposes to merge |
| Production deploy (single module) | `gstack-team:land-and-deploy` | Engineering specialist (spawned) | After `ship` opens a PR and user approves merge |
| Canary / progressive rollout | `gstack-team:canary` | Engineering specialist (spawned) | For risky production changes — Invariant #27 constrains scope |
| PDF export of any deliverable | `gstack-team:make-pdf` | CoS | Default for user-facing deliverables — Invariant #24 |

The Chief of Staff does not load these skills itself for any action that isn't orchestration. Skill loading happens in the spawned specialist (per Invariant #5: lean context). CoS's job is to name which skill the spawn must read and why.

## §plan-critique — exact mapping

Tier-1 plan-critique runs before implementation starts. The four lenses and when each one fires:

1. **`gstack-team:plan-ceo-review`** — strategy/scope challenge. Runs first. If it returns a scope-change recommendation, the plan is rewritten before the other three lenses see it.
2. **`gstack-team:plan-eng-review`** — architecture and implementation soundness. Runs second. If it flags a technical infeasibility, the plan is rewritten before design and devex see it.
3. **`gstack-team:plan-design-review`** — interaction, UX, and design-slop detection.
4. **`gstack-team:plan-devex-review`** — API/SDK/CLI ergonomics. May be skipped if the module exposes no developer-facing surface.

Lenses 3 and 4 can run in parallel after 1 and 2 clear.

**Parent-scope plans.** A plan that affects multiple modules (e.g., a shared schema change, a parent roadmap milestone) runs all four lenses at the parent first. Then each affected module's session runs just the engineering lens locally against its slice to catch module-specific implementation issues. This is a two-layer critique: parent for coherence, module for locality.

**Light-scale condensed pass.** On light scale, lenses 1-4 collapse into one Task-tool spawn that enumerates all four skills in order and asks for a single-shot verdict. This is faster, less thorough, and explicitly NOT a skip — see Invariant #8.

## §pdf-default — what the default looks like in practice

When CoS proposes a user-facing deliverable, the proposal block names the format:

> Proposal: Produce the Q2 roadmap as `project-studio/exports/2026-04-22-q2-roadmap.pdf` via `gstack-team:make-pdf`, sourced from `project-studio/project/roadmap.md`.
>
> Export format: PDF via make-pdf. Override with "markdown only" to skip the PDF render.

The user answers yes or override. On yes, CoS writes the markdown source (if not already present), then invokes `gstack-team:make-pdf` with that source as input. The PDF lands in `project-studio/exports/<YYYY-MM-DD>-<slug>.pdf`. On override, CoS writes the markdown only and skips the PDF step.

Internal files (log entries, register updates, inbox messages, bus routing, seed yaml) never go through this flow. They stay markdown-only.

## §freeze-scope — parent/module semantics

`.cowork/freeze.json` files live at two levels:

- **Parent freeze**: `~/parent/.cowork/freeze.json`. Registered via a parent-session run of `gstack-team:freeze`. Blocks writes to parent files (`.project-studio/`, `shared/`, any path matching a parent-registered pattern) from any session, including child modules operating on parent files.
- **Module freeze**: `~/parent/<module>/.cowork/freeze.json`. Registered from a module session. Blocks writes only within that module's tree.

Before every Write/Edit, CoS reads whichever `.cowork/freeze.json` files are in scope for the current session (module session reads module-level and, if targeting a parent file, parent-level) and enforces `gstack-team:guard` against the combined list.

## §deploy-scope — cross-module rules

`gstack-team:ship`, `gstack-team:canary`, and `gstack-team:land-and-deploy` are always module-scoped when invoked from a module session. A coordinated cross-module release requires:

1. A parent session to be active.
2. A parent-level plan (authored via `gstack-team:autoplan`) that enumerates each module to deploy and the order.
3. The parent invokes each module's deploy command via the bus, one at a time, waiting for each to return green before advancing.

A module session that proposes a cross-module deploy halts at the proposal stage with a decision card: (a) promote this to a parent-session plan, (b) descope to single-module deploy, (c) cancel.

## §retro-format — how gstack-team:retro plugs in

Milestone retros use `gstack-team:retro` as the format. CoS feeds it:

- The log slice since the last retro (from `project-studio/log/`)
- The milestone's roadmap entry (from `project-studio/project/roadmap.md`)
- Any open items from registers (risks, open-questions, learnings)

The retro output lands in `project-studio/retros/<YYYY-MM-DD>-<milestone>.md`. A PDF export is generated by default (Invariant #24) to `project-studio/exports/<YYYY-MM-DD>-<milestone>-retro.pdf`.

## §context-save / context-restore — how session continuity plugs in

These two gstack-team skills replace Project Studio's earlier ad-hoc resume layer. The workflow:

- **On session wind-down** (last user action, or before a risky operation): CoS runs `gstack-team:context-save` to snapshot the current session's understanding into `.cowork/context/<timestamp>.md`.
- **On session start** (boot protocol, step 1): CoS checks for `.cowork/context/` entries. If present, runs `gstack-team:context-restore` against the most recent snapshot before loading `protocol/boot.md`.

Project Studio's own `protocol/resume.md` handles higher-level resume concerns that are specific to the studio model (persona reload, register reconciliation, parent security check). The two layers do not overlap: gstack-team's skills handle the generic session state; Project Studio's resume handles studio-specific state.

## §careful-mode — default critique stance

`gstack-team:careful` is not a one-shot escalation. Project Studio defaults CoS into careful mode for any action that touches production, deployment, security, data migration, or parent-level files. Careful mode raises the depth of plan-critique (all four lenses run at full depth even on light scale) and requires an extra user-facing confirmation beyond the standard propose-then-yes gate.

CoS explicitly de-escalates careful mode for local dev, docs-only, and sandbox actions — those use the standard critique depth.

## §graphify-combo — when gstack-team:* methodology skills pair with graphify

Invariant #19 now lists `gstack-team:review`, `gstack-team:cso`, `gstack-team:investigate`, `gstack-team:qa`, and `gstack-team:design-review` as valid downstream analysis skills for a code-heavy spawn. The decision table in `references/invokable-skills.md` enumerates the typical pairings:

- `graphify` + `gstack-team:review` — pre-merge code review against a scoped diff
- `graphify` + `gstack-team:cso` — OWASP/STRIDE security audit against a module
- `graphify` + `gstack-team:investigate` — root-cause hunt with cross-file evidence
- `graphify` + `gstack-team:qa` — QA targeting after structural changes (browser-side tests informed by graph clusters)

## §degraded-mode — Degraded mode: gstack-team absent

If gstack-team is not installed:

- Plan-critique falls back to CoS-driven structured critique using role-tag specialists (the original v3.0.0 behavior). Quality drops, but Invariant #20 is still satisfied.
- Browser-dependent skills (`gstack-team:qa`, `gstack-team:design-review`, `gstack-team:browse`) are unavailable. Specialists are told in their spawn prompts that browser evidence cannot be gathered.
- Deploy skills (`gstack-team:ship`, `gstack-team:canary`, `gstack-team:land-and-deploy`) are unavailable. CoS surfaces a "no deploy path" flag on any proposal that would otherwise trigger a deploy.
- PDF export falls back to markdown-only. CoS announces the downgrade in every deliverable proposal.
- Freeze/guard fall back to a lightweight in-memory freeze list maintained in the session log; it does not survive session end.

Degraded mode is announced at boot in `project-studio/log/<today>.md` as the first entry and in every subsequent proposal affected by the missing capability.

## Related

- `references/skill-catalog.md` — full list of invokable skills with namespace and scope
- `references/invokable-skills.md` — spawn template, graphify combo matrix
- `references/connectors.md` — severity tiers and degraded-mode triggers
- `references/scope-policy.md` — how scope interacts with gstack-team's `freeze`/`guard`
- `references/monorepo-pattern.md` — how gstack-team's assumptions map onto Project Studio's parent/module architecture
- `references/feature-provenance.md` — the full pro