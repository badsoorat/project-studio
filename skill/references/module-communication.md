# Module Communication — Inbox / Outbox / Bus

How sibling modules in a multi-module parent exchange information without ever reading each other's folders. Covers the message format, routing model, sync command, auto-draft gates, chattiness modes, and retention rules.

This file is the companion to `references/parent-module-handoff.md` and to `references/setup-flow.md` §Step 2D2 (sibling sync at setup) and §Step 7f (communication file creation).

---

## Why this exists

Rule 2 of the parent↔module boundary invariants is absolute: **module sessions never read into sibling module folders.** Without a communication channel, modules would either (a) silently drift apart, (b) force the user to shuttle information by hand, or (c) tempt CoS to walk into sibling trees and violate isolation.

The inbox/outbox/bus model gives modules a disciplined way to share what matters (decisions, blockers, handoffs, milestones) without ever reading sibling state. Messages are the only thing that crosses module boundaries. Everything else stays local.

---

## The three file types

Three file types, three locations, three jobs. Keep them straight.

### 1. Module outbox (staging, local)

**Path:** `<module>/project-studio/outbox-staging.md`
**Owned by:** the module session.
**Purpose:** a local draft queue where CoS writes candidate messages during a work session. Nothing here has been sent yet. The user approves messages in staging before they are flushed to the parent outbox.

### 2. Parent outbox (sent queue)

**Path:** `<parent>/shared/<module-slug>-outbox.md`
**Owned by:** the parent communication layer, written by module sessions on flush.
**Purpose:** outgoing messages from a specific module that have been approved by the user but not yet routed. The sync command picks these up, routes them to sibling inboxes, and appends to the bus.

### 3. Module inbox (received)

