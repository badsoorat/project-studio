# Parent Architecture — Hub-and-Spoke Multi-Module Projects

When a product has multiple modules (website, API, mobile app, admin panel, etc.), each module is a separate Project Studio project in its own subfolder under a shared parent directory. The parent directory provides a coordination layer — a data manifest, shared asset store, and cross-module communication channel — while each module works in isolation.

> **v2.4 update — matrix teams, module seeds, communication layer.** This file describes the core parent↔module architecture. Several sub-systems have been factored into companion files:
>
> - **`references/parent-module-handoff.md`** — module-seed files, the auto-trigger resume mode, shared-assets access via relative paths, the two distinct `shared/` folders, and the parent↔module boundary invariants.
> - **`references/module-communication.md`** — inbox/outbox/bus message model, the sync command, auto-draft gates, chattiness modes, and retention/rotation.
> - **`references/conflict-resolution.md`** — the 6-option decision card for persona, shared-asset, and roadmap-rollup conflicts, plus override/promote/fork flows.
> - **`references/classifier-rules.md`** — the 4-tier, 8-heuristic classifier used in Step 2.5 when an existing tree is being adopted into a parent.
> - **`references/persona-schema.md` §scope** — the `scope: parent | shared | module:<slug>` field and the per-module override schema.
>
> The folder layout below shows the v2.4 structure with two distinct `shared/` folders: `<parent>/shared/` for the communication layer (bus.md + outboxes) and `<parent>/.project-studio/shared/` for parent-level state (brief, roadmap, brand, docs, conventions, data). Read `references/parent-module-handoff.md` for the complete layout and rationale.

---

## Core Principles (v2.4)

1. **Parent holds data and shared state, not workflow instructions.** The parent has a data-only CLAUDE.md manifest, a `.project-studio/shared/` folder with shared assets (brief, roadmap, brand, docs, conventions, data), a `.project-studio/team/` folder for parent- and shared-scope personas, and a `shared/` folder that carries the communication layer (bus.md + per-module outboxes). No protocol files, no registers, no logs live at the parent level — those remain per-module.
2. **Matrix team model.** Personas have a `scope` field (`parent`, `shared`, or `module:<slug>`). Parent-scope personas can only be spawned from a parent session. Shared-scope personas can be spawned from any module session, with per-module overrides. Module-scope personas live inside the module folder. See `references/persona-schema.md` §scope.
3. **Shared assets are referenced, not copied.** Each module references parent shared assets via relative paths captured in `project-studio/shared/shared-index.md`. A logo file lives once at the parent and is read by any module that needs it. See `references/parent-module-handoff.md` §shared-assets-access.
4. **Cross-module communication flows through messages.** Modules never read into sibling folders. Instead, each module has an inbox, an outbox-staging file, and a per-module parent outbox; a `bus.md` at the parent archives every routed message. See `references/module-communication.md`.
5. **Module resume is auto-triggered.** When a Cowork session opens at a module folder, CoS detects `project-studio/module-seed.yaml` and drops straight into Module Resume Mode instead of re-running the setup wizard. See `references/parent-module-handoff.md` §module-resume-mode and `references/setup-flow.md` §Step 0 / §Step 8.
6. **Conflicts are surfaced, never auto-resolved.** Divergences between shared and local state produce a 6-option decision card. See `references/conflict-resolution.md`.
7. **Platform matters.** In Cowork, the user mounts one folder at a time; the full parent↔module file system is only available when the parent is mounted. Module-only mounts fall back to imports-based context sharing. In Claude Code CLI, the full architecture works without restriction.

---

## §platform-limitations — Platform Limitations

**Cowork mode:** In Cowork, the user mounts ONE folder. Access to `../` (parent directory) and sibling module folders is NOT available. The parent architecture's live update protocol (reading `../CLAUDE.md` and `../shared/`) cannot function as designed. For Cowork users:
- Use `project-studio/imports/` (read-only context slices) to exchange context between modules manually.
- The user copies update notification content between sessions by hand.
- The full parent architecture works as designed in **Claude Code CLI**, where file system access is unrestricted.

