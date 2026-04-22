# Named Patterns

This file is the single source of truth for reusable patterns referenced across the skill. When SKILL.md or any reference says "see PATTERN:<name>", the canonical definition lives here. Edit once, apply everywhere.

Each pattern has: a one-line purpose, the canonical form, and usage notes. Do not duplicate these definitions elsewhere — reference them by name.

---

## PATTERN:role-tag-voice

**Purpose:** Attribute every persona utterance with a bracketed role tag instead of first-person character performance.

**Form:**

```
[<ROLE> — <mode>]
<content>
```

- `<ROLE>` is the persona's short role label in title case or uppercase (`PM`, `Engineer`, `Designer`, `CoS`, `Researcher`).
- `<mode>` is one of: `critique`, `proposal`, `flags`, `synthesis`, `decision matrix`, `learning`, `self-check`.
- `<content>` is dense, evidence-oriented, bullets or short prose. No roleplay, no "I think as a PM...", no character voice.

**Example:**

```
[PM — critique]
- Spec lacks success metrics. How do we know if this worked?
- Scope includes 4 features; I'd push to 2 for v1.

[Engineer — flags]
- DISSENT with PM: cut time not features.
```

**Use whenever** a persona speaks in the log, in a sub-agent return, or in a message presented to the user. Never omit the tag. Never switch to first-person in-character prose.

---

## PATTERN:role-tag-return

**Purpose:** Standard structured return format for every specialist sub-agent.

**Form:**

```
[<ROLE> — critique]
<2-6 bullets of critique scaled to stakes>

[<ROLE> — proposal]
<concrete proposal for this persona's domain, bulleted or short prose>

[<ROLE> — flags]
<dependencies / dissent / open questions — or "none">

[<ROLE> — self-check]
<one line: does this proposal satisfy the acceptance criterion? if no, why>

[<ROLE> — learning]
<one line: new fact, surprise, or assumption surfaced — or "none">
```

**Rules:**
- Total response under 400 words.
- Every section present (write "none" if empty).
- `self-check` references the acceptance criterion from PATTERN:acceptance-criterion.
- `learning` feeds `registers/learnings.md` when non-empty.
- No file edits — specialist appends only to its own `team/<persona>.md` Context notes.

**Use whenever** CoS spawns a specialist via the Agent tool (or Task tool in Claude Code CLI). This is the return contract.

---

## PATTERN:spawn-context-slice

**Purpose:** Minimal, deliberate context payload passed into a sub-agent spawn. Sub-agents start empty; be surgical.

**Form (sub-agent prompt skeleton):**

```
You are <persona name>, <role title>, working on "<project name>".

## Your persona
<paste ONLY these sections from team/<persona-name>.md:
 Role, Background, Principles, Obsession, Domain, Critique mode, Tone>
<DO NOT paste "Context notes" — that's append-log, not identity>

## Project slice
- Brief (1 sentence): <from CLAUDE.md>
- Current phase + milestone: <from roadmap>
- Roadmap items you own: <filtered to this persona>
- Relevant open questions/risks: <filtered to this persona's domain>

## Invokable skills (when the turn is code-heavy)
<list 1-3 skills the specialist must load in order before analyzing. For
 code-heavy spawns at standard/heavy scale on code-bearing modules, the
 first skill is `graphify` with a scoped path (module or cluster). Combo
 loadouts pair graphify with downstream analysis skills — see
 references/invokable-skills.md for the decision table. For design,
 research, and marketing spawns, list only domain skills. Skip this block
 entirely if the turn does not benefit from skill loading.>

## Acceptance criterion for this turn
<see PATTERN:acceptance-criterion — 1 testable sentence>

## Skills to load
<1-3 skills, specific to this task>
Use the Skill tool to load each before proceeding. If a skill fails to load (not found, error), note the failure and proceed with your base competence. Flag the missing skill in your return under [flags].

## User's prompt
"<verbatim>"

## Task
1. Critique (scaled to stakes).
2. Propose (concrete, domain-specific, no edits).
3. Flag (dependencies / dissent / open questions).
4. Self-check against the acceptance criterion.
5. Append a one-sentence note to team/<persona>.md under Context notes.

## Return format
See PATTERN:role-tag-return. Under 400 words.
```

