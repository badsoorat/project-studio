# Conflict Resolution — Shared vs Module Ownership

How Project Studio handles situations where a shared artefact (persona, roadmap milestone, brand asset, doc, convention) is being modified, duplicated, or contested across modules. The goal is to keep shared state coherent without freezing it.

Covers three conflict categories: **persona ownership**, **shared-asset edits**, and **roadmap rollup disputes**. Each has a 6-option decision card that CoS uses to make the conflict visible and the resolution explicit.

This file is the companion to `references/persona-schema.md` (scope field and override model), `references/parent-module-handoff.md` (shared-assets access rules), and `references/setup-flow.md` §Step 3m (matrix team setup) and §Step 4t (two-tier roadmap).

---

## The core tension

Shared artefacts exist because duplication is worse than coordination. One logo, one product brief, one Senior PM persona — each is defined once at the parent and referenced by every module. The tension is that modules have legitimate, divergent needs:

- Auth module needs a stricter code-style than the default convention.
- Payments module needs a variant of the Senior PM persona that understands PCI-DSS deeply.
- The admin module wants to reschedule a Tier 1 parent milestone because its local dependencies slipped.

If every divergence promoted to the parent, the parent would bloat. If every divergence forked into a local-only override, shared state would fragment. The resolution flow exists to make the trade-off visible.

---

## General rules

1. **Conflicts are surfaced, not auto-resolved.** CoS never silently promotes, demotes, or edits shared state. Every conflict gets a decision card.
2. **Shared state is read-only from modules.** Always. A module session cannot write to `<parent>/.project-studio/shared/` or to any shared persona file. Module sessions write overrides locally; promotion happens from a parent session.
3. **Every resolution is recorded as an ADR.** The decision lives in the module's `decisions/` folder (for module-local resolutions) or in the parent's `.project-studio/decisions/` folder (for parent-level resolutions). Both cases reference each other.
4. **Promotion requires parent-session approval.** A module cannot unilaterally promote its local override to parent shared state. It can *propose* promotion via a `persona-promote` or `shared-update` outbox message; the parent session evaluates and approves.
5. **Demotion is rare.** Demoting a shared artefact back to module-local is almost always a sign that it was incorrectly shared in the first place. Treat demotion as a design-review conversation, not a routine move.

---

## The 6-option decision card

Whenever CoS detects a conflict, it presents the same 6-option card. The options are ordered by escalation — the top option is the lightest-touch, the bottom is the heaviest.

```
Conflict detected: <short description>

Context:
  Shared source:   <path>
  Current module:  <slug>
  Conflict type:   <persona | shared-asset | roadmap-rollup>
  Trigger:         <what just happened>

Options:
  [1] Local override only
      Keep the shared source untouched. Write a module-scoped override
      at <override-path>. Other modules are unaffected.

  [2] Local override + FYI to parent
      Same as [1], plus auto-draft an FYI outbox message to @parent
      so the parent session is aware. No parent action required.

  [3] Propose promotion to shared
      Write a local override AND auto-draft a persona-promote / shared-update
      message to @parent with rationale. Parent session decides whether
      to adopt. Until adopted, the override stays local.

  [4] Request parent-session review
      Do nothing locally. Draft a question-tag message to @parent asking
      for a decision. Staging blocks the conflict until parent replies.

  [5] Fork the shared artefact
      Create a new shared artefact alongside the original (e.g.,
      pm-lead-strict vs pm-lead). Both modules can reference whichever
      fits. Requires parent-session approval to land in shared.

  [6] Revert my change
      Discard the local edit. Shared source stays canonical.
      Useful when the override was accidental or the conflict was
      actually a misunderstanding.

Choose: [1] [2] [3] [4] [5] [6]
```

### Option guidance

| Option | When it's right | When it's wrong |
|---|---|---|
| **[1] Local override** | divergence is truly module-specific and won't affect siblings | you suspect other modules will face the same need soon |
| **[2] Override + FYI** | you're overriding but want the parent to know for eventual consolidation | the override is sensitive and shouldn't be public |
| **[3] Propose promotion** | you believe the change should be the new shared default | the divergence is clearly specific to your module |
| **[4] Parent review** | you need the parent's judgment before acting, and waiting is cheaper than reverting | you need to keep moving locally this session |
| **[5] Fork** | two legitimate, stable variants coexist | the variants are temporary or experimental |
| **[6] Revert** | the change was accidental or based on misreading | the underlying need is real and just needs a different resolution |