**Claude Code CLI:** Full parent architecture works as designed. No limitations.

---

## Folder Structure (v2.4)

```
~/parent/
├── CLAUDE.md                                  ← Data-only manifest (NO instructions)
│
├── shared/                                    ← COMMUNICATION LAYER
│   ├── bus.md                                 ← routed-message archive
│   ├── bus-routing.log                        ← append-only routing log
│   ├── auth-outbox.md                         ← auth module's outgoing queue
│   ├── payments-outbox.md
│   ├── admin-outbox.md
│   └── auth-outbox-sent.md                    ← sent-message archives (rotated)
│
├── .project-studio/                           ← PARENT-LEVEL STATE (dot-hidden)
│   ├── shared/                                ← shared assets (referenced, not copied)
│   │   ├── brief.md                           ← product-wide brief
│   │   ├── roadmap.md                         ← Tier 1 parent milestones
│   │   ├── brand/                             ← logos, icons, fonts
│   │   ├── docs/                              ← architecture, API, glossary
│   │   ├── conventions/                       ← code style, naming
│   │   ├── data/                              ← reference datasets
│   │   └── index-updated-at                   ← one-line ISO timestamp
│   ├── team/                                  ← parent- and shared-scope personas
│   │   ├── chief-of-staff.md                  ← parent CoS (scope: parent)
│   │   ├── product-lead.md                    ← scope: parent (optional)
│   │   └── design-lead.md                     ← scope: shared
│   ├── protocol/                              ← parent session boot/resume
│   ├── decisions/                             ← parent-scope ADRs
│   ├── archive/                               ← read-sealed rotation targets
│   ├── inbox.md                               ← parent session's inbox
│   └── sort-log-*.md                          ← Step 2.5 audit logs
│
├── auth/                                      ← Module folder
│   ├── CLAUDE.md                              ← module source of truth
│   ├── START-HERE.md                          ← human-readable handoff
│   ├── project-studio/
│   │   ├── module-seed.yaml                   ← the seed (auto-triggers Module Resume)
│   │   ├── shared/
│   │   │   ├── shared-index.md                ← index of parent shared assets (relative paths)
│   │   │   └── bus-snapshot.md                ← optional local view of recent bus entries
│   │   ├── inbox.md                           ← received messages
│   │   ├── outbox-staging.md                  ← local draft queue
│   │   ├── team/                              ← module-scope personas
│   │   │   ├── eng-lead.md                    ← scope: module:auth
│   │   │   └── persona-overrides.yaml         ← patches for shared personas
│   │   ├── project/
│   │   │   ├── brief.md                       ← module-specific brief
│   │   │   └── roadmap.md                     ← Tier 2 module milestones
│   │   ├── protocol/
│   │   ├── registers/
│   │   ├── decisions/
│   │   ├── log/
│   │   ├── imports/
│   │   │   └── legacy/                        ← Tier 1 classification output (Step 2.5)
│   │   └── archive/
│   └── src/                                   ← module codebase
│
├── payments/
│   └── (same structure as auth)
│
└── admin/
    └── (same structure as auth)
```

### Two distinct `shared/` folders

There are **two folders named `shared/`** in the parent and they do different jobs. Do not conflate them.

1. **`<parent>/shared/`** — **Communication layer.** Contains only `bus.md`, `bus-routing.log`, one `<module-slug>-outbox.md` per module, and sent-message archives. Append-heavy, rotated every 30 days. Managed by the sync command.

2. **`<parent>/.project-studio/shared/`** — **Parent-level state and assets.** Contains the product-wide brief, Tier 1 roadmap, brand assets, shared docs, conventions, data, and the index timestamp. Durable, rarely rotates. Read-only from module sessions.

See `references/parent-module-handoff.md` §layout-rules for the full rationale.

