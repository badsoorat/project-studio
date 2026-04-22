# Monorepo pattern — parent + modules

Project Studio's parent/module architecture is native. gstack-team has no monorepo concept of its own — every gstack-team skill runs at a single mounted folder. This doc explains how Project Studio extends the parent/module architecture to host gstack-team skills correctly, and where the two models interact.

## The one-sentence summary

Project Studio provides the monorepo skeleton (parent + modules, bus routing, shared-asset references); gstack-team runs per-context inside that skeleton, with each module treated as a standalone gstack-team target.

## What Project Studio owns (native)

- Parent directory layout (`~/parent/`, `shared/`, `.project-studio/`, per-module folders)
- Matrix team of personas (parent/shared/module scope)
- Module seed auto-detection (`project-studio/module-seed.yaml` triggers Module Resume Mode)
- Inbox / outbox / bus messaging
- Shared-asset references (no duplication; relative paths only)
- Roadmap rollup (parent Tier-1 milestones, module Tier-2 milestones)
- Conflict resolution (6-option decision card)
- Classifier (4-tier, 8-heuristic walk for adopting an existing tree)

These are Project Studio's invention and they stay that way. gstack-team has no equivalent.

## What gstack-team owns (direct-dependency)

- Plan-critique lenses (ceo, eng, design, devex)
- Code review, security audit, investigation
- Browser QA and visual design review
- Deploy pipeline (ship, canary, land-and-deploy)
- Retrospective format
- PDF export
- Context save/restore
- Freeze/guard/unfreeze

Each of these runs at a single mounted folder. Project Studio's job is to pick the right folder to run them at, and to coordinate across modules when the work spans more than one.

## Three narrow patterns Project Studio borrows from gstack-team

Not wholesale absorption — three discrete improvements.

### §ephemera-split — 1. `.cowork/` for ephemeral state

gstack-team uses `.cowork/` for session-ephemeral state — freeze rules, context snapshots, log tails. Project Studio adopts the same pattern at both levels:

- Parent: `~/parent/.cowork/` holds parent-session freeze, context snapshots, and routing log tails.
- Module: `~/parent/<module>/.cowork/` holds module-session freeze, context snapshots, and log tails.

This is purely for ephemera. Durable methodology — briefs, roadmaps, retros, personas, registers, decisions — stays in `project-studio/` (module) or `.project-studio/` (parent).

The split matters because `.cowork/` can be safely gitignored or wiped between sessions; `project-studio/` is the project's memory and must survive.

### §atomic-writes — 2. Atomic-write discipline for shared parent files

gstack-team uses write-temp-then-rename for anything that multiple sessions could touch simultaneously. Project Studio adopts the same discipline for shared parent files that multiple modules can write to:

- `~/parent/shared/bus.md`
- `~/parent/shared/<module-slug>-outbox.md`
- `~/parent/.project-studio/shared/*` when updated via bus

Pattern (bash):

```bash
# Atomic write: temp file, fsync-equivalent, rename
TMP=$(mktemp "${TARGET}.XXXXXX")
cat > "$TMP" <<EOF
... new content ...
EOF
mv "$TMP" "$TARGET"
```

Pattern (Write tool): always include a nonce in a tempfile name via bash first, then use Write tool on the final path after bash confirms no concurrent edit arrived.

