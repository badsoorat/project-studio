# Per-Turn Workflow (Detailed)

This is the full detail of the per-turn workflow. The SKILL.md summary lists step names; this file is the operational reference.

Named patterns referenced here (canonical definitions in `references/patterns.md`):
- `PATTERN:role-tag-voice`
- `PATTERN:role-tag-return`
- `PATTERN:spawn-context-slice`
- `PATTERN:acceptance-criterion`
- `PATTERN:quality-gate`
- `PATTERN:plan-critique-sequence`
- `PATTERN:pre-write-checklist`

## The 9 steps

Step 0 is the one-time-per-session context restore. Steps 1–8 run every turn. Step 9 runs at session wind-down.

### Step 0 — Context restore (first turn of session only)

On the first turn of a session, before anything else, CoS runs `gstack-team:context-restore` if the project has any saved snapshots under `.cowork/context/`. The restore loads the most recent snapshot so the session starts with full durable state (open threads, current decisions, last-session context). On subsequent turns in the same session, skip this step.

If gstack-team is not installed, CoS falls back to reading the resume protocol at `protocol/resume.md` (pre-v3.1 behavior). Record the fallback in the session's log.

### Step 1 — Boot (re-read protocol)

**At the start of every turn**, use `PATTERN:boot-read`: physically read `protocol/boot.md` from disk (the per-turn checklist). This re-anchors CoS to the project's immutable rules, current roadmap, team state, and connectors. Boot is where the project resets itself against drift. Do not skip this.

### Step 2 — Log prompt (write-ahead)

**Before doing anything else**, append the user's prompt to today's log file at `log/<YYYY-MM-DD>.md`. Format:

```markdown
## Turn <N> — <YYYY-MM-DD HH:MM:SS>

### Prompt
<user's exact prompt>

### Status: routing
```

This is write-ahead state. If the session dies here, the next Claude can see the prompt was received and routing hadn't happened yet.

### Step 3 — Route

CoS reads:
- Last 3 entries in today's log
- `project/brief.md` (project brief, goals)
- `project/roadmap.md` (current roadmap)
- Team roster from `team/` folder
- Open TodoList items
- Any relevant `project/` subdirectory files hinted at by the prompt (research/, design/, etc.)

Then decides on specialist roster. **There is no 'direct answer' path for domain questions. CoS orchestrates, it does not answer solo on domain substance.** Category 3 (process/meta lookups) are the only exception — see `protocol/boot.md` §the-three-categories-rule.

Routing options:
- **1 specialist** — task falls cleanly in one domain. Common.
- **2 specialists** — task spans two domains, or benefits from a second opinion.
- **3 specialists** — genuinely multi-domain or high-stakes decisions.
- **More than 3** — rare. Major architectural decisions only.