**Path:** `<module>/project-studio/inbox.md`
**Owned by:** the module session (but written to by the sync command, not by the module's own CoS).
**Purpose:** incoming messages from siblings or the parent. The module's CoS reads the inbox at resume and when the user asks "any news?". Unread messages are summarised at resume.

### §bus-semantics — 4. Parent bus (archive)

**Path:** `<parent>/shared/bus.md`
**Owned by:** the parent communication layer.
**Purpose:** chronological archive of every routed message. This is the single product-wide timeline — the closest thing to a "what's happening across all modules" view. Read at parent resume, never at module resume (modules read their own inbox, not the bus).

---

## §message-format — Message format

Messages are markdown blocks with a small YAML frontmatter. One message = one block. Messages are append-only — never edit a sent message in place.

```markdown
---
id: msg-20260411-1432-001
timestamp: 2026-04-11T14:32:10Z
from:
  module: auth
  persona: eng-lead
to:
  - "@payments"          # target another module
  - "@all"               # broadcast to every active module
  - "@parent"            # send up to the parent session
  - "@admin/pm-lead"     # target a specific persona inside a module
tags: [decision, scope, handoff]
thread: msg-20260410-0915-003   # optional — links this message to a prior one
priority: normal        # one of: urgent, normal, fyi
expires: 2026-04-18     # optional — auto-archive after this date
---

# Short title — one line

Body of the message in plain markdown. One to five paragraphs is ideal. If the message is longer than that, consider whether it should be a shared-asset update instead of a message.

## What changed (if applicable)

- Concrete change 1
- Concrete change 2

## What I need from you (if applicable)

- A question, a confirmation, a blocker-acknowledgement, etc.

## Refs

- `<module>/project-studio/decisions/ADR-012.md`
- `../.project-studio/shared/docs/api-contract.md#endpoints-auth`
```

### Field contracts

- **`id`** — deterministic format `msg-YYYYMMDD-HHMM-NNN` where `NNN` is a 3-digit counter within that minute. Prevents collisions when multiple messages are drafted back-to-back.
- **`from.module`** — the slug of the sending module. Always set. A parent session sets this to `parent`.
- **`from.persona`** — optional slug of the persona who originated the message (e.g., `eng-lead`, `pm-lead`). Defaults to `chief-of-staff` when omitted.
- **`to[]`** — a list of targets. At least one entry. Targets use `@`-syntax. Multiple targets are fine, but **broadcasts are rate-limited** (see chattiness modes).
- **`tags[]`** — from the tag vocabulary below. At least one tag. Tags drive routing priority and inbox summarisation.
- **`thread`** — optional. If this message continues a prior thread, paste the prior message id. Used to render conversations at review time.
- **`priority`** — one of `urgent`, `normal`, `fyi`. See priority behaviour below.
- **`expires`** — optional date. The sync command auto-archives expired messages at rotation time.

### Target vocabulary (`to[]`)

| Target | Meaning | Resolution |
|---|---|---|
| `@<module-slug>` | all personas in that module | delivered to `<module>/project-studio/inbox.md` |
| `@<module-slug>/<persona-slug>` | a specific persona in that module | delivered to the module's inbox with a `tag: for-persona-<slug>` |
| `@all` | every active module | fan-out to every active module's inbox |
| `@parent` | the parent session | delivered to `<parent>/.project-studio/inbox.md` |
| `@<persona-slug>` (no module) | a shared or parent persona | routed via the persona's `scope` to either parent inbox or every module that uses that shared persona |

Sibling folders are never read during target resolution. The sync command uses the parent manifest's module list to resolve targets, not directory walks.

### Tag vocabulary

Tags are a controlled vocabulary. New tags require a manifest-level decision (ADR) because routing and retention depend on them. Current tags:

| Tag | When to use | Default priority | Retention |
|---|---|---|---|
| `decision` | a locked-in decision that other modules should know about | normal | 90 days |
| `blocker` | the sender is blocked on something in another module | urgent | 90 days |
| `question` | a direct question to a sibling | normal | 30 days |
| `fyi` | informational, no action needed | fyi | 30 days |
| `handoff` | ownership of something is moving between modules | normal | 90 days |
| `milestone` | a milestone was completed | normal | 90 days |
| `scope` | scope change that affects cross-module roadmap | urgent | 90 days |
| `persona-promote` | a shared persona needs parent-level approval | normal | 90 days |
| `shared-update` | a parent shared asset changed (auto-generated by sync) | fyi | 14 days |

Messages can carry multiple tags. Retention uses the longest retention of any tag on the message.

### Priority behaviour

- **`urgent`** — surfaces at the top of the inbox summary on next module resume with a 🔴 marker. If the module is not opened within 7 days, the next sync broadcasts a `fyi: unread-urgent` to the parent inbox.
- **`normal`** — surfaces in the unread count at resume. Summarised by tag category.
- **`fyi`** — surfaces in the unread count but not in the quick summary. The user has to ask "show me FYI messages" to see them.

---

## §sync-command — The sync command  <!-- aliases: §sync -->

The sync command is the only thing allowed to touch files across the parent/module boundary in the direction of cross-module writes. It runs in a parent session or can be invoked from any module session as long as the parent is mounted.

### What sync does (in order)

1. **Lock.** Touch `<parent>/shared/.sync-lock` with an expiry of 30 seconds. If the lock already exists and is not expired, abort and ask the user to retry.
2. **Read module outboxes.** For every active module in the parent manifest, read `<parent>/shared/<module-slug>-outbox.md`. Parse message blocks.
3. **Resolve targets.** For each message, resolve `to[]` using the parent manifest's module list. Build a per-target delivery plan.
4. **Show plan.** Print a one-line-per-message delivery summary to the user:
   ```
   msg-20260411-1432-001  auth → payments, admin              [decision, scope]     normal
   msg-20260411-1433-001  payments → @all                     [blocker]             urgent
   msg-20260411-1435-001  admin → parent                      [persona-promote]    normal
   ```
5. **Ask to proceed.** Standard propose-then-yes gate. Options: `[a]` ll, `[s]` elective, `[c]` ancel.
6. **Deliver.** For each message with approved delivery:
   - Append the message block to every resolved target's inbox (`<target-module>/project-studio/inbox.md`).
   - Append the same block to `<parent>/shared/bus.md` with a `routed_at` timestamp prepended.
   - Append a one-line routing record to `<parent>/shared/bus-routing.log`.
7. **Mark sent.** Move delivered messages from the parent outbox into `<parent>/shared/<module-slug>-outbox-sent.md` so they are not re-routed on the next sync.
8. **Broadcast shared-update messages.** If any `<parent>/.project-studio/shared/*` file changed since the last sync (by timestamp check), auto-generate a `shared-update` message per changed file and fan-out to all active modules. See §parent-asset-change-notifications.
9. **Release lock.**
10. **Print summary.** Final one-line summary: *"Delivered 4 messages to 3 inboxes. 1 shared asset update broadcast."*

### When to run sync

There is **no automatic sync**. Sync runs only when the user asks. Recommended triggers:

- At the start of a parent session, after the parent resume protocol.
- At the end of a module session when the user is about to move to a different module.
- At the end of any session that produced approved outbox messages.
- After a parent-level shared asset edit.

Running sync too often wastes tokens and floods inboxes. Running it too rarely lets threads stall. The default chattiness mode (Standard, see below) recommends once per working session.

### Sync from within a module session

A module session can trigger sync, but only when:
1. The parent is mounted (otherwise there's nothing to read).
2. The user explicitly asks ("sync", "push updates", "run sync").
3. The sync will process outboxes for **every** active module, not just the current one. This is deliberate — partial syncs create drift.

If the user asks for sync inside a module session and the parent is not mounted, CoS replies with a fallback flow: flush local staging to the parent outbox at the correct path (a single write to `../shared/<module-slug>-outbox.md`), and tell the user to run sync from a parent session later.

---

## §auto-draft-gates — Auto-draft gates

CoS drafts outbox messages automatically at specific moments, but drafts always go to staging first and require user approval before flushing. These are the auto-draft gates:

| Gate | When it fires | Default tag | Default target |
|---|---|---|---|
| **Roadmap change** | a Tier 2 milestone is added, removed, or rescheduled AND the parent milestone it rolls up into has `feeds_from: [this-module]` | `scope` | `@parent`, `@all` (opt-in at draft time) |
| **Decision lock-in** | a new ADR is recorded AND the ADR has `cross_module: true` or tags `[shared-asset, api-contract, data-model]` | `decision` | `@parent` + any module named in the ADR's `affects[]` field |
| **Blocker log** | an entry is added to `registers/blockers.md` AND the entry's `blocked_by` field names a sibling module | `blocker` | the module named in `blocked_by` |
| **Milestone complete** | a Tier 2 milestone is marked done AND it's linked to a Tier 1 parent milestone | `milestone` | `@parent` |
| **Scope change** | a `registers/open-questions.md` entry is resolved with an answer that adds or removes scope for a cross-module boundary | `scope` | `@parent`, `@all` (opt-in at draft time) |
| **Shared persona modification** | a shared-scope persona is edited via persona-overrides.yaml | `persona-promote` | `@parent` |
| **Handoff** | the user explicitly says "hand off X to Y" or a milestone's ownership changes between modules | `handoff` | the receiving module |
| **Manual** | the user asks for an outbox message directly | user-picked | user-picked |

### The draft flow

1. A gate fires. CoS drafts a message following the message format above.
2. CoS appends the draft to `<module>/project-studio/outbox-staging.md` with a `status: draft` marker.
3. CoS shows the user a one-tap approval block:
   ```
   Outbox draft (staging only, not sent yet):

   To:    @parent, @payments
   Tags:  [decision, scope]
   Title: Auth tokens now expire after 30 days

   [body shown in full]

   [1] Send (flush to parent outbox, awaits next sync)
   [2] Edit
   [3] Broadcast (change target to @all)
   [4] Skip (discard the draft)
   [5] Keep in staging (don't send yet, keep for later review)
   ```
4. On `Send`, CoS appends the message block to `<parent>/shared/<module-slug>-outbox.md` and marks the staging entry as `status: flushed`.
5. On `Edit`, CoS opens a mini-edit flow that rewrites the message body before re-showing the approval block.
6. On `Broadcast`, CoS replaces the `to:` field with `@all` and re-shows the approval block.
7. On `Skip`, CoS deletes the draft from staging and records it in `log/` as `(skipped outbox draft: <reason>)`.
8. On `Keep`, CoS leaves the draft in staging. The next resume will re-surface it.

### Staging retention

`outbox-staging.md` is rotated at the end of each session. Flushed messages move to `outbox-staging-history.md`. Skipped messages are deleted. Kept drafts persist. This keeps staging readable and prevents old drafts from bleeding into new sessions.

---

## Chattiness modes

Users have three chattiness presets that control how eagerly CoS auto-drafts and broadcasts. The preset lives in `CLAUDE.md` under `communication_mode: <mode>`.

### Chatty

- Every gate fires.
- `@all` broadcasts are offered as the first suggestion for roadmap/scope changes.
- Auto-generated `shared-update` messages fan out to every module on any parent asset change.
- Draft approval blocks appear inline in every turn that triggers a gate.
- Recommended for: early-stage products, small teams where alignment matters more than noise, first-week-of-setup shakedowns.

### Standard (default)

- All gates fire except `Milestone complete` and `Shared persona modification`, which fire but default to `[5] Keep` so they batch up.
- `@all` broadcasts are opt-in (not the default target).
- Auto-generated `shared-update` messages fan out once per sync, not immediately.
- Draft approval blocks surface at session end or on explicit request.
- Recommended for: most projects. This is the default.

### Quiet

- Only `blocker`, `decision`, and `handoff` gates fire automatically.
- Everything else requires a manual "send an outbox message" request.
- Broadcasts are always opt-in and require two-step confirmation.
- Auto-generated `shared-update` messages do NOT fan out — users must explicitly ask for a shared-asset digest.
- Recommended for: stable mid/late stage products where noise is the enemy.

---

## §retention-and-rotation — Retention and rotation  <!-- aliases: §retention -->

Messages do not live forever. The bus, outboxes, and inboxes all rotate.

### Rotation schedule

- **Inboxes** — messages move to `inbox-archive.md` after the retention window (per-tag). At resume, CoS summarises what was archived since last resume and offers to delete the archive file older than 90 days.
- **Parent outbox (sent)** — messages in `<parent>/shared/<module-slug>-outbox-sent.md` rotate every 30 days. Older messages move to `<parent>/.project-studio/archive/outbox-<module>-<yyyy-mm>.md`.
- **Bus** — the `bus.md` file itself rotates every 30 days into `<parent>/.project-studio/archive/bus-<yyyy-mm>.md`. The live `bus.md` keeps the last 30 days plus a **summary block** at the top that links to archived slices.

### Summary blocks

Every rotation generates a summary block that lives at the top of the rotated-out file and at the top of the active bus. The summary block is approved by the user before being written — never auto-generated and silently inserted. Format:

```markdown
## Rotation summary — 2026-03-11 → 2026-04-11

**Period:** 31 days
**Messages routed:** 47 (auth: 18, payments: 19, admin: 10)
**Decisions locked:** 6
**Blockers resolved:** 4 (avg resolution 2.3 days)
**Milestones completed:** 3 (Tier 1: 1, Tier 2: 2)
**Scope changes:** 2
**Urgent unread at rotation:** 0

### Top threads this period

1. **Auth token expiry thread** (msg-20260315-1402-001) — 8 messages, resolved with ADR-014.
2. **Payment webhook contract** (msg-20260320-0930-001) — 6 messages, ongoing, owner: payments/eng-lead.
3. **Admin role matrix** (msg-20260402-1610-001) — 5 messages, resolved with ADR-017.

### Archive

Rotated-out messages live at `.project-studio/archive/bus-2026-03.md`.
```

### Read-sealed archive

All rotated-out files live under `<parent>/.project-studio/archive/` and are **read-sealed** per invariant 17 (archive is never read from). If the user needs to dig into an old thread, they open the archive file manually — CoS does not read it into context unprompted.

---

## Parent asset change notifications

When a parent session edits anything under `<parent>/.project-studio/shared/` (brief, roadmap, brand, docs, conventions, data), the sync command auto-generates a `shared-update` message per changed file and fans out to every active module's inbox (chatty/standard mode) or batches them into a digest (quiet mode).

### Generation rule

1. Sync reads `<parent>/.project-studio/shared/index-updated-at` (a one-line ISO timestamp).
2. If it's newer than the last recorded sync timestamp, sync walks the shared tree and diffs modification times against its cached index.
3. For each changed file, sync generates a message like:
   ```markdown
   ---
   id: msg-<ts>-shared-001
   timestamp: <ts>
   from:
     module: parent
     persona: chief-of-staff
   to:
     - "@all"
   tags: [fyi, shared-update]
   priority: fyi
   ---

   # Shared asset updated: brand/logo.svg

   The parent brand asset `brand/logo.svg` was updated at 2026-04-11T14:32:10Z.

   Your module's `project-studio/shared/shared-index.md` timestamp has been refreshed. No action required unless you were caching this file locally.

   ## Ref
   - `../.project-studio/shared/brand/logo.svg`
   ```
4. The message is delivered via the normal sync flow.

### No fan-out for log files

Sync does NOT generate shared-update messages for files under `<parent>/.project-studio/log/` or `<parent>/.project-studio/archive/`. Only user-facing shared assets trigger notifications.

---

## Failure modes and recovery

### Sync lock stuck

If `.sync-lock` is older than 30 seconds, any sync invocation will detect and offer to force-release. The user approves the release before the next sync proceeds.

### Message with unknown target

If `to[]` contains a module slug that is not in the parent manifest (e.g., a deleted module), sync puts the message into `<parent>/shared/undeliverable.md` with a `reason: unknown-target` note and asks the user what to do.

### Inbox file missing

If a module's `inbox.md` does not exist at delivery time (e.g., the module folder was deleted), sync creates it with a scaffolded header and delivers the message. It does NOT create a new module folder — only the inbox file inside an existing module folder. If the folder is gone, the message goes to undeliverable.

### Conflicting broadcasts in the same sync

If two modules both send `@all` messages about the same topic in the same sync run, both are delivered. The user sees them as separate threads in each inbox. There is no automatic de-duplication — threading is the user's job.

### Bus corruption

If the bus.md file becomes invalid markdown (e.g., a half-written rotation), CoS reads `bus-routing.log` as the authoritative record of what was delivered and rebuilds a clean bus.md from the log plus rotated archive files. This is a manual recovery step, not automatic.

---

## Reference: minimal outbox example

```markdown
# Auth module outbox

This file holds approved outgoing messages awaiting sync. The sync command reads from here, routes to siblings, and marks messages sent.

---

---
id: msg-20260411-1432-001
timestamp: 2026-04-11T14:32:10Z
from:
  module: auth
  persona: eng-lead
to:
  - "@payments"
  - "@parent"
tags: [decision, scope]
priority: normal
---

# Auth tokens now expire after 30 days

We landed ADR-014 this morning. Session tokens issued after 2026-04-12 will have a hard expiry of 30 days. Refresh tokens remain at 90 days.

## Why

User research from the last cohort showed 68% of users never log out on shared devices. 30-day expiry balances convenience against account-takeover risk.

## What changes for you

- **Payments:** any cached user session in the billing queue will hit a 401 after 30 days. Please add a background refresh hook.
- **Parent:** product brief needs a one-line update under "Security posture".

## Refs

- `auth/project-studio/decisions/ADR-014.md`
- `../.project-studio/shared/docs/security-posture.md`

---
```

---

## Reference: minimal bus.md example

```markdown
# Product bus

Chronological archive of routed cross-module messages. Read by parent sessions at resume, never by module sessions.

Rotation: every 30 days into `.project-studio/archive/bus-<yyyy-mm>.md`.

---

## Rotation summary — 2026-03-11 → 2026-04-11

(most recent summary block here, see §summary blocks for format)

---

## 2026-04-11

### 14:32 — auth → @payments, @parent  [dec