# CHANGES — project-studio v3.0 → v3.1

This file describes every modification made in the v3.1 update of the
`project-studio` skill. The headline is the Model A integration of the
`gstack-team` plugin as a direct runtime dependency — the same integration
shape as `graphify`, not pattern absorption.

## Headline

**`gstack-team` becomes a first-class runtime dependency.** Twenty-six
`gstack-team:*` skills are now callable by specialists and CoS via fully
qualified names (namespace migration). The plugin joins `workspace bash`
in the **Critical** connector tier. A standalone graphify + gstack-team
combo matrix governs when specialists load structural analysis vs
methodology skills.

Alongside the Model A integration, v3.1 introduces a tiered connector
setup wizard, a mandatory plan-critique gate at every scale, a
standardized exports path with PDF-as-default, ephemeral state
(`.cowork/`) separated from durable state (`project-studio/` and
`.project-studio/`), and a feature provenance manifest with PDF snapshot
that tracks capability origin for every behavior in the skill.

## Invariants — amendments and additions

### Amended

- **#8 Respect scale mode** — added "one exception with no room for
  negotiation": Tier-1 plan-critique (see #20) runs at every scale,
  including light. Scale may shrink the number of lenses or depth per
  lens, but plan-critique is never fully skipped.
- **#19 Code-heavy specialist spawns load graphify on demand** —
  expanded the list of downstream analysis skills that a graphify-bearing
  spawn may combine with to include `gstack-team:review`,
  `gstack-team:cso`, `gstack-team:investigate`, `gstack-team:qa`, and
  `gstack-team:design-review` (all fully qualified). Added devops,
  browser-QA, release-readiness, and security-audit to the list of
  code-heavy archetypes that qualify.

### Added

- **#20 Plan-critique is mandatory before implementation.** Tier-1
  plan-critique runs before any plan executes: four lenses via
  `gstack-team:plan-ceo-review`, `gstack-team:plan-eng-review`,
  `gstack-team:plan-design-review`, `gstack-team:plan-devex-review`.
  Light scale runs a condensed single-pass version but may not skip
  entirely. Parent-level plans that affect multiple modules run the four
  lenses at the parent first, then each affected module runs the
  relevant lens locally for its slice.
- **#21 Connector severity gate at setup.** The setup wizard classifies
  every connector into Critical, Recommended, or Optional and prompts
  tier-by-tier. Critical defaults: workspace bash + `gstack-team`.
  Recommended defaults: `graphify` + `Claude-in-Chrome` MCP. Optional
  defaults: Vercel MCP and any project-specific MCPs. Absent connectors
  are recorded in `references/connectors.md` and propagated to
  specialists so they can substitute or degrade.
- **#22 Retro runs at every milestone, not on calendar.** Retros are
  tied to roadmap milestone completion, not a fixed weekly cadence.
  Weekly retros become the default only if the milestone cadence is
  itself weekly. Format is `gstack-team:retro` against the log slice
  since the last retro.
- **#23 Scope policy is cooperative, not absolute.** When a proposed
  action touches files outside the module's defined scope, CoS surfaces
  the out-of-scope paths in a single decision card and proceeds only on
  explicit approval. Hard scope locks exist only for parent-level files
  from a module session and for frozen paths registered via
  `gstack-team:freeze`.
- **#24 PDF is the default for user-facing deliverables.** Briefs,
  roadmaps, retro reports, manifests, one-pagers, proposals, plans, and
  design specs export as PDF via `gstack-team:make-pdf` by default.
  Markdown-only is allowed when the user asks or when the deliverable is
  internal. Default is never silent: CoS announces "Export format: PDF
  via make-pdf" in the proposal so the user can override.
- **#25 Connector setup is scoped to the current context.** In
  multi-module projects, each module declares its own connector
  availability as an overlay on the parent baseline. Cross-module
  actions at the parent reconcile the union; a connector absent in any
  one involved module downgrades the action to the least-capable common
  path.
- **#26 Freeze scope respects parent/module boundary.**
  `gstack-team:freeze` paths are module-scoped unless explicitly
  registered at the parent. Module-level freezes cannot block sibling
  modules or parent files. Parent-level freezes block writes from any
  child module session via the parent-shared-files gate.
