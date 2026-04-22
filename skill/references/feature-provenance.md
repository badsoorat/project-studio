# Feature provenance manifest

Every capability in Project Studio has a recorded origin. This is the canonical markdown record; the matching PDF export (`project-studio/exports/<YYYY-MM-DD>-feature-provenance-manifest.pdf`) is the user-facing deliverable. Both are kept in sync per Invariant #28.

## Provenance types

There are four types of provenance. Know which one you're looking at when you reference a capability.

- **native** — Invented inside Project Studio. No external reference. Can be modified freely.
- **pattern-absorbed** — Inspired by an external source but implemented inside Project Studio's code/files. Reference is a design influence, not a runtime dependency. Can be modified, but modifications should be conscious of the pattern's intent.
- **direct-skill** — Runtime invocation of an external skill. The external skill is read at execution time. Modifications to the external skill take effect immediately. Project Studio owns the wrapping, not the content.
- **direct-plugin** — Runtime invocation of a skill that lives inside an installed plugin. Same as direct-skill, but provenance is a plugin (group of skills) rather than a single skill.

When in doubt: if removing the external dependency breaks the feature, it's direct-*. If removing the external dependency leaves a copy of the pattern intact but orphaned from future improvements, it's pattern-absorbed. If the external reference didn't exist when the feature was built, it's native.

## Manifest