**Rules:**
- Paste only identity-shaped persona sections, never the full file.
- Filter CLAUDE.md to the slice this persona actually needs.
- Always include the acceptance criterion.
- Cap skills at 1-3.
- Target under 1,500 words of injected context per specialist. If you need more, you're probably spawning too few specialists (split the domain) or including context the specialist doesn't need for this specific turn.
- Never paste full files. Extract the relevant section. The project-studio folder may be 100KB+ total — a specialist needs 2-5% of that per turn.
- Infrastructure files (`project/infrastructure/*.md`) are loaded ONLY when the prompt touches that service. Don't bulk-load all infrastructure for a UI question.
- For code-heavy spawns, prefer a scoped graphify invocation (via the specialist's skill loadout) over pasting source into the context slice. The specialist runs graphify against the scoped path on entry and returns a distilled slice — see `references/invokable-skills.md`. Only fall back to raw source excerpts when the question is narrower than a single file.

**Use whenever** spawning any specialist sub-agent.

---

## PATTERN:acceptance-criterion

**Purpose:** One testable sentence that defines "done" for this turn's proposal. Enables self-check, verifier, and quality gate.

**Form:**

```
Acceptance criterion: <single sentence, testable, output-shaped>
```

**Guidelines:**
- One sentence. If you need two, the turn is doing two things — split it.
- Testable means: a later reader could look at the output and say yes/no.
- Output-shaped means: it describes the artifact, not the activity.
- Written by CoS during routing (Step 2), before specialists spawn.

**Examples:**

```
Acceptance criterion: CLAUDE.md contains a roadmap section with 3-7 owner-tagged atomic tasks under the current milestone.

Acceptance criterion: The proposal names exactly one primary metric and one guardrail metric with numeric targets.

Acceptance criterion: The ADR captures the decision, 2+ options considered, and the reason the chosen option won — in under 200 words.
```

**Use whenever** CoS routes a turn that will result in a file edit or structural change. Skip for pure clarification turns.

---

## PATTERN:quality-gate

**Purpose:** Mandatory pre-execute check before any structural file edit. Catches sloppy edits, missed side effects, drift from acceptance criterion.

**Form:**

Run BEFORE executing Branch A ("yes") edits IF any of these are true:
- Edit touches CLAUDE.md sections beyond "Context notes" or log append.
- Edit deletes or renames a file.
- Edit modifies the roadmap (adds/removes/reshuffles tasks).
- Edit creates or removes a persona.
- Edit modifies connectors, identity locks, or invariants.

**Gate steps:**
1. Re-read the acceptance criterion from the turn's routing entry.
2. Spawn ONE verifier sub-agent (see workflow.md Post-Turn Checkpoint) with: target files, proposal, user's prompt, acceptance criterion.
3. Verifier returns: criterion-met (yes/no + why), side-effects (list), risks (list).
4. If criterion-met=no OR side-effects non-empty → present to user, wait for re-approval.
5. If clean → execute.

**Skip gate for:**
- Register appends (assumptions/risks/learnings/decisions).
- Persona Context notes appends.
- Log appends.
- Small copy edits under 10 lines within a single non-structural section.

**Use whenever** executing a structural edit. Non-optional for the triggers above.

---

## PATTERN:weekly-retro

**Purpose:** Recurring self-review using PDCA (Plan-Do-Check-Act) to catch drift, surface learnings, and adjust the roadmap.

**Form:**

Scheduled weekly for standard/heavy projects (skip for light). Run as a CoS-led turn with optional specialist input.

**PDCA cycle:**

1. **Plan (recap last week's plan)** — CoS reads: last 7 days of logs, roadmap delta, registers delta. Lists what was planned.
2. **Do (recap what actually happened)** — Lists completed tasks, abandoned tasks, unplanned work that appeared.
3. **Check (diff plan vs do)** — What slipped, what surprised, what accelerated. Pull learnings from `registers/learnings.md` added this week.
4. **Act (propose adjustments)** — Roadmap edits, new risks to register, assumptions to revisit, process changes.

**Return:** Populate PATTERN:retro-output-schema. Present to user. User approves adjustments via standard propose-then-yes gate.

**Use whenever** the scheduled retro fires, or when user asks for a weekly/sprint retro. Triggered by `mcp__scheduled-tasks` when configured at setup.

---

## PATTERN:retro-output-schema

**Purpose:** Canonical structure for retro output, so retros are comparable week-over-week.

**Form:**

```markdown
# Retro — <YYYY-MM-DD> (week ending)

## Plan (what we said we'd do)
- <item 1>
- <item 2>

## Do (what actually happened)
- Completed: <list>
- Abandoned: <list + 1-line why>
- Unplanned: <list>

## Check (diff + learnings)
- Slipped: <item — reason>
- Surprised: <item — what we didn't expect>
- Accelerated: <item — what went faster than planned>
- Learnings this week: <link to registers/learnings.md entries added>

## Act (adjustments proposed)
- Roadmap: <add / remove / reorder>
- Risks: <new risks to register>
- Assumptions: <to revisit>
- Process: <changes to how we work>

## Metrics (if tracked)
- <metric>: <value> (Δ from last week)

## Next week's plan
- <top 3-5 items>
```

**Rules:**
- Save to `retros/retro-<YYYY-MM-DD>.md`.
- Link from CLAUDE.md under a "Retros" section.
- Keep under 400 words total.

**Use whenever** PATTERN:weekly-retro runs.

---

## §memory-durability — PATTERN:memory-durability

**Purpose:** Survive context loss (compaction, session end, account switch) by making every durable decision, assumption, risk, and learning live on disk, not in transcript memory. This is the inheritance of the Memory Palace metaphor into project-studio's file-based state.

**Form:**

- **Registers** (`registers/assumptions.md`, `registers/risks.md`, `registers/open-questions.md`, `registers/learnings.md`) are append-only and exhaustive — anything worth remembering between sessions is written here, never "held in head."
- **Decisions** (`decisions/D-NNN-*.md`) are ADR-style records of choices with options, rationale, consequences. One file per significant decision.
- **Log** (`log/<YYYY-MM-DD>.md`) captures every turn's prompt, routing, returns, proposal, and status. The log is the primary recovery surface after compaction.
- **Checkpoints** (`checkpoints/<N>-<slug>.md`) snapshot CLAUDE.md + registers + roadmap at each milestone — the file-based analogue of a "save state."
- **Context snapshots** (`.cowork/context/<timestamp>.md`) preserve in-flight session understanding for the same or a future session to pick up, via `gstack-team:context-save` / `context-restore` (Invariant #28).

**Why this exists:** Transcripts are ephemeral. Context compaction, session limits, and cross-account resumes all drop any state not written to disk. A file-based durable layer is the substrate every other pattern (boot-read, reflexion-check, quality-gate) depends on — without it, none of them survive a single long session.

**Swap location:** Replacing this pattern means rewriting the register schemas (`references/registers.md`), log format (`references/workflow.md`), checkpoint contract (`references/setup-flow.md` §Step 7), and session snapshot behavior (`references/gstack-integration.md` §context-save). Invariants #5, #22, #25, #28 all rest on this layer.

---

## PATTERN:boot-read

**Purpose:** Force CoS to physically re-read the per-turn protocol from disk at the start of every user prompt, preventing workflow drift from context decay.

**Form:**

At the START of processing every user prompt (before logging, before routing, before anything):

1. Read `protocol/boot.md` from disk using the Read tool.
2. Follow the checklist in boot.md exactly.
3. End with the reflexion self-check before responding.

**Why this exists:** After 3-5 turns of specialist returns, log entries, and user discussion, the original skill ins