- **#27 Cross-module deploy happens at the parent only.**
  `gstack-team:ship`, `gstack-team:canary`, and
  `gstack-team:land-and-deploy` may only affect a single module from a
  module session. Coordinated cross-module releases must be driven from
  a parent session, which routes deploy commands to each module via the
  bus. Module sessions attempting cross-module deploy halt with a
  "promote to parent" decision card.
- **#28 Feature provenance is kept current.** Every capability has a
  recorded origin (native, pattern-absorbed, direct-skill, or
  direct-plugin) in `references/feature-provenance.md` plus a PDF export
  under `project-studio/exports/`. Whenever a capability is added,
  swapped, or retired, CoS updates both.

## Files modified

All paths are relative to `project-studio/`.

| File | Change |
|---|---|
| `SKILL.md` | Version bump v3.0 → v3.1; added gstack-team integration summary; added Model A note; added provenance link |
| `protocol/invariants.md` | Amended #8 and #19; added #20-#28 |
| `protocol/boot.md` | Added pre-write freeze-check step; added plan-critique gate; added PDF-default announcement step |
| `protocol/resume.md` | Added connector severity reconciliation; added `.cowork/` presence check; added degraded-mode banner |
| `protocol/boot-light.md` | Added plan-critique gate (condensed single-pass) to light scale |
| `references/patterns.md` | Added 3 new patterns: PATTERN:plan-critique-sequence, PATTERN:pre-write-checklist (freeze-aware), PATTERN:retro-output-schema (milestone-triggered) |
| `references/skill-catalog.md` | New file — canonical catalog of all 26 gstack-team:* skills, graphify, native substitutes, and degraded-mode matrix |
| `references/invokable-skills.md` | Rewrote v3.1: graphify + gstack-team combo matrix; solo vs combo loadouts; Task-tool invocation template; anti-patterns; degraded-mode table |
| `references/team-archetypes.md` | Added Archetype 8 (Platform/Infra Team); updated all archetypes to reference gstack-team:* skills |
| `references/scale-modes.md` | Amended light scale: plan-critique gate preserved; PDF default preserved; severity-gated Critical tier preserved |
| `references/parent-architecture.md` | Added v3.1 section: `.cowork/` at parent, parent-level `exports/`, cross-module deploy routing, connector overlay reconciliation |
| `references/setup-flow.md` | Appended v3.1 section: Step 5 severity-gated wizard, Step 6 PDF announcement + plan-critique gate, Step 7a `.cowork/` scaffolding, Step 7b `exports/` + feature-provenance seed, Step 7f parent-level ephemera, light-scale amendment, interruption-recovery sixth row |
| `references/connectors.md` | New file — severity tiers, parent/module overlay, degraded-mode table, connector manifest YAML |
| `references/gstack-integration.md` | New file — capability-to-skill mapping, plan-critique §, freeze-scope §, deploy-scope §, pdf-default §, degraded-mode § |
| `references/feature-provenance.md` | New file — provenance catalog with four types (native, pattern-absorbed, direct-skill, direct-plugin); update procedure |
| `references/scope-policy.md` | New file — cooperative scope rules; decision-card format; hard-lock exceptions |
| `references/workflow.md` | Added retros § (milestone-triggered); added plan-critique § (Tier-1 sequence); added export § (PDF-default) |
| `templates/log-entry.md.tmpl` | Added Degraded-mode field; added Export-format field |
| `templates/roadmap.md.tmpl` | Added milestone → retro trigger column |
| `templates/parent-claude.md.tmpl` | Added parent-level connector overlay section; added `.cowork/` inventory |
| `templates/CLAUDE.md.tmpl` | Added connector manifest pointer; added export format default |
| `scripts/init_project.py` | Extended to scaffold `.cowork/` (context/, freeze.json, cache/graphify/) and `exports/` at both parent and module levels |
| `evals/evals.json` | Added four new evals: plan-critique-gate-at-light-scale, severity-gate-tier-classification, pdf-default-announcement, freeze-scope-enforcement |
| `evals/xref_check.py` | Extended to verify all `gstack-team:*` references are fully qualified; verify invariant numbering; verify PATTERN catalog consistency |

## New concepts