| Feature | Provenance | Type | Notes | Swap path |
|---|---|---|---|---|
| Chief of Staff orchestration | project-studio native | native | CoS role, routing logic, three-categories rule, propose-then-yes gate | self-modify |
| Per-turn boot re-read | project-studio native | native | Invariant #12; re-read protocol/boot.md every turn to prevent drift | self-modify |
| Specialist personas with `PATTERN:role-tag-voice` | project-studio native | native | Role-tag structured returns, not character performance | self-modify |
| Persona schema with scope (parent/shared/module) | project-studio native | native | Scope field enables matrix team model | self-modify |
| Log-as-durability layer | project-studio native | native | Invariant #2; write-ahead and after-write markers | self-modify |
| Register files (assumptions, risks, open-questions, learnings) | project-studio native | native | — | self-modify |
| Memory Palace metaphor | Memory Palace (pattern inspiration) | pattern-absorbed | Knowledge persistence across session boundaries via file-based state | swap by editing `references/patterns.md` §memory-durability |
| Scale modes (light/standard/heavy) | project-studio native | native | `references/scale-modes.md` | self-modify |
| Parent/module matrix architecture | project-studio native | native | Multi-module parent, shared/ split, inbox/outbox/bus, classifier | self-modify |
| Module resume auto-detection | project-studio native | native | `module-seed.yaml` triggers Module Resume Mode | self-modify |
| Conflict resolution 6-option card | project-studio native | native | `references/conflict-resolution.md` | self-modify |
| Codebase classifier (4-tier, 8-heuristic) | project-studio native | native | `references/classifier-rules.md` | self-modify |
| Heavy code-structure mapping | `graphify` | direct-skill | On-demand spawn in code-heavy specialists; scoped per call | swap by editing Invariant #19 and `references/invokable-skills.md` |
| Team builder + workflow baseline | `gstack-team` plugin | direct-plugin | Propose-then-yes, critique-before-implement, retro cadence | swap by editing `references/gstack-integration.md` |
| Plan-critique (strategy lens) | `gstack-team:plan-ceo-review` | direct-skill | Tier-1 lens 1; runs before implementation | swap by editing `references/gstack-integration.md` §plan-critique |
| Plan-critique (engineering lens) | `gstack-team:plan-eng-review` | direct-skill | Tier-1 lens 2 | swap by editing `references/gstack-integration.md` §plan-critique |
| Plan-critique (design lens) | `gstack-team:plan-design-review` | direct-skill | Tier-1 lens 3 | swap by editing `references/gstack-integration.md` §plan-critique |
| Plan-critique (developer-experience lens) | `gstack-team:plan-devex-review` | direct-skill | Tier-1 lens 4; may skip if no dev-facing surface | swap by editing `references/gstack-integration.md` §plan-critique |
| End-to-end feature planning | `gstack-team:autoplan` | direct-skill | Intake → CEO review → implementation plan | swap by editing `references/gstack-integration.md` |
| Idea interrogation / office hours | `gstack-team:office-hours` | direct-skill | YC-style product challenge before a plan exists | swap by editing `references/gstack-integration.md` |
| Code review | `gstack-team:review` | direct-skill | Scope drift detection, production-risk checks | swap by editing `references/gstack-integration.md` |
| Security audit | `gstack-team:cso` | direct-skill | OWASP Top 10 + STRIDE | swap by editing `references/gstack-integration.md` |
| Root-cause investigation | `gstack-team:investigate` | direct-skill | Phase 1/2/3 root-cause methodology | swap by editing `references/gstack-integration.md` |
| Browser QA | `gstack-team:qa` | direct-skill | Uses Claude-in-Chrome MCP for live-URL testing | swap by editing `references/gstack-integration.md` |
| Visual design review | `gstack-team:design-review` | direct-skill | AI-design-slop check on deployed sites | swap by editing `references/gstack-integration.md` |
| Milestone retrospective | `gstack-team:retro` | direct-skill | Structured look-back; supersedes weekly cadence | swap by editing `references/gstack-integration.md` §retro-format |
| Careful-mode escalation | `gstack-team:careful` | direct-skill | Default critique stance for production-critical changes | swap by editing `references/gstack-integration.md` §careful-mode |
| Session context save | `gstack-team:context-save` | direct-skill | Snapshot into `.cowork/context/` on session wind-down | swap by editing `references/gstack-integration.md` §context-save |
| Session context restore | `gstack-team:context-restore` | direct-skill | Load most-recent snapshot on boot | swap by editing `references/gstack-integration.md` §context-save |
| Freeze / guard / unfreeze | `gstack-team:freeze`, `:guard`, `:unfreeze` | direct-skill | Path-level write protection; respects parent/module boundary (Invariant #26) | swap by editing `references/gstack-integration.md` §freeze-scope |
| Pre-merge ship sequence | `gstack-team:ship` | direct-skill | Tests + CEO review + CHANGELOG + deploy preview | swap by editing `references/gstack-integration.md` |
| Land-and-deploy to production | `gstack-team:land-and-deploy` | direct-skill | Post-approval merge + Vercel deploy + live-URL verify | swap by editing `references/gstack-integration.md` |
| Canary / progressive rollout | `gstack-team:canary` | direct-skill | Traffic shifting, auto-rollback on anomalies | swap by editing `references/gstack-integration.md` |
| PDF export | `gstack-team:make-pdf` | direct-skill | Default format for user-facing deliverables (Invariant #24) | swap by editing `references/gstack-integration.md` §pdf-default |
| Teach-first walkthrough | `gstack-team:learn` | direct-skill | Learning mode for unfamiliar codebases | swap by editing `references/gstack-integration.md` |
| Folder convention (durable vs ephemeral) | gstack-team `.cowork/` pattern | pattern-absorbed | `.cowork/` for ephemera (freeze, snapshots, log tail); `project-studio/` for durable methodology, team, roadmap, retros. Symmetrical at parent and module levels. | swap by editing `references/parent-architecture.md` |
| Shared-file write safety | gstack-team atomic-write pattern | pattern-absorbed | Write-temp-then-rename for all shared parent files (`shared/bus.md`, `shared/<module>-outbox.md`) to prevent corruption from concurrent module writes | swap by editing `references/parent-architecture.md` |
| Export path convention | project-studio native (derived from gstack-team `.cowork/` precedent) | native | `project-studio/exports/<YYYY-MM-DD>-<slug>.<ext>` for make-pdf outputs and other user-facing deliverables. Parent and module each have their own `exports/` | self-modify |

## Connector severity matrix

| Connector | Severity | Rationale | Absence behavior |
|---|---|---|---|
| workspace bash | critical | File I/O backbone; every write goes through it | Project Studio does not boot |
| `gstack-team` plugin | critical | Backs plan-critique, retros, deploy, PDF, freeze, context save/restore | Degraded mode — see `references/gstack-integration.md` §degraded-mode |
| `graphify` | recommended | Heavy code-structure mapping for code-heavy specialist spawns | CoS annotates "structure confidence: low" on structural claims |
| Claude-in-Chrome MCP | recommended | Browser QA and visual design review on deployed URLs | `gstack-team:qa` and `:design-review` unavailable; specialists told up front |
| Vercel MCP | optional | Deploy pipeline + build logs + runtime logs | `gstack-team:ship`/`:canary`/`:land-and-deploy` fall back to bash git + manual deploy trigger |

## §update-procedure

Whenever a capability is added, swapped, or retired, CoS:

1. Edits this file (`references/feature-provenance.md`) — add/modify/remove the row.
2. Regenerates the PDF via `gstack-team:make-pdf` into `project-studio/exports/<YYYY-MM-DD>-feature-provenance-manifest.pdf`.
3. Logs the change in `project-studio/log/<today>.md` with a `PROVENANCE-UPDATE:` prefix.
4. If the change affects an Invariant, also updates `protocol/invariants.md`.

The regenerated PDF is the user-facing version. The markdown is CoS's working copy.

## Provenance rules of thumb

- A capability that cannot answer "where did this come from?" in one sentence is not ready to be cataloged. Defer the add until the answer is clear.
- Pattern-absorbed capabilities should name the specific source (e.g., "gstack-team `.cowork/` pattern", not "gstack-team"). This keeps the absorption auditable.
- Direct-skill capabilities should always use the fully qualified namespace (`gstack-team:<skill>`). No bare references.
- Native capabilities' swap path is "self-modify" — there is nothing external to swap.

## Related

- `protocol/invariants.md` §28 — the invariant that enforces this file
- `references/gstack-integration.md` — per-skill runtime details
- `references/connectors.md` — severity-tier mechanics
- `references/monorepo-pattern.md` — how natively monorepo-aware features interact with gstack-team's single-folder assumptions