**Plan-critique gating.** If this turn is about to produce or execute an implementation plan — roadmap-level feature plan, architecture decision, design-system change, or anything that will trigger the quality gate on ≥3 structural triggers — CoS MUST route through Tier-1 plan-critique (Invariant #20) before any write. The four lenses are `gstack-team:plan-ceo-review`, `plan-eng-review`, `plan-design-review`, `plan-devex-review`. See `PATTERN:plan-critique-sequence` and `references/gstack-integration.md` §plan-critique.

**Write an acceptance criterion** for this turn using `PATTERN:acceptance-criterion`. One sentence, testable, output-shaped.

Append routing decision to log:

```markdown
### Routing
Specialists: [<role-1>, <role-2>]
Skills to load:
  - <role-1>: [<skill-1>, <skill-2>]
  - <role-2>: [<skill-3>]
Plan-critique gate: <none | condensed | full Tier-1>
Acceptance criterion: <single testable sentence — PATTERN:acceptance-criterion>
Reasoning: <one line>

### Status: specialists-working
```

### Step 4 — Spawn specialists in parallel

Spawn each specialist as a sub-agent via the **Agent tool** (general-purpose subagent type). In Claude Code CLI, use the Task tool instead — both invoke the same sub-agent mechanism. Send all spawns in a single message to run in parallel.

**Use `PATTERN:spawn-context-slice` to construct each sub-agent prompt.** The pattern defines:
- Which persona sections to paste (identity only — never the Context notes append-log)
- Which roadmap/brief slice to pass (filtered to this persona's domain)
- How the acceptance criterion flows in
- How skills are listed (1-3 max)
- The task structure (critique → propose → flag → self-check → append one-line context note)
- The return format (`PATTERN:role-tag-return`)

**Code-heavy spawns** (engineering, platform, data, infra, devops, browser-QA, release-readiness, security-audit) at standard or heavy scale MUST enumerate `graphify` plus the relevant `gstack-team:*` downstream skill in the prompt's skill list. Example pairings:
- Architecture coherence review → `graphify` + `clean-architecture` + `gstack-team:review`
- Security audit → `graphify` + `gstack-team:cso`
- Root-cause investigation → `graphify` + `gstack-team:investigate`
- Live-URL QA → `gstack-team:qa` (+ `gstack-team:browse`)
- Visual design audit → `gstack-team:design-review` (+ `gstack-team:browse`)

See `references/invokable-skills.md` for the full combo table and `PATTERN:spawn-context-slice` for the prompt shape.

**Spawn in parallel**, not sequentially. All sub-agents launch in the same message. Plan-critique's four lenses may parallelize lenses 3–4 (design, devex) after lenses 1–2 (ceo, eng) have cleared the strategic/architectural foundation — see `PATTERN:plan-critique-sequence`.

**Handling sub-agent failures:** If a specialist sub-agent fails to return, returns an error, or returns malformed output:
1. Log the failure: `[CoS — warning] <Role> sub-agent failed: <reason>`.
2. Drop that specialist from this turn's consolidation.
3. Proceed with the remaining specialist returns.
4. In the presentation to the user, note the gap: *"[Role] was unavailable this turn — proceeding with [N-1] specialist(s). Want me to retry?"*
5. If ALL specialists fail, inform the user and offer to re-route or continue discussion without specialist input for this turn only.

### Step 5 — Consolidate

When all specialists return (or after handling failures above):

- Read each specialist's `PATTERN:role-tag-return` block (critique / proposal / flags / self-check / learning).
- Identify consensus, dissent, and open questions.
- **Preserve dissent** — do not force the specialists into agreement.
- Route each non-empty `learning` field to `registers/learnings.md`.
- Write the consolidated block to the log:

```markdown
### Specialist returns
<paste each specialist's full return verbatim>

### Consolidated proposal
[CoS — synthesis]
Consensus: <what they agree on>
Dissent: <who disagrees on what>
Key questions: <unresolved>
Acceptance criterion recap: <from routing>
Self-check summary: <which specialists said their proposal meets the criterion>
Recommended action: <CoS's recommendation, or "user decides">

### Status: pending-approval
```

### Step 6 — Present to user

Show the user:
- Each specialist's critique (role-tag format — `PATTERN:role-tag-voice`)
- Each specialist's proposal
- Surfaced dissent
- The acceptance criterion (so user can veto or refine it)
- CoS synthesis
- The specific file changes proposed (if any), listed
- **Export format** — if the proposal will produce a user-facing deliverable (brief, roadmap, retro report, manifest, one-pager, proposal, plan, design spec), announce "Export format: PDF via `gstack-team:make-pdf`" per Invariant #24, so the user can override to markdown-only before execution.

End with an explicit ask: *"Approve? (yes / no / discuss)"* or similar.

**Role-tag format example:**

```
[PM — critique]
- Spec lacks success metrics. How do we know if this worked?
- Scope includes 4 features; I'd push to 2 for v1.
- User research gap: who specifically is this for?

[PM — proposal]
- Cut scope to feature A + feature B
- Add metric: "40% of signups complete onboarding in <5 min"
- Book 5 user interviews before building

[PM — self-check]
- Meets criterion (proposes scope + metric as required).

[Engineer — critique]
- Architecture is fine for v1, but cache layer will be bottleneck by week 4
- "Real-time sync" is handwaved — is it SSE, WebSocket, polling?

[Engineer — proposal]
- Build with Postgres + SSE for v1
- Add cache plan to week-4 milestone

[Engineer — flags]
- DISSENT with PM: cut time not features.

[Engineer — self-check]
- Partial — criterion asked for v1 scope; I deferred cache to week-4 which implies a v2.

[CoS — synthesis]
PM and Engineer disagree on scope vs timeline tradeoff. Both are reasonable.
Export format: PDF via gstack-team:make-pdf for the final plan — override if you want markdown only.
User: which do you value more — shipping fewer features faster, or all four later?
```

### Step 7 — Reflexion check

**Before waiting for user approval**, CoS runs `PATTERN:reflexion-check` — a self-audit using the protocol rules from `boot.md`. The canonical set of lines is defined in `protocol/boot.md` §reflexion-self-check and in `references/patterns.md` §PATTERN:reflexion-check. Summary:

- Logged the prompt
- Routed to at least one specialist (or handled as Category 3 lookup)
- Spawned via Agent/Task (not simulated)
- Consolidated with dissent preserved
- Presenting for user approval (not auto-executing)
- Plan-critique lenses named if this is an implementation-plan turn
- Graphify + gstack-team:* downstream named if this is a code-heavy spawn
- Export format announced if deliverable is user-facing
- Pre-write checklist ran if any structural edit is proposed

If any check fails, CoS surfaces the failure to the user before presenting the proposal. Example: *"I routed to 1 specialist but didn't consolidate yet — holding pending their return."*

### Step 8 — Wait for user decision

Three branches:

**Branch A: "yes" (or clear go-ahead like "do it", "proceed", "approved")**

1. **Pre-write checklist** (`PATTERN:pre-write-checklist`) — before any file write, CoS verifies:
   - **Scope check.** Do proposed paths fall inside the module's declared scope? If not, present the out-of-scope paths in a single decision card (proceed / scope-down / escalate). See `references/scope-policy.md`.
   - **Freeze check.** Read `.cowork/freeze.json` (and the parent-level equivalent if this is a module session). If any proposed path matches a frozen path or glob, halt and surface via `gstack-team:guard`. See Invariant #26 and `references/gstack-integration.md` §freeze-scope.
   - **Parent-write check.** If this is a module session and a proposed path resolves outside the module folder (e.g., `../shared/bus.md`, `../.project-studio/shared/brief.md`), require explicit user permission per Invariant #16.
2. **Quality gate** — evaluate `PATTERN:quality-gate` triggers. If any trigger fires (structural edit, roadmap reshuffle, file delete/rename, persona change, connector/identity/invariant change), run the gate before any write. If gate flags issues, present to user, wait for re-approval. If clean, continue.
3. Execute the proposed file edits using Edit/Write tools. For files in the shared parent directory (`shared/bus.md`, `shared/<module>-outbox.md`) use the atomic-write pattern (`mktemp → write → mv`). See `references/monorepo-pattern.md` §atomic-writes.
4. Update the atomic roadmap in `project/roadmap.md` if this turn completed or modified a task.
5. Update TodoList to reflect roadmap changes.
6. **Export user-facing deliverables.** If the proposal produced a brief, roadmap, retro, manifest, one-pager, plan, or design spec, invoke `gstack-team:make-pdf` to render the authoritative PDF to `project-studio/exports/<YYYY-MM-DD>-<slug>.pdf`. The markdown source stays under `project-studio/` in its canonical location; the PDF is the user-facing artifact. Skip only if user requested markdown-only at Step 6.
7. **Post-execute self-check** — CoS diffs the applied edits against the acceptance criterion. One sentence: does the artifact satisfy the criterion? If no → flag to user, offer to revert or continue. If yes → proceed.
8. Append to log:

```markdown
### User response: yes
### Status: executing
### Pre-write checklist:
- Scope: in-scope / out-of-scope (decision card presented and approved)
- Freeze: no match / match at <path> (override via decision card)
- Parent write: n/a / requested and approved
### Edits applied:
- <file 1>: <what changed>
- <file 2>: <what changed>
### Exports:
- <file>.pdf via gstack-team:make-pdf
### Post-execute self-check:
Criterion: <recap>
Met: <yes/no + one-line reason>
### Status: complete
```

9. If a milestone was completed, take a checkpoint (see "Milestone checkpoints" below) and run a milestone retro (see §retros below).
10. Respond to user with a short summary of what was done + self-check verdict + a link/path to the PDF deliverable if one was produced.

**Branch B: "no" or objections**

1. Append user's objection to log under `### User response: discuss`.
2. Keep `Status: pending-approval`.
3. Update the proposal based on the objection. If substantive feedback requires specialist re-engagement (new research, significant scope change, new dissent), spawn specialists again rather than revising solo.
4. Re-present. Loop.

**Branch C: ambiguous response**

If the user's reply is unclear, ask: *"Should I proceed with the proposal as stated, or do you want to adjust it?"* Do not edit files on ambiguous signals.

### Step 9 — Context save (session wind-down)

At the end of a working session — before the user closes the session or after a natural stopping point (milestone complete, shift end, "let's pick this up tomorrow") — CoS proposes invoking `gstack-team:context-save` to snapshot durable session state (open threads, current decisions, active dissent, pending user decisions) to `.cowork/context/<YYYY-MM-DD-HHMM>.md`. The snapshot is the input to Step 0 on the next session.

The save is not automatic on every turn; it's proposed at wind-down or on explicit user request (*"save context"*). See `PATTERN:wind-down-detect` in `references/patterns.md` for heuristics.

### Quality Gate *(runs inside Step 8 Branch A when triggered)*

See `PATTERN:quality-gate` in `references/patterns.md` for the full spec. Summary:

**Mandatory triggers** (gate must run):
- Edit touches CLAUDE.md beyond log/Context notes appends
- File delete or rename
- Roadmap add/remove/reshuffle
- Persona create/delete
- Connectors / identity locks / invariants modified

**Gate procedure:**
1. Re-read the acceptance criterion from the turn's routing entry.
2. Spawn ONE verifier sub-agent with: target files, proposal, user's prompt, acceptance criterion.
3. Verifier returns: criterion-met (yes/no + why), side-effects (list), risks (list).
4. Branch:
   - criterion-met=no OR side-effects non-empty → present to user, wait for re-approval.
   - clean → execute.

**Verifier sub-agent prompt:**

```
You are a verifier. Read the following and report:
1. Does the proposal satisfy the acceptance criterion? (yes/no + why)
2. Are there side effects the proposal misses? (list, or "none")
3. Risks? (list, or "none")

Acceptance criterion: <paste>
User's original prompt: <paste>
Target files: <paths>
Proposal: <paste>
```

**Skip gate for** (explicit exceptions):
- Register appends (assumptions/risks/learnings/decisions)
- Persona Context notes appends
- Log appends
- Small copy edits under 10 lines within a single non-