For files only one session writes (a module's own `project-studio/team/eng-lead.md`), atomic writes are unnecessary — plain Write tool is fine.

### 3. Standardized exports path

gstack-team's `make-pdf` produces user-facing deliverables. Project Studio gives these a consistent home:

- Parent: `~/parent/.project-studio/exports/<YYYY-MM-DD>-<slug>.<ext>`
- Module: `~/parent/<module>/project-studio/exports/<YYYY-MM-DD>-<slug>.<ext>`

The date prefix keeps exports ordered chronologically. The slug is a short kebab-case descriptor of what the deliverable is (e.g., `q2-roadmap`, `milestone-3-retro`, `security-audit-auth`). Exports are gitignored by default — the markdown source is the durable record.

## How gstack-team skills map onto the parent/module architecture

| gstack-team skill | Runs at | Scope |
|---|---|---|
| `gstack-team:plan-*-review` | The session that owns the plan | If plan is module-scoped → module session. If parent-scoped → parent session (then per-module for the engineering lens on each affected module) |
| `gstack-team:autoplan` | The session that will own the implementation | Module session for module plans; parent session for cross-module plans |
| `gstack-team:review` | Module session | Module-scoped branch/diff |
| `gstack-team:cso` | Module session | Module-scoped; parent session can run it for parent-level code if any |
| `gstack-team:investigate` | Wherever the error surfaced | Can hop via bus messages to pull module-specific evidence |
| `gstack-team:qa` / `gstack-team:design-review` | Module session (for a module's live URL) or parent session (for an aggregated dashboard) | URL-bound, not folder-bound |
| `gstack-team:retro` | Milestone owner's session | Module session for module milestones; parent session for parent milestones |
| `gstack-team:context-save` / `gstack-team:context-restore` | Every session, both levels | Writes to local `.cowork/context/` |
| `gstack-team:freeze` / `gstack-team:guard` / `gstack-team:unfreeze` | Session that owns the paths | Module-level for module paths; parent-level for parent paths. See Invariant #26 |
| `gstack-team:ship` / `gstack-team:land-and-deploy` / `gstack-team:canary` | Module session | Single-module only. Cross-module coordination via parent — Invariant #27 |
| `gstack-team:make-pdf` | The session producing the deliverable | Writes to local `exports/` |

## Cross-module coordination — the rule

Whenever a gstack-team action would affect more than one module, it must be driven from the parent session. The parent:

1. Authors the coordinated plan (`gstack-team:autoplan` at parent scope).
2. Runs Tier-1 plan-critique at parent scope.
3. Dispatches per-module work via bus messages (`project-studio/inbox.md` for each affected module).
4. Each module session picks up its inbox message, runs its local plan-critique for its slice (engineering lens at minimum), executes, and replies via outbox.
5. Parent aggregates outcomes, runs a parent-scope retro if the work was milestone-sized.

Single-module actions never involve the parent. A bug in one module's auth code gets `gstack-team:investigate` at that module's session — nothing else needed.

## Auto-identification — parent vs module vs standalone

CoS identifies the context at boot by looking at the mounted folder:

- **Parent**: folder contains `shared/bus.md` AND `.project-studio/` AND at least one sibling folder that contains `project-studio/module-seed.yaml`. CoS reads `.project-studio/protocol/boot.md`.
- **Module**: folder contains `project-studio/module-seed.yaml` AND parent (`../`) contains `shared/bus.md`. CoS enters Module Resume Mode per `references/parent-module-handoff.md`. If `../` is not accessible (Cowork mode mounted at module only), CoS enters module-local fallback.
- **Standalone**: folder contains `project-studio/` but no `module-seed.yaml` and no parent with `shared/bus.md`. CoS reads `project-studio/protocol/boot.md`.

The detection logic is deterministic. There is no user prompt for "is this a parent or a module?" — the folder layout answers it.

## The parent's `project-studio/` vs `.project-studio/` distinction

For historical continuity, Project Studio keeps parent-level state in `.project-studio/` (dot-hidden) while module state lives in `project-studio/` (visible). The rationale:

- Modules have their own codebase at the module root. `project-studio/` sits beside `src/`. Dot-hiding it would be unhelpful — users expect to see the management layer.
- Parents typically do NOT have their own codebase at the parent root — they're orchestration containers. Dot-hiding `.project-studio/` keeps the parent root clean for the user to see just module folders and the `shared/` communication layer.

This is a naming convention, not a different architecture. Contents and rules are identical.

## Related

- `references/parent-architecture.md` — full parent/module architecture (native Project Studio)
- `references/parent-module-handoff.md` — module resume mode, shared-asset access
- `references/module-communication.md` — bus, inbox, outbox mechanics
- `references/gstack-integration.md` — per-skill runtime wiring
- `references/scope-policy.md` — cooperative out-of-scope handling
- `references/feature-provenan