- **Severity-gated connector setup** (Invariant #21). Critical /
  Recommended / Optional tiers with explicit user prompting at setup.
- **Plan-critique gate** (Invariant #20). Mandatory Tier-1 four-lens
  critique before any plan executes, at every scale.
- **`.cowork/` ephemera split**. Ephemeral, git-ignored state in
  `.cowork/` (context snapshots, freeze list, graphify cache) distinct
  from durable state in `project-studio/` and `.project-studio/`.
- **Atomic-write discipline** for shared parent files. `mktemp →
  write → mv` pattern to prevent partial-read races when multiple module
  sessions touch `../shared/`.
- **Standardized `exports/` path**. User-facing deliverables land under
  `project-studio/exports/<YYYY-MM-DD>-<slug>.<ext>` at both parent and
  module levels.
- **PDF-first default** (Invariant #24). `gstack-team:make-pdf` renders
  deliverables to PDF; markdown is opt-in.
- **Feature provenance manifest** (Invariant #28). Every capability
  carries a recorded origin. Four types: native, pattern-absorbed,
  direct-skill, direct-plugin. Canonical record is
  `references/feature-provenance.md` plus a PDF snapshot under
  `project-studio/exports/`.
- **Parent/module connector overlay** (Invariant #25). Each module
  overlays the parent's connector baseline; cross-module actions
  reconcile the union.
- **Cooperative scope policy** (Invariant #23). Scope is a
  conversation, not a lock — except for parent files from a module
  session and frozen paths.
- **Milestone-triggered retros** (Invariant #22). Retros run at
  roadmap milestone completion, not on fixed calendar.

## Namespace migration

Before v3.1, unqualified aliases (`review`, `cso`, `investigate`, `qa`,
`retro`, `careful`, `ship`, `freeze`, `guard`, `learn`, `autoplan`,
`office-hours`, `design-review`, `design-consultation`, `make-pdf`, and
the plan-*-review family) resolved to gstack-team skills by convention.

v3.1 is a **hard-cut** migration: specialists and CoS must invoke the
fully qualified `gstack-team:<skill>` form. Unqualified aliases no
longer resolve. If the bundle references an unqualified alias, treat it
as drift and migrate.

Files that deliberately retain unqualified aliases (for historical /
explanatory reasons only):
- `references/invokable-skills.md` — v3.1 migration note at the top of
  the file calls out the change.
- `SKILL.md` — v3.1 announcement section explains the migration.

## Degraded mode

When `gstack-team` is not installed, specialists substitute native
equivalents per the table in `references/invokable-skills.md`:

| Missing gstack-team skill | Native substitute |
|---|---|
| `gstack-team:review` | `code-review-senior-perspective` |
| `gstack-team:cso` | `saas-business-logic-analyst` + manual OWASP checklist |
| `gstack-team:investigate` | Native CoS-led debugging (no skill) |
| `gstack-team:qa` | `webapp-testing` (playwright) |
| `gstack-team:design-review` | `ux-heuristics` + `refactoring-ui` |
| `gstack-team:plan-*-review` | See `references/gstack-integration.md` §plan-critique degraded |
| `gstack-team:retro` | Inline retro template from `patterns.md` PATTERN:weekly-retro |
| `gstack-team:make-pdf` | `pdf` skill or markdown-only export with user opt-in |

Degraded mode does NOT waive Invariant #20. Plan-critique still runs —
just with native substitutes. The substitution is logged per turn under
`### Degraded-mode` in the log entry.

## Absorbed patterns (narrow, 3 total)

Model A means we do NOT absorb gstack-team's methodology wholesale; we
invoke its skills by name. Three *narrow* patterns were absorbed
because they are idiomatic to how a workspace file layout ought to
work, regardless of whether gstack-team is present:

1. **`.cowork/` ephemera split** — ephemeral state lives in `.cowork/`,
   durable state lives in `project-studio/` (module) and
   `.project-studio/` (parent). Came from gstack-team's convention;
   kept even in degraded mode.
2. **Atomic-write discipline** — `mktemp → write → mv` for shared
   parent files. Came from gstack-team's bus-write pattern; kept even
   in degraded mode because the race it prevents is real.
3. **Standardized `exports/` path** — `project-studio/exports/<YYYY-
   MM-DD>-<slug>.<ext>`. Came from gstack-team's `/make-pdf`
   convention; kept even in degraded mode because it replaces the
   previous ad-hoc deliverable-dropping that drifted between modules.

## Bundle verification

Verified via grep/wc:

- **Invariant references** — all `Invariant #N` citations resolve to
  a defined invariant (#1-#28). Highest-cited: #20 × 25, #24 × 17, #27
  × 8, #26 × 8, #22 × 7, #21 × 6, #19 × 6.
- **PATTERN names** — 12 PATTERN names used across the bundle and
  consistent with definitions in `references/patterns.md`:
  `acceptance-criterion`, `boot-read`, `plan-critique-sequence`,
  `pre-write-checklist`, `quality-gate`, `reflexion-check`,
  `retro-output-schema`, `role-tag-return`, `role-tag-voice`,
  `spawn-context-slice`, `weekly-retro`, `wind-down-detect`.
- **Unqualified gstack aliases** — none outside explanatory contexts
  (`invokable-skills.md` migration note, `SKILL.md` v3.1 announcement).
- **v3.1 concept coverage** — each of `severity-gated`, `.cowork/`,
  `exports/`, `feature-provenance`, `plan-critique`, `Tier-1`,
  `degraded-mode`, `atomic-write`, `severity tier` appears across
  multiple files.

Bundle size: 48 files, ~8,124 lines (excluding templates and this
CHANGES.md).

## File tree

```
project-studio-updated/
├── SKILL.md
├── CHANGES.md                           ← this file
├── protocol/
│   ├── boot-light.md
│   ├── boot.md
│   ├── invariants.md                    ← amended #8, #19; added #20-#28
│   └── resume.md
├── references/
│   ├── classifier-rules.md
│   ├── conflict-resolution.md
│   ├── connectors.md                    ← new in v3.1
│   ├── contamination-checklist.md
│   ├── feature-provenance.md            ← new in v3.1
│   ├── gstack-integration.md            ← new in v3.1
│   ├── import-slices.md
│   ├── invokable-skills.md              ← rewritten for v3.1
│   ├── module-communication.md
│   ├── monorepo-pattern.md
│   ├── multi-project.md
│   ├── parent-architecture.md           ← v3.1 additions appended
│   ├── parent-module-handoff.md
│   ├── patterns.md                      ← +3 patterns
│   ├── persona-schema.md
│   ├── registers.md
│   ├── scale-modes.md                   ← amended for plan-critique at light
│   ├── scope-policy.md                  ← new in v3.1
│   ├── setup-flow.md                    ← v3.1 additions appended
│   ├── skill-catalog.md                 ← new in v3.1
│   ├── team-archetypes.md               ← +Archetype 8
│   └── workflow.md                      ← retros § + plan-critique § + export §
├── templates/
│   ├── CLAUDE.md.tmpl
│   ├── START-HERE.md.tmpl
│   ├── brief.md.tmpl
│   ├── bus.md.tmpl
│   ├── checkpoint.md.tmpl
│   ├── chief-of-staff.md.tmpl
│   ├── import-manifest.md.tmpl
│   ├── inbox.md.tmpl
│   ├── infrastructure-index.md.tmpl
│   ├── infrastructure-module.md.tmpl
│   ├── infrastructure-shared.md.tmpl
│   ├── log-entry.md.tmpl                ← +Degraded-mode, +Export-format
│   ├── module-seed.yaml.tmpl
│   ├── module-update.md.tmpl
│   ├── outbox.md.tmpl
│   ├── parent-claude.md.tmpl            ← +overlay §, +.cowork/ inventory
│   ├── persona.md.tmpl
│   ├── roadmap.md.tmpl                  ← +milestone-retro column
│   └── shared-index.md.tmpl
├── scripts/
│   └── init_project.py                  ← +.cowork/ + exports/ scaffold
└── evals/
    ├── evals.json                       ← +4 evals
    └── xref_check.py                    ← +qualified-alias + invariant + PATTERN checks
```

## Migration note for existing projects

A project built with v3.0 boots under v3.1 as follows:

1. On first resume, CoS detects the version mismatch and runs a
   one-time migration:
   - Scaffolds `.cowork/` and `exports/` at module (and parent if
     multi-module).
   - Creates `references/connectors.md` with a default manifest based
     on observed tool availability, then prompts the user once to
     confirm/override.
   - Creates `references/feature-provenance.md` seeded with the v3.1
     provenance catalog.
   - Migrates any existing ad-hoc deliverables under
     `project-studio/reports/` or similar into
     `project-studio/exports/`.
2. The one-time migration writes a log entry marking the v3.0 → v3.1
   transition and the user's setup choices.
3. No retro, plan, or proposal carried forward from v3.0 is
   invalidated. The Tier-1 plan-critique gate applies only to new
   plans authored after migration.
