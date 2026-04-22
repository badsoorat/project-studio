# Session-Resume Protocol

Run this at every session start, after context compaction, or after switching Claude accounts. This runs BEFORE the boot protocol takes over for regular turns.

## The Resume Sequence

When user opens Cowork on an existing project and mentions project-studio (or root CLAUDE.md exists with project-studio markers), CoS does this before anything else:

### 1. Read root CLAUDE.md
Read the thin index at the project root. It tells you where everything lives inside `project-studio/`.

### 2. Parent security check (multi-module projects only)

**Skip this step entirely if:** The project is standalone (no parent architecture). Check root CLAUDE.md for a "Parent" section — if absent, skip to step 3.

**If parent architecture exists:**

**Step 2a: Read parent manifest.**
Read `../CLAUDE.md` (the parent-level manifest). Identify sibling modules and their status.

**Step 2b: Check inbox for unread messages.**
Read `project-studio/inbox.md`. Check the `## Unread` section for any messages delivered since the last session.

- **If inbox has NO unread messages →** Stop reading parent. Skip to step 3. Zero additional parent reads. This is the common case — optimize for it.
- **If unread messages exist →** Proceed to Step 2c.

**Step 2c: Present inbox messages.**
Surface unread messages grouped by sender:

```
You have N unread messages:
  • auth     → decision: "switched password hashing to argon2" (2h ago)
  • payments → question: "should we unify the billing webhook?"   (yesterday)
  • parent   → milestone: "Tier 1 milestone 'Auth done' is 80%"   (3d ago)

Want me to summarise, open one, or mark all read?
```

Don't block resume on these — they're informational. The user decides what to do.

- **If user wants to act on a message →** Process it, then continue to step 3.
- **If user says skip/mark read →** Move messages from `## Unread` to `## Read` in inbox.md. Continue to step 3.

**Step 2d: Flush any pending outbox drafts (optional).**
Check `project-studio/outbox-staging.md` for drafted messages that were never flushed. If any exist, ask: *"You have N unsent draft messages in outbox staging. Want me to flush them to the parent outbox now, or keep them as drafts?"*

- **If user says flush →** Write each message to `../shared/<this-module-slug>-outbox.md` and clear the staging file. Note: a full sync (routing from outboxes to inboxes across all modules) requires running `sync` from a parent session — see `references/module-communication.md`.
- **If user says keep →** Leave drafts in staging. Note in log.

**Step 2e: Stop reading parent.**
All parent access is done. CoS works entirely inside the module folder for the rest of the session.

### 3. Read boot protocol
Read `project-studio/protocol/boot.md` to reload the per-turn workflow into context.

### 4. Read today's log
Read `project-studio/log/<YYYY-MM-DD>.md`. If it doesn't exist, read the most recent log file in `project-studio/log/`.

### 5. Scan last turn's status
Check the log tail for the last turn's `Status:` marker. This determines recovery path.

### 6. Read latest checkpoint
Read the most recent file in `project-studio/checkpoints/` for milestone context.

### 7. Read project brief + roadmap
Read `project-studio/project/brief.md` and `project-studio/project/roadmap.md` to reload project state.

### 8. Read open registers
Skim `project-studio/registers/assumptions.md`, `project-studio/registers/risks.md`, `project-studio/registers/open-questions.md` for active items.

### 9. Check TodoList
Read active TodoList items.

### 10. Reconcile connector identities
For each connector in root CLAUDE.md's "Connectors installed" section, verify identity matches. See `project-studio/references/connectors.md` for the per-MCP probe table. Do NOT call any connector tool before reconciliation (invariant #10).

### 11. Summarize to user

```markdown
## Resuming: <project name>

**Scale:** <light/standard/heavy>
**Phase:** <current phase from roadmap>
**Active milestone:** <current milestone + owner>

**Team:** <names comma separated>

**Last activity:**
- Last turn: #<N> on <date/time>
- Last turn status: <complete | pending-approval | in-progress | abandoned>
- Last 3 turns: <one-line summary each>

**Inbox:** <N unread messages from siblings | no unread messages | standalone project>

**Open registers:**
- <K> active assumptions, <K> active risks, <K> open questions

**Pending:** <recovery action if needed, or "None — ready for next prompt">

How do you want to proceed?
```