---

## §persona-ownership — Conflict category 1: Persona ownership

A persona conflict fires when a module session edits a **shared-scope** persona file or a **parent-scope** persona. Shared personas live at `<parent>/.project-studio/team/<persona>.md` and are referenced from each module via `shared_personas[]` in the module seed.

### Detection triggers

- The module tries to edit `../.project-studio/team/<persona>.md` directly (blocked — always a hard stop).
- The module edits `project-studio/team/persona-overrides.yaml` with a non-trivial change to a shared persona's slice.
- The module's session log records "persona X proposed new principle", "persona X proposed new skill", or "persona X's tone was changed".

### Override model

Module-local overrides to shared personas live in a single YAML file per module: `project-studio/team/persona-overrides.yaml`. The file format:

```yaml
schema_version: 1
overrides:
  - persona: pm-lead
    scope_source: shared
    source_path: "../.project-studio/team/pm-lead.md"
    effective_at: 2026-04-11T14:32:00Z
    reason: "Payments-specific PCI-DSS focus"
    patches:
      principles_add:
        - "PCI-DSS compliance is a non-negotiable constraint, not a checkbox."
      principles_remove: []
      obsession_override: null
      domain_add:
        - "Card tokenisation boundary"
      skill_menu_add:
        - payments-specific-compliance-checklist
      skill_menu_remove: []
      tone_override: null
```

### Patch semantics

- **`principles_add`** — appended to the shared persona's principles list. Capped at 5 total across shared + override.
- **`principles_remove`** — removed from the shared list when applied. Must match exactly.
- **`obsession_override`** — if set, replaces the shared obsession for this module only.
- **`domain_add`** / **`domain_remove`** — edit the domain paragraph by line.
- **`skill_menu_add`** / **`skill_menu_remove`** — edit the skill list. Additions require the same Gate 2 approval as the original persona setup (see `references/setup-flow.md` §Step 3c.5).
- **`tone_override`** — if set, replaces the shared tone for this module only.

### Applying overrides at spawn

When a module session spawns a shared persona as a sub-agent:

1. Read the shared persona file's spawn-context zone (Role through Tone).
2. Read the matching override entry from `persona-overrides.yaml`.
3. Apply patches in the order: domain → principles → obsession → skill_menu → tone.
4. Pass the patched slice into the spawn via `PATTERN:spawn-context-slice`.

Never edit the shared persona file from a module session. Always patch on the way into the spawn.

### Promoting an override

If the user decides the override should become the new shared default, CoS:

1. Auto-drafts a `persona-promote` tagged message to `@parent` with the override YAML inlined and a one-paragraph rationale.
2. Flushes to the parent outbox on approval.
3. On the next sync, the message lands in the parent inbox.
4. In a parent session, CoS reads the message, re-runs Gate 2 (skill approval) for any new skills, and — if approved — edits the shared persona file directly.
5. The parent session sends a `shared-update` message back to all modules noting the new version.
6. Modules delete their override entry on next resume (or keep it intentionally if the patch is subtly different from the promoted version).

### Forking a shared persona

If Option [5] is chosen, CoS at the parent session creates a new shared persona file at `<parent>/.project-studio/team/<persona>-<variant>.md` and updates the module seeds that prefer the variant. The original persona stays unchanged.

Forking is heavier than overriding but lighter than a module-local clone. Use it when two stable variants coexist across the product (e.g., `pm-lead-strict` for regulated modules, `pm-lead` for unregulated).

---

## §shared-asset-edits — Conflict category 2: Shared-asset edits

A shared-asset conflict fires when a module session wants to edit a file under `<parent>/.project-studio/shared/` (brand, docs, data, conventions, brief, roadmap).

### Detection triggers

- The module tries to write to any path beginning with `../.project-studio/shared/` (blocked — always a hard stop).
- The module creates a file at `project-studio/shared/<category>-overrides/<filename>` with the same basename as a shared asset.
- The module's session log records "needs different version of <shared asset>".

### Override model

Shared-asset overrides live per-category under `project-studio/shared/<category>-overrides/`. Example:

```
auth/
└── project-studio/
    └── shared/
        ├── shared-index.md              ← updated to point to override
        ├── brand-overrides/
        │   └── logo-auth.svg            ← local variant
        └── conventions-overrides/
            └── code-style.md            ← local variant
```

