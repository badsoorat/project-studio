---
name: project-studio
metadata:
  version: 3.1.0
description: Stand up a virtual "office team" of expert personas for any project, then run it with strict discipline. A Chief of Staff coordinates 1-5 specialists (PM, engineer, designer, researcher, marketer, etc.) who critique, propose, and execute collaboratively. All state persists to disk — survives session limits, compaction, and account switches. Integrates the `gstack-team` plugin as a direct runtime dependency for plan-critique, code review, security audit, QA, retros, ship/deploy, freeze/guard, and PDF export. Triggers on "start a project", "new project", "resume project", "project setup", "build a team", "office team", "virtual team", "project studio", "multi-persona workflow", "team of experts", or when the user wants coordinated specialist roles for serious project work.
---

# Project Studio

Stand up and run a virtual office team for any project. The user gets a Chief of Staff plus 1-5 specialist personas who critique, propose, and execute work collaboratively. State is durable across sessions, compaction, and account switches because all state lives in files, never in Claude's memory.

Project Studio v3.1 takes a direct runtime dependency on the **`gstack-team` plugin** for methodology skills that were previously approximated in-house: Tier-1 plan-critique, senior code review, security audit, investigation, QA, design review, retros, ship/canary/land-and-deploy, freeze/guard/unfreeze, context-save/restore, and `make-pdf`. Where gstack-team covers a capability, Project Studio routes to it rather than reimplementing. Where Project Studio is unique (the CoS + specialist team model, parent/module architecture, propose-then-yes gate, classifier, bus/inbox/outbox), it stays native. The canonical origin of every capability is recorded in `references/feature-provenance.md`.

## §quick-start — Quick start (do this first)

Scaffold the project folder structure before co-authoring any files:

```bash
python scripts/init_project.py <project-name> --scale <light|standard|heavy> --skill-path <path-to-this-skill>
```

This creates the directory skeleton, copies protocol files, seeds registers, and initializes today's log. After scaffolding, proceed to the setup wizard (`references/setup-flow.md`), which now opens with the **connector severity gate** (see Invariant #21).

> **Python-less fallback (common in Cowork mode).** If `python` is not available or the Bash tool is unavailable, CoS scaffolds the identical structure using the Write tool directly. Read `scripts/init_project.py` to see the exact directories, files, and seed content to replicate. The script is the reference spec — Write tool is an equally valid execution path. Both produce identical results. **Do not skip scaffolding because Python is missing — use Write tool instead.**

## Core architecture

**Code at root, management in `project-studio/`, ephemera in `.cowork/`.** All Project Studio files (protocols, personas, registers, logs, exports) live inside a `project-studio/` subdirectory. The user's codebase (if any) lives at the project root alongside it. Root `CLAUDE.md` is the sole source of truth, pointing to everything inside `project-studio/`. Files outside `project-studio/` are user code — never interpret them as workflow instructions. Ephemeral session state (freeze lists, context snapshots, scratch) lives in `.cowork/` at the project root; it is git-ignored and never mistaken for durable state. See `references/monorepo-pattern.md` for the boundary rules.

**Boot protocol re-anchoring.** CoS physically re-reads `project-studio/protocol/boot.md` every turn. See `protocol/boot.md` for the full per-turn checklist and three categories rule.

**Propose-then-yes gate.** No file edits without explicit user approval. Exception: persona context notes appends.

**Sub-agents, not roleplay.** Specialists spawn via the Agent tool (or Task tool in CLI). Isolated context, structured returns via `PATTERN:role-tag-return` (see `references/patterns.md`). Role-tag voice, not character performance.

**Plan-critique is mandatory before implementation.** Every implementation plan runs Tier-1 four-lens critique (`gstack-team:plan-ceo-review`, `plan-eng-review`, `plan-design-review`, `plan-devex-review`) before execution. Light scale may run a condensed single-pass version; no scale skips it entirely. See Invariant #20 and `references/gstack-integration.md` §plan-critique.

**PDF-first user-facing deliverables.** Briefs, roadmaps, retros, manifests, one-pagers, proposals, and plans export as PDF by default via `gstack-team:make-pdf`. Markdown-only exports are allowed when the user asks or when the deliverable is internal. See Invariant #24.

