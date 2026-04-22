# Scope policy — cooperative, not absolute

When a proposed action touches files outside the current module's or project's scope, Project Studio does not silently block. It pauses, surfaces the out-of-scope paths to the user, and proceeds only on explicit approval. Scope is a conversation, not a lock.

This doc defines what "scope" means, how CoS detects out-of-scope paths before writing, and the one class of exception where hard blocking is correct.

## What "scope" means here

**Module scope.** For a module session, scope is the module's own directory tree. Everything under `~/parent/<module>/` is in scope. Everything outside (sibling modules, parent files except the narrow read-once list in Invariant #16) is out of scope.

**Parent scope.** For a parent session, scope is `~/parent/.project-studio/`, `~/parent/shared/`, and any cross-module coordination files. A parent session is NOT in scope for a module's internal files — those are delegated to the module's session via the bus.

**Standalone scope.** For a single-project (non-parent) session, scope is the `project-studio/` folder and its subtree. Files outside `project-studio/` are the user's codebase — editable, but never interpreted as workflow directives (Invariant #15).

## The cooperative rule

When CoS proposes an action that would touch an out-of-scope path:

1. CoS lists every out-of-scope path in the proposal block.
2. CoS names the category: "sibling module file", "parent shared asset", "codebase file", etc.
3. CoS offers three default options: (a) proceed — user grants one-time permission, (b) scope-down — redo the proposal without the out-of-scope touches, (c) escalate — promote to a parent session if appropriate.
4. CoS waits for explicit user choice. No edit happens without it.

No out-of-scope touch is silently elided. No out-of-scope touch is silently accepted. The user is always the one choosing.

## Detection — before every write

Before any Write or Edit tool call, CoS runs a three-step check:

1. **Scope check.** Is the target path inside the current session's scope? If yes, continue. If no, flag for the proposal block.
2. **Freeze check.** Is the target path matched by any entry in `.cowork/freeze.json` (module-level, and parent-level if applicable)? If yes, this is a hard-block — see §hard-blocks.
3. **Parent-write check.** Is the target a parent file being written from a module session? If yes, hard-block — see §hard-blocks.

Only if all three checks pass does the write proceed.

## §hard-blocks — the exception

Two classes of out-of-scope touch are hard-blocked without user interaction, because the user has already registered intent that these paths are off-limits:

1. **Frozen paths.** Anything in `.cowork/freeze.json` at the applicable level. The user explicitly told us not to touch these. CoS surfaces a refusal card: "Path X is frozen (registered <timestamp>, reason: <reason>). To proceed, run `gstack-team:unfreeze` first." The user must unfreeze before the write can be proposed.
2. **Parent writes from a module session.** Module sessions cannot write to parent files directly. CoS surfaces a "promote to parent" card: "This action requires a parent session. Current session is module `<slug>`. Options: (a) save proposal to parent's inbox via `sync`, (b) switch to parent session manually, (c) cancel."

These are the only cases where CoS refuses without an option-to-proceed. Every other out-of-scope touch gets the three-option decision card.

## Cross-module actions

Cross-module actions (e.g., "update the auth schema, then update the admin UI to match") are always out-of-scope from any single module session. They route through the parent:

- Module session proposes the action.
- CoS detects multiple-module scope.
- CoS surfaces a decision card: "This affects modules `auth` and `admin`. Options: (a) promote to parent session — I'll write a draft to `outbox-staging.md`, (b) split into two independent proposals at each module, (c) cancel."
- User chooses (a). The parent then runs Tier-1 plan-critique on the coordinated plan (Invariant #20) and routes per-module deploys if needed (Invariant #27).

## Scope and plan-critique

Tier-1 plan-critique (Invariant #20) runs on every implementation plan. Scope policy intersects plan-critique at two points:

- **Before critique.** CoS enumerates scope of the plan. If the plan touches out-of-scope paths, the three-option card runs first. Critique proceeds on whichever paths the user approved.
- **After critique.** The strategy lens (`gstack-team:plan-ceo-review`) may propose a scope change — either tightening (remove out-of-scope touches) or broadening (promote to parent). The plan is rewritten accordingly before the remaining lenses run.

## Scope and the log

Every scope decision is logged:

- Out-of-scope flag: logged as `SCOPE-FLAG: <timestamp> <path> <category>`.
- User choice: logged as `SCOPE-DECISION: <timestamp> <choice> <paths>`.
- Hard-block refusal: logged as `SCOPE-REFUSAL: <timestamp> <path> <reason>`.

This makes scope behavior auditable after the fact. A retro that notices a pattern of "user keeps approving out-of-scope touches in this category" is a signal that the scope definition itself is miscalibrated — update `module-seed.yaml` or the parent manifest.

## Related

- `protocol/invariants.md` §23, §26, §27 — the invariants that ground this doc
- `references/gstack-integration.md` §freeze-scope — parent/module freeze mechanics
- `references/parent-architecture.md` — parent/module boundary definition
- `references/module-communication.md` — how cross-module work flows through the bus