---

## Parent CLAUDE.md — Template

The parent CLAUDE.md is pure data. No workflow instructions, no behavioral rules, no protocol references.

```markdown
# [Product Name]

> Multi-module product managed by Project Studio. Each module is a separate project.
> This file is a data manifest — not a workflow config.

## Modules

| Module | Folder | Description | Status | Last updated |
|--------|--------|-------------|--------|-------------|
| Website | Module1/ | Customer-facing marketing site | Active | 2026-04-06 |
| API | Module2/ | REST API for all clients | Active | 2026-04-05 |
| Mobile App | Module3/ | iOS/Android app | Paused | 2026-03-28 |

## Cross-module communication

Modules communicate via inbox/outbox/bus messaging routed by the `sync` command. **Communication layer** lives at `shared/` (parent level): `bus.md` (routed-message archive), `bus-routing.log` (append-only routing log), and per-module outboxes `<module-slug>-outbox.md`. **Module side:** each module has `project-studio/inbox.md` (received messages) and `project-studio/outbox-staging.md` (local draft queue). See each module's `project-studio/references/module-communication.md` for the full protocol.

## Rules for Claude

If you are Claude reading this file:
- You are working on ONE module at a time. Check the module's own CLAUDE.md for instructions.
- You may read this file, `shared/bus.md`, and `shared/<module-slug>-outbox.md` ONLY during the resume security check (session start) or when running a `sync` command.
- You may NEVER read sibling module folders. Module1's CoS cannot read Module2/ or Module3/.
- You may NEVER write to this file or `shared/` without explicit user permission.
- After the resume security check, work ENTIRELY inside the module folder for the rest of the session.
```