### 12. Wait for user instruction
Do NOT take any action until user confirms. Then switch to the per-turn boot protocol for all subsequent prompts.

## Recovery by Last-Turn Status

### Status: complete
Last turn finished cleanly. Project is idle. Prompt user for next action.

### Status: pending-approval
A proposal was waiting for "yes". Present the saved proposal from the log. Offer: yes / discuss / abandon.

### Status: specialists-working
Specialists were spawned but hadn't all returned. Offer: resume (respawn missing with reflexion context from returned specialists) / restart (re-route from scratch) / abandon.

### Status: routing
Routing was happening when session died. Offer: restart or abandon.

### Status: executing
Edits were being applied. Inspect each listed file against the log's "Edits applied" list. Report which edits completed and which didn't. Ask user how to proceed.

### No status (malformed log)
Read previous day's log or latest checkpoint. Summarize what's known. Ask user to confirm before doing anything.

## Cross-Account Resume

User mounts the same workspace folder in a different Claude account and says "resume". The standard resume sequence above handles this — all state is in files, not transcripts. Do NOT try to access the other account's session history.

## Setup-Interrupted Recovery

If context compacts or a session ends **during setup** (before the project is fully built), the standard resume sequence above won't work because CLAUDE.md may not exist or may be incomplete. Detect this case and recover:

**Detection:** Root CLAUDE.md either (a) doesn't exist, (b) exists but lacks `project-studio` markers, or (c) the `project-studio/` directory exists but is missing key files (`protocol/boot.md`, `team/chief-of-staff.md`, `project/brief.md`).

**Recovery steps:**

1. Read today's log at `project-studio/log/<YYYY-MM-DD>.md` if it exists. If no log exists, check for any files in `project-studio/` to determine how far setup progressed.
2. Determine last completed setup step from log entries or file presence:
   - **Only `project-studio/` dir exists (empty or just protocol/):** Setup interrupted at Step 7a scaffolding. Restart from Step 7.
   - **Team files exist but no `project/brief.md`:** Setup interrupted after team setup (Step 3) but before roadmap was written. Resume from Step 4.
   - **Brief + roadmap exist but no `CLAUDE.md`:** Setup nearly complete. Resume from Step 7b/7c (write remaining files + CLAUDE.md).
   - **`CLAUDE.md` exists but missing sections:** Setup interrupted during final file writes. Diff against `templates/CLAUDE.md.tmpl` to identify missing sections and fill them.
3. Summarize to user: *"Setup was interrupted. I found [what exists]. Resuming from Step [N]."*
4. Wait for user confirmation before continuing setup.

**Key rule:** Never restart setup from scratch if partial state exists on disk — that would discard user decisions already made (team selection, roadmap, connectors).

## After Context Compaction (Same Session)

When context compacts mid-session:
1. Immediately run this resume protocol.
2. Explain: "My context compacted. I've re-read project state from disk. We were on <summary>. Continuing."
3. **Skip the parent security check** (Step 2) on compaction resume — parent was already checked at session start. Work stays local.

## After Long Absence (Days/Weeks)

1. Read last 7 days of logs (not just today's).
2. Read most recent checkpoint in full.
3. Scan retro logs for retros that happened while away.
4. **Run the parent security check** (Step 2) — sibling updates are likely after a long absence.
5. Summarize: "You were away <N> days. Here's what happened: <summary>."
6. Ask user what they want to do.

## Resume Invariants

1. Never act before summarizing and getting user confirmation.
2. Never skip reading root CLAUDE.md + `project-studio/protocol/boot.md`. They are the source of truth.
3. Never assume memory. If it's not in a file inside `project-studio/`, it doesn't exist. Reconstruct state from the log, checkpoints, and registers — never from what you think you remember about the last turn.
4. Never read `project-studio/archive/` or any `CLAUDE_old.md`. Those files are sealed (Invariant #9).
5. Never silently upgrade import scope, bypass the parent security check on a multi-module project (Step 2 must execute; early exit at Step 2b after confirming an empty inbox is not bypass), or call a connector tool before identity reconciliation (Invariant #10).
6. If any required state file is missing or corrupted, warn the user and wait — do not hallucinate contents to keep the session moving.