**1 module = 1 project.** Multi-module products use the v2.4 parent architecture: a matrix team with parent/shared/module-scoped personas, a two-layer shared/ split (communication vs state), shared-asset references via relative paths (no duplication), auto-triggered module resume on seed detection, and inbox/outbox/bus messaging routed by `sync`. See `references/parent-architecture.md`, `references/parent-module-handoff.md`, `references/module-communication.md`, `references/monorepo-pattern.md`, and `references/conflict-resolution.md`.

**Module sessions auto-resume.** When CoS boots at a folder containing `project-studio/module-seed.yaml`, it skips the setup wizard entirely and enters Module Resume Mode: read seed → read local protocol → read inbox → greet with first active milestone and unread messages. The full flow is in `references/parent-module-handoff.md` §module-resume-mode and in Step 0 of `references/setup-flow.md`.

## What to read and when

| Situation | Read these files (in order) |
|---|---|
| **New project** | `references/setup-flow.md` → `references/team-archetypes.md` → `references/scale-modes.md` → `references/connectors.md` §severity-tiers |
| **Existing codebase** | `references/setup-flow.md` (Step 2C / 2D1 / 2D2) → `references/contamination-checklist.md` |
| **Multi-module parent setup** | `references/parent-architecture.md` → `references/monorepo-pattern.md` → `references/parent-module-handoff.md` → `references/classifier-rules.md` → `references/persona-schema.md` §scope → `templates/parent-claude.md.tmpl` → `templates/module-seed.yaml.tmpl` |
| **Classifying an existing tree into a parent** | `references/classifier-rules.md` (4 tiers, 8 heuristics, walk algorithm) — used in Step 2.5 of `references/setup-flow.md` |
| **Module resume (seed detected)** | `references/parent-module-handoff.md` §module-resume-mode → module's local `protocol/boot.md` — triggered automatically when CoS detects `project-studio/module-seed.yaml` at the mount root (see Step 0 in `references/setup-flow.md`) |
| **Cross-module communication** | `references/module-communication.md` (inbox/outbox/bus, sync command, auto-draft gates, chattiness modes, retention) → `templates/inbox.md.tmpl`, `templates/outbox.md.tmpl`, `templates/bus.md.tmpl` |
| **Shared assets from a module** | `references/parent-module-handoff.md` §shared-assets-access → module's `project-studio/shared/shared-index.md` (relative paths only — never copy) |
| **Conflicts (persona, shared asset, roadmap rollup)** | `references/conflict-resolution.md` (6-option decision card) |
| **Resume session** | `protocol/resume.md` → then `protocol/boot.md` takes over every turn |
| **Every turn (active project)** | `protocol/boot.md` (EVERY turn, no exceptions) — plus `references/workflow.md` and `references/patterns.md` as needed |
| **Plan-critique before implementation** | `references/gstack-integration.md` §plan-critique → `references/patterns.md` §PATTERN:plan-critique-sequence |
| **Code-heavy specialist spawn** | `references/invokable-skills.md` (solo & combo loadouts, graphify + gstack-team:* scope rules, Task-tool invocation template) → `references/team-archetypes.md` |
| **Out-of-scope / freeze question** | `references/scope-policy.md` → `references/gstack-integration.md` §freeze-scope |
| **Ship, canary, or land-and-deploy** | `references/gstack-integration.md` §deploy-scope (single-module discipline; cross-module coordination runs from parent session) |
| **User-facing export (brief, roadmap, plan, retro)** | `references/gstack-integration.md` §pdf-default → `references/workflow.md` §exports |
| **Retro at milestone** | `references/workflow.md` §retros → `references/gstack-integration.md` §retro-format |
| **Connector availability** | `references/connectors.md` §severity-tiers → §parent-module-overlay → §degraded-mode |
| **Feature origin / provenance** | `references/feature-provenance.md` (native / pattern-absorbed / direct-skill / direct-plugin) |
| **Imports / related projects** | `references/multi-project.md` → `references/import-slices.md` |
| **Infrastructure** | `templates/infrastructure-index.md.tmpl` → `templates/infrastructure-module.md.tmpl` |