**Note:** The "Rules for Claude" section is the ONE exception to "no instructions in parent." These are isolation rules, not workflow rules. They prevent cross-module contamination (see Invariant #16 in `protocol/invariants.md` for the canonical statement). They are reinforced in each module's CLAUDE.md and boot.md.

---

## Resume Security Check Flow

When a user starts a session in a multi-module project:

### Step 1: Read parent manifest
CoS reads `~/parent/CLAUDE.md`. Identifies module list and last-updated timestamps.

### Step 2: Check inbox for unread messages
CoS reads `project-studio/inbox.md`. Checks the `## Unread` section for messages delivered since last session.

- **If inbox has NO unread messages →** Stop reading parent. Drop straight into module's own resume protocol. Zero additional parent reads.
- **If unread messages exist →** Proceed to Step 3.

### Step 3: Present inbox messages
CoS shows unread messages grouped by sender:

*"You have unread messages from sibling modules:*
- *auth → decision: "switched password hashing to argon2" (2h ago)*
- *payments → question: "should we unify the billing webhook?" (yesterday)*
- *parent → milestone: "Tier 1 milestone 'Auth done' is 80%" (3d ago)*

*Want me to walk through them?"*

Don't block resume on these — they're informational. The user decides what to act on.

### Step 4: Flush any pending outbox drafts
Check `project-studio/outbox-staging.md` for drafted messages that were never flushed. If any exist, ask: *"You have N unsent draft messages in outbox staging. Want me to flush them to the parent outbox now, or keep them as drafts?"*

- **If flush →** Write each message to `../shared/<this-module-slug>-outbox.md` and clear staging file. Full sync (routing into sibling inboxes) requires running `sync` from a parent session.
- **If keep →** Leave drafts in staging. Note in log.

### Step 5: Stop reading parent
All parent access is done. CoS works entirely inside the module folder for the rest of the session. The normal module resume protocol continues from here.

---

## Logging Updates to Parent — Outbox Flow

Updates to the parent are NEVER automatic. The flow:

### Trigger
User explicitly says "log updates to parent" or "push updates" or similar. CoS may also suggest it at session end: *"You changed the auth provider this session. This affects shared infrastructure. Want to draft a message for sibling modules?"* User decides.

### Step 1: Draft message to outbox staging
CoS compiles a structured message (see `references/module-communication.md` §message-format). Writes to `project-studio/outbox-staging.md`.

### Step 2: Ask permission to flush
CoS shows the user exactly what will be sent:

*"I've drafted a message to outbox staging. Here's the content:*

*(shows message)*

*Flush to parent outbox now?"*

### Step 3: Flush on approval
- Write message to `../shared/<module-slug>-outbox.md`
- Clear the entry from `project-studio/outbox-staging.md`
- Note: routing from outboxes to sibling inboxes requires running `sync` from a parent session

### Step 4: Close parent access
Done writing. Back to local-only.

---

## Initial Population — New Module Setup

When a NEW module is being set up and other modules already exist:

### One-time cross-module read
During setup (and ONLY during setup), CoS reads an existing module's `project-studio/shared/` to copy the current shared context. This is a one-time controlled read — not a per-session event.

1. CoS identifies which existing module has the most complete shared context (usually the first one set up).
2. Asks user: *"Module1 has shared infrastructure, design system, and product brief. Want me to copy these as your starting point?"*
3. On approval, reads the source module's `project-studio/shared/` files.
4. Writes copies to the new module's `project-studio/shared/`.
5. Sets `last-sync-timestamp` to now.

After setup, the isolation rule kicks in: no more cross-module reads during normal work sessions.

### First module (no siblings)
If this is the first module, CoS populates `project-studio/shared/` from the setup wizard's Step 2 scenario-branch context gathering (for Scenario B this is 2B.1-2B.4; for D1 this is 2D1.1-2D1.3; for D2 this is 2D2.1-2D2.6). The parent manifest is created at this point too.

---

## Monorepo Edge Case

For monorepos (`packages/frontend`, `packages/api`, `packages/shared` in one git repo):

- Mount the monorepo root as a single Project Studio project.
- Treat the monorepo as one "module" — the whole thing is one project.
- Use `project/infrastructure/` to track which packages exist and their relationships.
- Do NOT try to split a monorepo into separate Project Studio projects — they share `.git/`, `package.json` (root), CI/CD, and often dependencies.

This is a documented limitation, not a bug. Monorepo-specific features are a future concern.

---

## .gitignore for Parent

During parent folder creation, CoS adds to the parent `.gitignore`:

```
# Project Studio management files (per-module)
*/project-studio/
shared/
```

This prevents all Project Studio files AND update notifications from being committed. The parent CLAUDE.md is intentionally NOT in .gitignore — the user may want to commit the product manifest. User can add it manually if they prefer.

---

## What Does NOT Go in the Parent (v2.4)

- No per-module registers (assumptions, risks, blockers — stay per-module).
- No per-module logs, checkpoints, or retros.
- No per-module imports (each module has its own `imports/` folder).
- No workflow instructions in `CLAUDE.md` — the parent manifest is data-only. The only exception is the isolation rules under "Rules for Claude", which are hard safety rails.
- No codebase files at the parent root unless the parent has its own shared codebase (rare — usually the parent is just a coordination folder).

## What DOES Go in the Parent (v2.4)

- A data-only `CLAUDE.md` manifest listing modules, communication paths, and shared asset locations.
- `shared/` — the communication layer (bus + per-module outboxes).
- `.project-studio/shared/` — durable parent-level state and assets (brief, roadmap, brand, docs, conventions, data).
- `.project-studio/team/` — parent- and shared-scoped personas (chief-of-staff, product-lead, design-lead). Module-scoped personas live inside each module's own `project-studio/team/`; shared personas can be patched via each module's `persona-overrides.yaml`.
- `.project-studio/protocol/` — parent session's boot and resume protocol.
- `.project-studio/decisions/` — parent-scope ADRs (decisions that affect the whole product, not one module).
- `.project-studio/archive/` — read-sealed rotation targets for old bus slices and outbox archives.
- `.project-studio/inbox.md` — parent session's inbox for