The module's `shared-index.md` gets a new entry for each override:

```markdown
## Brand (with overrides)

- **Logo (color)** — `project-studio/shared/brand-overrides/logo-auth.svg`  ← OVERRIDE (was `../.project-studio/shared/brand/logo.svg`)
- **Logo (white)** — `../.project-studio/shared/brand/logo-white.svg`
- **Favicon** — `../.project-studio/shared/brand/favicon.ico`
```

The `← OVERRIDE` marker is mandatory — it keeps the divergence visible whenever the index is read.

### When overriding gets called out

At every module resume (Step 8c), CoS reads `shared-index.md` and notices every `← OVERRIDE` marker. It includes a one-line reminder in the resume summary: *"This module has 2 shared-asset overrides. Consider whether any should be promoted."*

At every parent sync, the sync command scans module shared-indexes (via the parent manifest's pointer — not by walking module folders) and produces a parent-level overrides inventory for the parent session's awareness. See `references/module-communication.md` §sync command step 8 (shared-update broadcasts).

### Promoting a shared-asset override

Similar flow to persona promotion:

1. Auto-draft a `shared-update` message to `@parent` with the override contents attached or referenced.
2. On approval, flush to the parent outbox.
3. In a parent session, CoS evaluates and either:
   - Adopts the override as the new shared default (edits `<parent>/.project-studio/shared/<category>/<file>` and writes a `shared-update` back to all modules).
   - Adopts it as a forked variant under `<parent>/.project-studio/shared/<category>/<variant>/`.
   - Rejects it with a reason; the module keeps the local override indefinitely.

### Revert flow

If Option [6] is chosen, CoS deletes the override file, removes the `← OVERRIDE` marker from the shared-index, and records a one-line revert note in `log/`. No parent message is sent — reverts are module-local cleanup.

---

## Conflict category 3 — Roadmap rollup disputes

A roadmap conflict fires when a module's Tier 2 milestones cannot honour the Tier 1 parent milestone they roll up into. This is the trickiest category because roadmap disputes usually involve multiple modules, not just one.

### Detection triggers

- A Tier 2 milestone is added, removed, or rescheduled AND its `rolls_up_to` field points to a parent milestone whose deadline is earlier than the new Tier 2 deadline.
- A Tier 2 milestone's `dependencies` field names a sibling module's milestone that has slipped.
- The reconciliation pass (Step 4t.4 in `references/setup-flow.md`) flags that a Tier 1 parent milestone has no remaining contributors (all Tier 2 rollups were cancelled).

### Conflict types

**Type A — Module can't meet parent deadline on its own.** Only one module contributes to the affected Tier 1 milestone. The module proposes a new Tier 1 date.

**Type B — Shared dependency slip.** Module A's Tier 2 depends on Module B's Tier 2, and B slipped. A's rollup breaks through no fault of A's own planning.

**Type C — Parent milestone orphaned.** A Tier 2 milestone was cancelled or descoped, leaving no contributors to the Tier 1 it fed. The Tier 1 is now a ghost.

**Type D — Scope mismatch.** Two modules disagree about what a Tier 1 milestone actually means (e.g., "auth v2" means one thing to auth and another to payments).

### Resolution using the 6-option card

- **[1] Local override** — rarely applicable to roadmap; only fits if the Tier 2 slip is genuinely module-local and the Tier 1 still has other contributors.
- **[2] Override + FYI** — log the slip locally, send an FYI to parent. Good for small slips (< 1 week).
- **[3] Propose promotion** — propose updating the Tier 1 parent milestone with a new deadline or scope. Parent session decides.
- **[4] Parent review** — for Type B (dependency slip), ask the parent session to mediate between the two modules. This is the right option when you don't have the full picture.
- **[5] Fork** — split the Tier 1 into two parent milestones (e.g., "auth v2 — session model" and "auth v2 — token model"). Parent session approves the split.
- **[6] Revert** — roll back the Tier 2 change that triggered the conflict. Useful when the change was speculative.

### Type-specific guidance

**Type A** — almost always Option [3]. A single-contributor slip needs a Tier 1 date update.

**Type B** — almost always Option [4]. The module that slipped should send a `blocker` message to its dependents AND to the parent. The dependent modules should send a `question` message asking the parent whether to wait or cut scope. The parent session is the only place with visibility to decide.

**Type C** — Option [3] or [6]. Either propose removing the orphaned Tier 1 (promotion) or revert the Tier 2 cancellation. Never leave ghost Tier 1 milestones in the roadmap — they rot.

**Type D** — Option [4]. Scope mismatch is a *definition* problem, not a *scheduling* problem. The parent session needs to re-run the relevant piece of Step 4t to clarify what the Tier 1 means. Options [1] and [3] are wrong here — they paper over the disagreement instead of surfacing it.

### Roadmap conflict lifecycle

1. Module CoS detects a rollup conflict at the moment a Tier 2 milestone is edited.
2. CoS presents the 6-option card with the conflict type labelled.
3. User picks an option. CoS logs an ADR in `decisions/` with:
   - The trigger event (what Tier 2 edit caused the conflict).
   - The conflict type (A/B/C/D).
   - The chosen option (1-6).
   - Rationale (1-2 sentences).
   - Outcome (what files/messages will be written).
4. If Options [2], [3], or [4] are chosen, an outbox message is auto-drafted per `references/module-communication.md` §auto-draft-gates.
5. If the option requires parent action, the module's roadmap stays in a `pending-parent-review` state locally (the affected milestone gets a `status: pending-review` marker).
6. On next sync, the parent session reviews the message and either approves (propagates changes to Tier 1 roadmap) or rejects (sends a `decision` message back).
7. On next module resume, CoS sees the reply in the inbox and either clears the `pending-parent-review` marker (approved) or re-surfaces the conflict (rejected, needs another option).

---

## Cross-category: the user's role

Conflicts are always user-visible. CoS never picks an option on the user's behalf, even when the "right" option seems obvious. Reasons:

1. **Preserving optionality.** What looks like a clear persona override might be the first sign of a deeper architectural issue that only the user can see.
2. **Accountability.** ADRs with human-chosen options are more useful in retro than AI-chosen ones.
3. **Rate limiting.** Forcing the user to pick slows down the pace of divergence, which is usually a good thing.

CoS can (and should) **recommend** an option based on the heuristics in this file. The recommendation appears above the decision card:

```
Recommendation: [3] Propose promotion — this override has strong signal
it should become the shared default (matches patterns already in
payments module, and aligns with the "security posture" thread in the bus).

[1] [2] [3] [4] [5] [6]
```

The user can still pick anything.

---

## Recording resolutions

Every conflict resolution is an ADR. Minimum ADR content:

```markdown
# ADR-NNN — <short title>

**Date:** YYYY-MM-DD
**Status:** accepted
**Category:** conflict-resolution
**Conflict type:** persona | shared-asset | roadmap-rollup
**Scope:** module | parent

## Context

What happened that triggered this conflict. Include the shared source path,
the module slug, and the edit that caused the conflict.

## Options considered

- [1] Local override
- [2] Override + FYI
- [3] Propose promotion
- [4] Parent review
- [5] Fork
- [6] Revert

## Decision

Option [N] — <one-line summary>.

Rationale:
- <point 1>
- <point 2>

## Consequences

- Files written / edited
- Outbox messages drafted
- Module state changes
- Parent state changes (if any)

## Refs

- `<path to the shared source>`
- `<path to the override or promotion artefact>`
- `<outbox message id if applicable>`
```

Parent-scope ADRs live at `<parent>/.project-studio/decisions/ADR-NNN.md`. Module-scope ADRs live at `<module>/project-studio/decisions/ADR-NNN.md`. Cross-scope conflicts get one ADR on each side that cross-reference each other.

---

## Anti-patterns

- **Silent overrides.** Editing a local shared-asset copy without creating a `← OVERRIDE` marker in the shared-index. The divergence becomes invisible and rots.
- **Unilateral promotion.** A module session writing directly to `<parent>/.project-studio/shared/`. This is an invariant violation and always blocked.
- **Forking without user approval.** Creating a new variant of a shared artefact because "it's just a small variant" without presenting the decision card.
- **Option [4] with no follow-up.** Parking a conflict under parent review and then ignoring the reply. Every `pending-parent-review` milestone/persona/asset should re-surface at each module resume until resolved.
- **ADR-less resolutions.** Resolving a conflict verbally and not recording the decision. A resolution without an ADR is indistinguish