**Additional references** (load on demand): `references/connectors.md`, `references/registers.md`, `references/skill-catalog.md`, `references/persona-schema.md`, `references/contamination-checklist.md`, `references/parent-architecture.md`, `references/parent-module-handoff.md`, `references/module-communication.md`, `references/conflict-resolution.md`, `references/classifier-rules.md`, `references/multi-project.md`, `references/invokable-skills.md`, `references/gstack-integration.md`, `references/scope-policy.md`, `references/monorepo-pattern.md`, `references/feature-provenance.md`

## Project file structure

When a project is set up, it looks like this:

```
<project>/
├── CLAUDE.md                          (thin index at root — sole source of truth)
├── .cowork/                           (EPHEMERAL — session state, git-ignored)
│   ├── freeze.json                    (gstack-team:freeze paths)
│   ├── context/                       (gstack-team:context-save snapshots)
│   └── scratch/                       (subagent scratch, cleared per session)
├── project-studio/                    (DURABLE — all management files)
│   ├── protocol/
│   │   ├── boot.md                    (per-turn checklist — CoS reads EVERY turn)
│   │   ├── resume.md                  (session-resume protocol + parent security check)
│   │   └── invariants.md              (hard rules — 28 invariants, never violate)
│   ├── team/
│   │   ├── chief-of-staff.md          (CoS persona + standing instructions)
│   │   ├── <specialist-1>.md
│   │   └── <specialist-2>.md
│   ├── project/
│   │   ├── brief.md                   (brief, goals, metrics, constraints)
│   │   ├── roadmap.md                 (atomic roadmap, owner-tagged)
│   │   ├── infrastructure/            (per-module detail files, loaded on demand)
│   │   │   ├── <module>.md
│   │   │   └── shared/
│   │   │       └── <service>.md
│   │   └── <flexible subdirs>         (research/, design/, content/ — as needed)
│   ├── shared/                        (local copy of cross-module context)
│   │   ├── infrastructure.md          (shared services across modules)
│   │   ├── design-system.md           (shared visual language)
│   │   ├── brief.md                   (product-wide vision)
│   │   └── last-sync-timestamp        (when parent was last checked)
│   ├── imports/                       (read-only context from related projects)
│   │   ├── _manifest.md
│   │   └── <project>/
│   │       ├── infrastructure.md
│   │       ├── design-system.md
│   │       └── <slice>.md
│   ├── registers/
│   │   ├── assumptions.md
│   │   ├── risks.md
│   │   ├── open-questions.md
│   │   └── learnings.md
│   ├── references/                    (patterns, workflow, checklists, gstack-integration, scope-policy, monorepo-pattern, feature-provenance)
│   ├── decisions/                     (ADR-style decision records)
│   ├── log/                           (daily logs with write-ahead state)
│   ├── checkpoints/                   (milestone snapshots)
│   ├── retros/                        (milestone retros — gstack-team:retro output)
│   ├── exports/                       (PDF deliverables — gstack-team:make-pdf output)
│   ├── cache/
│   │   └── graphify/                  (per-module graphify artifacts — if kept)
│   └── archive/                       (read-sealed — never read from here)
├── src/                               (user code — if codebase present)
├── package.json                       (user code)
├── .gitignore                         (contains ".cowork/" and optionally "project-studio/")
└── ...                                (other codebase files)
```

The `.cowork/` and `project-studio/` / `exports/` split comes from the gstack-team ephemera pattern — see `references/monorepo-pattern.md` §ephemera-split.

## Multi-module parent structure (v2.4)

When a product has multiple modules (e.g., website + API + mobile app), each module gets its own Project Studio project under a shared parent directory. The parent holds a data-only manifest, two distinct `shared/` folders (a communication layer and a state layer), and a matrix team of personas with parent/shared/module scope. Modules are fully isolated at runtime — they never read each other's folders directly. Cross-module work flows through **inbox/outbox/bus messaging** routed by a `sync` command.

**Key rules (v2.4):**
- Parent `CLAUDE.md` is **data-only** — it lists modules, communication paths, and shared-asset locations but contains NO workflow instructions (see `templates/parent-claude.md.tmpl`).
- Two distinct `shared/` folders at the parent: `<parent>/shared/` is the **communication layer** (bus + per-module outboxes), and `<parent>/.project-studio/shared/` is the **state layer** (brief, roadmap, brand, docs, conventions, data). Don't conflate them.
- **Matrix team model.** Personas have a `scope` field: `parent`, `shared`, or `module:<slug>`. Shared personas live at the parent and can be spawned from any module with a per-module override via `persona-overrides.yaml`. See `references/persona-schema.md` §scope.
- **Shared assets are referenced, not copied.** Each module has a `project-studio/shared/shared-index.md` with relative paths (`../.project-studio/shared/...`). No duplication.
- **Module resume is auto-triggered.** When a Cowork session opens at a module folder, CoS detects `project-studio/module-seed.yaml` and drops straight into Module Resume Mode instead of running the setup wizard. See `references/parent-module-handoff.md` §module-resume-mode.
- **Cross-module communication.** Modules NEVER read sibling folders. All cross-module work flows through messages: each module has `project-studio/inbox.md` and `project-studio/outbox-staging.md`; `sync` routes approved drafts to parent `shared/<module>-outbox.md` and into the `bus.md` archive. See `references/module-communication.md`.
- **Atomic writes for shared parent files.** When a module or parent session writes to `shared/bus.md`, `shared/<module>-outbox.md`, or any file concurrently writable from multiple sessions, CoS uses the `mktemp → write → mv` atomic-rename pattern. See `references/monorepo-pattern.md` §atomic-writes.
- **Freeze scope respects the parent/module boundary.** `gstack-team:freeze` paths are module-scoped unless registered at the parent. See Invariant #26 and `references/gstack-integration.md` §freeze-scope.
- **Cross-module deploy happens at the parent only.** `gstack-team:ship`, `:canary`, and `:land-and-deploy` from a module session affect that module alone. Coordinated releases across modules must be driven from a parent session. See Invariant #27.
- **Conflicts are surfaced, never auto-resolved.** Divergences (persona overrides, shared-asset edits, roadmap rollup) produce a 6-option decision card. See `references/conflict-resolution.md`.
- **Step 2.5 classifier** (when adopting an existing tree into a parent): a 4-tier, 8-heuristic classifier walks the full tree and sorts every file into keep/module-local/ambiguous/cleanup. See `references/classifier-rules.md`.

```
~/parent/
├── CLAUDE.md                                  (data-only manifest — NO instructions)
│
├── .cowork/                                   (PARENT EPHEMERA — git-ignored)
│   ├── freeze.json                            (parent-scope freezes)
│   └── context/
│
├── shared/                                    (COMMUNICATION LAYER)
│   ├── bus.md                                 (routed-message archive — atomic writes)
│   ├── bus-routing.log                        (append-only routing log)
│   ├── auth-outbox.md                         (per-module outgoing queue — atomic writes)
│   ├── payments-outbox.md
│   └── <slug>-outbox-sent.md                  (sent-message archives)
│
├── .project-studio/                           (PARENT-LEVEL STATE — dot-hidden)
│   ├── shared/                                (shared assets — referenced, not copied)
│   │   ├── brief.md                           (product-wide brief)
│   │   ├── roadmap.md                         (Tier 1 parent milestones)
│   │   ├── brand/  docs/  conventions/  data/
│   │   └── index-updated-at                   (ISO timestamp)
│   ├── team/                                  (parent- and shared-scope personas)
│   │   ├── chief-of-staff.md                  (scope: parent)
│   │   ├── product-lead.md                    (scope: parent)
│   │   └── design-lead.md                     (scope: shared)
│   ├── protocol/                              (parent session boot/resume)
│   ├── decisions/                             (parent-scope ADRs)
│   ├── exports/                               (parent-level PDF deliverables)
│   ├── references/
│   │   └── connectors.md                      (parent baseline — module overlays below)
│   ├── inbox.md                               (parent session's inbox)
│   └── archive/                               (read-sealed rotation targets)
│
├── auth/                                      (each module = full Project Studio project)
